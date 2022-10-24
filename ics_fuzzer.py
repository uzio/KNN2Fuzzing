# coding:utf-8
from kitty.core import KittyException
from kitty.fuzzers import BaseFuzzer
from threading import Thread, Event
from Queue import Queue
from pymongo import MongoClient
from ics_logger import ICSLogger
from base64 import b64decode, b64encode
from kitty.data.report import Report
from kitty.data.data_manager import synced
from kitty.fuzzers.test_list import RangesList, StartEndList
from katnip.monitors.network import NetworkMonitor
from utils import config
from workstation.constants import JobStatus

import time
import cPickle
import zlib
import traceback
import os


class DataManagerTask:
    def __init__(self, task, *args):
        self.event = Event()
        self.result = None
        self.task = task
        self.args = args
        self.exception = None

    def execute(self, data_manager):
        self.event.clear()
        try:
            self.result = self.task(data_manager, *self.args)
        except Exception as e:
            self.exception = e
            ICSLogger.get_logger().error(traceback.format_exc())
        self.event.set()

    def get_results(self):
        self.event.wait()
        if self.exception is not None:
            raise self.exception #pylint:disable=E0702  
        return self.result
    #Pylint 已知bug：Pylint doesn't do a lot of flow-control inferencing.

class MongoDataManager(Thread):
    """
    Todo 这里把当前job的ID放进入
    """
    def __init__(self, dbname, params):
        super(MongoDataManager, self).__init__()
        self.dbname = dbname
        self.params = params
        self.db = None
        self.connection = None
        self.reports = None
        self.session_info = None
        self.volatile_data = {}
        self.stopped_event = Event()
        self.queue = Queue()

    def open(self):
        self.db = MongoClient()
        self.connection = self.db.fuzz
        self.session_info = SessionInfoMongo(self.connection)  # 初始化两个储存信息到mongodb的类
        self.reports = ReportsMongo(self.connection, self.params)

    def run(self):
        self.stopped_event.clear()
        self.open()
        while True:
            task = self.queue.get()
            if task is None:
                break
            task.execute(self)
        self.close()
        self.stopped_event.set()

    def submit_task(self, task):
        self.queue.put(task)
        return task

    def close(self):
        self.db.close()

    def stop(self):
        self.submit_task(None)
        self.stopped_event.wait()

    @synced
    def get_session_info_manager(self):
        return self.session_info

    @synced
    def get_session_info(self):
        return self.session_info.get_session_info()

    @synced
    def set_session_info(self, info):
        self.session_info.set_session_info(info)

    @synced
    def get_reports_manager(self):
        return self.reports

    @synced
    def get_report_test_ids(self):
        return self.reports.get_report_test_ids()

    @synced
    def get_report_list(self):
        return self.reports.get_report_list()

    @synced
    def get_report_by_id(self, report_id):
        return self.reports.get(report_id)

    @synced
    def store_report(self, report, test_id):
        self.reports.store(report, test_id)

    @synced
    def set(self, key, data):
        if isinstance(data, dict):
            self.volatile_data[key] = {k: v for (k, v) in data.items()}
        else:
            self.volatile_data[key] = data
        self.session_info.save_volatile(self.volatile_data)  # 将数据写入Mongodb中

    @synced
    def get(self, key):
        return self.volatile_data.get(key, None)


class SessionInfoMongo:
    """
    从mongodb中取出信息
    """
    __COLLECTION_NAME__ = 'sessionInfo'
    __FIELDS__ = [
        'start_time',
        'start_index',
        'end_index',
        'current_index',
        'failure_count',
        'kitty_version',
        'data_model_hash',
        'test_list_str',
    ]

    def __init__(self, connection):
        self.connection = connection
        self.info = self.read_info()

    def read_info(self):
        info = self.connection[self.__COLLECTION_NAME__].find_one()
        if info is None:
            return None
        return SessionInfo.from_dict(info)

    def set_session_info(self, info):
        collection = self.connection[self.__COLLECTION_NAME__]
        if not self.info:
            self.info = SessionInfo()
            info_d = self.info.as_dict()
            collection.insert_one(info_d)
        changed = self.info.copy(info)
        if changed:
            collection.replace_one({}, self.info.as_dict())

    def get_session_info(self):
        return SessionInfo(self.info)

    def save_volatile(self, volatile):
        """
        kitty里有些信息也保存到mongo里
        :param volatile:
        :return:
        """
        info = self.info.as_dict()
        info['volatile'] = volatile
        collection = self.connection[self.__COLLECTION_NAME__]
        collection.replace_one({}, info)


class SessionInfo(object):
    """
    保存模糊会话信息
    """
    fields = [i for i in SessionInfoMongo.__FIELDS__]

    def __init__(self, orig=None):
        '''
        :param orig: SessionInfo object to copy (default: None)
        '''
        self.start_time = 0
        self.start_index = 0
        self.current_index = 0
        self.end_index = None
        self.failure_count = 0
        self.kitty_version = ''
        self.data_model_hash = 0
        self.test_list_str = ''
        if orig:
            self.copy(orig)

    def copy(self, orig):
        '''
        :param orig: SessionInfo object to copy
        :return: True if changed, false otherwise
        '''
        changed = False
        for attr in SessionInfo.fields:
            oattr = getattr(orig, attr)
            if getattr(self, attr) != oattr:
                setattr(self, attr, oattr)
                changed = True
        return changed

    def as_dict(self):
        '''
        :return: dictionary with the object fields
        '''
        return {fname: getattr(self, fname) for fname in SessionInfo.fields}

    @classmethod
    def from_dict(cls, info_d):
        '''
        :param info_d: the info dictionary
        :rtype: :class:`~kitty.data.data_manager.SessionInfo`
        :return: object that corresponds to the info dictionary
        '''
        info = SessionInfo()
        for k, v in info_d.items():
            setattr(info, k, v)
        return info


class ReportsMongo:
    __COLLECTION_NAME__ = 'reports'
    __FIELDS__ = [
        'id',
        'test_id',
        'content',
        'status',
        'reason',
    ]

    def __init__(self, connection, params):
        self.connection = connection
        self.params = params

    def store(self, report, test_id):
        report_d = report.to_dict()
        # content = self.serialize_dict(report_d)
        self.connection[self.__COLLECTION_NAME__].insert({
            'test_id': test_id,
            'content': report_d,
            'job_id': self.params['JOB_ID'],
            'case_id': self.params['CASE_ID']
        })

    def get(self, test_id):
        report = self.connection[self.__COLLECTION_NAME__].find_one({'test_id': test_id})
        if report is None:
            raise KeyError('No report with test id %s in the MongoDB' % test_id)
        # content = self.deserialize_dict(report['content'])
        return Report.from_dict(report['content'])

    def get_report_test_ids(self):
        collection = self.connection[self.__COLLECTION_NAME__]
        ids = collection.find({}, {'test_id': 1})
        return list(ids)

    def get_report_list(self):
        collection = self.connection[self.__COLLECTION_NAME__]
        lists = collection.find({}, {'test_id': 1, 'status': 1, 'reason': 1})
        return list(lists)

    @classmethod
    def serialize_dict(cls, data):
        '''
        serializes a dictionary

        :param data: data to serialize
        '''
        return b64encode(zlib.compress(cPickle.dumps(data, protocol=2))).decode()


    @classmethod
    def deserialize_dict(cls, data):
        '''
        deserializes a dictionary

        :param data: data to deserialize
        '''
        return cPickle.loads(zlib.decompress(b64decode(data.encode())))


class ICSFuzzer(BaseFuzzer):
    """
    用于工控设备的模糊器
    """
    def __init__(self, params, name='ICSFuzzer', logger=None, option_line=None):
        super(ICSFuzzer, self).__init__(name, logger, option_line)
        # self.config.store_all_reports = True  # 保存每一轮报告
        self.params = params

    def _start(self):
        self.logger.info('should keep running? %s' % self._keep_running())
        while self._next_mutation():
            sequence = self.model.get_sequence()
            # self._run_sequence(sequence)
            try:
                self._run_sequence(sequence)
            except KittyException as e:
                # job = self.params['JOB_ID'] 
                job = self.params['JOB']  # 当前任务信息  由runner.py提交
                job['error_msg'] = str(e)
                job['status'] = JobStatus.ERROR  # 出现这个错误是因为PLC已经无法连接，有可能第一次就连接不上
                break
            except Exception as e:
                self.logger.error('Error occurred while fuzzing: %s', repr(e))
                self.logger.error(traceback.format_exc())
                break
        self._end_message()
        if self.session_info.failure_count > 0: 
            job = self.params['JOB'] #TODO
            job['status'] = JobStatus.VULN
            print('error count > 0')

    def _test_environment(self):
        sequence = self.model.get_sequence()
        try:
            if self._run_sequence(sequence):
                raise Exception('Environment test failed')
        except:
            self.logger.info('Environment test failed')
            raise

    def set_target(self, target):
        '''
        调用父类的set_target，然后调用monitor
        :param target: target object
        '''
        super(ICSFuzzer, self).set_target(target)
        pcap_path = os.path.join(config['scan_config_path'], 'pcap', self.params['JOB_ID']) 
        if not os.path.exists(pcap_path):
            os.mkdir(pcap_path)
        target.add_monitor(NetworkMonitor(self.params['INTERFACE'], pcap_path, 'ss_monitor'))
        return self

    def _run_sequence(self, sequence):
        '''
        Run a single sequence
        '''
        self._check_pause()
        self._pre_test()
        session_data = self.target.get_session_data()
        self._test_info()
        resp = None
        for edge in sequence:
            if edge.callback:
                edge.callback(self, edge, resp)
            session_data = self.target.get_session_data()
            node = edge.dst
            node.set_session_data(session_data)
            resp = self._transmit(node)
        return self._post_test()

    def _transmit(self, node):
        '''
        Transmit node data to target.

        :type node:  Template
        :param node: node to transmit
        :return: response if there is any
        '''
        multiple = node.multiple  # multiple表示当前测试报文会被重复几次
        payload = node.render().tobytes()
        self._last_payload = payload
        try:
            return self.target.transmit(payload, multiple)
        except Exception as e:
            self.logger.error('Error in transmit: %s', e)
            raise

    def start(self):
        '''
        Start the fuzzing session

        If fuzzer already running, it will return immediatly
        '''
        if self._started:
            self.logger.warning('called while fuzzer is running. ignoring.')
            return
        self._started = True
        assert self.model
        assert self.user_interface
        assert self.target

        self.dataman = MongoDataManager('fuzz', self.params)
        self.dataman.start()
        if self._test_list is None:
            self._test_list = StartEndList(0, self.model.num_mutations())
        else:
            self._test_list.set_last(self.model.last_index())

        list_count = self._test_list.get_count()
        self._test_list.skip(list_count - 1)
        self.session_info.end_index = self._test_list.current()
        self._test_list.reset()
        self._store_session()
        self._test_list.skip(self.session_info.current_index)
        self.session_info.test_list_str = self._test_list.as_test_list_str()

        self._set_signal_handler()
        self.user_interface.set_data_provider(self.dataman)
        self.user_interface.set_continue_event(self._continue_event)
        self.user_interface.start()

        self.session_info.start_time = time.time()
        self._start_message()
        self.target.setup()
        start_from = self.session_info.current_index #
        if self._skip_env_test:
            self.logger.info('Skipping environment test')
        else:
            self.logger.info('Performing environment test')
            self._test_environment()
        self._in_environment_test = False
        self._test_list.reset()
        self._test_list.skip(start_from)
        self.session_info.current_index = start_from
        self.model.skip(self._test_list.current())
        self._start()
