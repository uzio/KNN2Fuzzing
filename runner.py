# coding:utf-8
from pymongo import MongoClient
from bson import ObjectId
from workstation.constants import (
    JobStatus,
    JobType
)
from ics_logger import ICSLogger
from utils import config
import time
import sys

logger = ICSLogger.get_logger()

mongo = MongoClient()
fuzz = mongo.fuzz
jobs = fuzz.jobs
status = fuzz.status


def enqueue():
    pass


def dequeue():
    job = jobs.find_one({'status': JobStatus.TO_FUZZ}) #获取一个jobs集合中状态码=2，即将要执行模糊测试的任务
    return job


def main():
    print('Runner started')
    while True:
        job = dequeue()

        if job is None or 'params' not in job:
            time.sleep(1)
            continue
        if job['type'] != JobType.FUZZ: # 如果不是模糊测试的任务，跳过本次循环
            time.sleep(1)
            continue

        print(job) # 打印将要测试的任务
        jobs.update_one({'_id': ObjectId(job['_id'])}, {'$set': {'status': JobStatus.FUZZING}}) # 将对应任务的状态码更新为3，即正在进行模糊测试

        logger.info(u'获取用例: {}'.format(job['title']))# 打印任务的目标信息
        cases = job['case'] # 获取对应用例的序号
        job['status'] = JobStatus.FUZZ_COMPLETE # 将任务标记为已完成
        for case in cases:
            try:
                runner = CaseRunner(case, job)# 将用例序号和任务提交至运行方法
                runner.run()
            except KeyError:
                job['error_msg'] = 'fuzz params error'
                logger.error('模糊测试参数错误', exc_info=1)
            except Exception as e:
                job['error_msg'] = str(e)
                job['status'] = JobStatus.ERROR # 任务执行发生错误
                logger.exception(u'执行用例:{}-错误'.format(case['title']))
        print(job)
        jobs.update_one({'_id': ObjectId(job['_id'])}, {'$set': job}) # 更新任务至数据库
        # if job['status'] == JobStatus.ERROR or job['status'] == JobStatus.VULN:
        #     jobs.update_one({'_id': ObjectId(job['_id'])}, {'$set': job})
        # else:
        #     jobs.update_one({'_id': ObjectId(job['_id'])}, {'$set': {'status': JobStatus.FUZZ_COMPLETE}})


class CaseRunner(object):
    def __init__(self, _case, _job):
        self.case = _case
        self.job = _job

    def run(self):
        """
        运行测试用例
        """
        params = self.job['params']
        case_specify = fuzz.cases.find_one({'_id': ObjectId(self.case['_id'])})  # 查找到完整的测试用例信息
        sys.path.append(case_specify['proto_path'])
        module = __import__(case_specify['module_name'])
        jobs.update_one({'_id': ObjectId(self.job['_id'])},
                        {'$set': {'start_time': time.time(), 'current': self.case['title']}})
        params['CASE_ID'] = self.case['_id']

        params['INTERFACE'] = config['monitor_iface']  # Todo
        params['JOB'] = self.job
        if self.case['title'] == u'Data write时，模糊Parameter中Item中的TransportSize ':
            params['INTERFACE'] = 'lo'  # Todo
        module.fuzz(params)
        sys.path.remove(case_specify['proto_path'])
        jobs.update_one({'_id': ObjectId(self.job['_id'])}, {'$inc': {'completed': 1}})
        del params['JOB']


if __name__ == '__main__':
    main()
