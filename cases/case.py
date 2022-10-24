# coding:utf-8
from pymongo import MongoClient
from flask import Blueprint, jsonify, request, abort
from bson import ObjectId

import pymongo
import json
import os
import sys

cases = Blueprint('cases', __name__)
client = MongoClient()

def init_cases():
    """
    初始化漏洞库, cases目录下的所有测试用例，然后写入数据库fuzz的cases中
    :return:
    """
    cases = client['fuzz']['cases']
    cases_dir = os.path.dirname(__file__)  # cases目录地址
    i = 1
    for proto in os.listdir(cases_dir):
        proto_dir = os.path.join(cases_dir, proto)
        if not os.path.isdir(proto_dir):
            continue
        for func_code_dir in os.listdir(proto_dir):  # 测试用例文件的名称，包括尾缀
            func_code_dir_path = os.path.join(proto_dir, func_code_dir)
            if not os.path.isdir(func_code_dir_path):
                continue
            sys.path.append(func_code_dir_path)  # 将cases目录里的case放入系统变量PATH中
            for case in os.listdir(func_code_dir_path):
                case_path = os.path.join(func_code_dir_path, case)  # 测试用例的路径
                if 'kitty' in case_path or not os.path.isfile(case_path) or case.startswith('__') or file_ext(case) == '.pyc':
                    continue
                print(i, ':IMPORT-------' + case_path)
                case_name = filename(case)  # 去除尾缀
                import_case(case_name, func_code_dir_path, cases, case_path)
                i += 1
            sys.path.remove(func_code_dir_path)
    client.close()


def import_case(module_name, proto_dir, mongo, case_path):
    module = __import__(module_name)
    if mongo.find_one({'case_path': case_path}):  # 已经存在这个测试用例
        return
    module.INFO['module_name'] = module_name
    module.INFO['proto_path'] = proto_dir
    module.INFO['case_path'] = case_path
    module.INFO['_id'] = ObjectId()
    mongo.insert_one(module.INFO)
    del module


def filename(file):
    return os.path.splitext(file)[0]


def file_ext(file):
    return os.path.splitext(file)[1]


@cases.route('/', methods=['GET', 'DELETE', 'POST'])
def get_cases():
    client = MongoClient()
    c = client.fuzz.cases
    if request.method == 'DELETE':
        _id = request.data
        case = c.find_one({'_id': ObjectId(_id)})
        if case is not None:
            if os.path.isfile(case['case_path']):
                os.remove(case['case_path'])
            c.delete_one({'_id': ObjectId(_id)})
        client.close()
        return jsonify({'status': 'success'}), 200

    elif request.method == 'GET':
        result = c.find().sort([{'_id', pymongo.DESCENDING}])
        count = c.find().count()
        return jsonify({'cases': list(result), 'count': count}), 200

    elif request.method == 'POST':
        vul_file = request.files['file']
        content = vul_file.read()
        info = ''
        can_add_info = False
        can_break = False
        for line in content.split('\n'):
            if 'INFO' in line:
                can_add_info = True
            if 'def fuzz(params)' in line:
                can_break = True

            if can_break:
                break
            if can_add_info:
                info += line

        if not can_break or not can_add_info:
            return jsonify({'msg': u'测试用例内容不符合规范'}), 400

        info = info[info.find('{')-1:]
        info = info.replace("\'", "\"")
        try:
            info = json.loads(info)
        except Exception as e:
            return jsonify({'msg': u'测试用例内容不符合规范:%s' % e.message}), 400

        dir_path = os.path.join(os.getcwd(), 'cases', info['protocol'])
        count = len(os.listdir(dir_path))
        module_name = info['protocol']+str(count)
        file_path = os.path.join(dir_path, module_name+'.py')
        that_case = c.find_one({'title': info['title']})
        if that_case is not None or os.path.isfile(file_path):
            return jsonify({'msg': u'测试用例重复添加'}), 400

        with open(file_path, 'w') as fp:
            fp.write(content)

        info['module_name'] = module_name
        info['proto_path'] = dir_path
        info['case_path'] = file_path
        cases = client['fuzz']['cases']
        cases.insert_one(info)
        return '', 200
