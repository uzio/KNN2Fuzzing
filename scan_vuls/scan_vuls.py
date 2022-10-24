# coding:utf-8
from pymongo import MongoClient
from flask import Blueprint, jsonify, request
from redis import Redis
from rq import Queue
from rq.job import Job
from utils import config

import json
import scan_models
import zgrab

scan_app = Blueprint('scan', __name__)
client = MongoClient()
db_fuzz = client.fuzz
vulnerability = db_fuzz.vulnerability
jobs = db_fuzz.jobs

redis_client = Redis()
q = Queue(connection=redis_client, name='scan')


protocol_to_tcp_port = {
    'http': 80,
    'siemens': 102,
    'modbus': 502,
    'clearscada': 80,
    'ftp': 21,
    'telnet': 23,
    'Siemens_HMI_miniweb': 80,
    'ethip': 44818,
    'dnp3': 20000,
    'crimson': 789,
    'pcworx': 1962,
    'fox': 1911,
    'codesys': 2455,
    'bacnet': 47808,
    'omron': 9600,
    'tls': 443
}
protocol_to_udp_port = {
    'wincc': 1434,
    'Siemens_Scalance': 161,
}


@scan_app.route('/scan', methods=["POST"])
def scan():
    """
    向任务队列发送任务，调用zgrab2来扫描目标
    :return:
    """
    request_data = request.get_json()
    ip = request_data['ip']   # 这里的IP地址是列表，表示多个目标

    args = (config['scanner'], ip, config['scan_config_path'])
    job = q.enqueue(zgrab.scan, args=args, timeout=600)
    print('job_id:', job.get_id())
    return jsonify({
        'code': 20000,
        'job': job.get_id()
    })


@scan_app.route('/result/<job_key>', methods=['GET'])
def get_results(job_key):
    """
    获取任务结果，未完成则返回等待信息
    :param job_key:
    :return:
    """
    job = Job.fetch(job_key, connection=redis_client)
    if job is None:
        return jsonify({
            'code': 20000,
        })
    if job.is_finished:
        result, error, retcode = job.result
        data = json.loads(result)['data']
        tcp_ports = []
        udp_ports = []
        for _, module in data.items():
            if module['protocol'] in protocol_to_tcp_port:
                port = protocol_to_tcp_port[module['protocol']]
                if port in tcp_ports:
                    continue
                tcp_ports.append(port)
            elif module['protocol'] in protocol_to_udp_port:
                port = protocol_to_udp_port[module['protocol']]
                if port in udp_ports:
                    continue
                udp_ports.append(port)

        return jsonify({
            'code': 20000,
            'results': result,
            'tcpPorts': tcp_ports,
            'udpPorts': udp_ports,
            'error': error,
            'retcode': retcode,
            'status': 1
        })
    if job.is_failed:
        return jsonify({
            'code': 500016,
            'message': '任务队列错误'
        })
    return jsonify({
        'code': 20000,
    })


@scan_app.route('/vuls', methods=['POST'])
def search_vuls():
    """
    请求中包括设备信息，通过设备信息来获取漏洞
    :return:
    """
    request_data = request.get_json()
    # info = request_data['info']  # 这里的IP地址是列表，表示多个目标
    protocols = request_data['protocols']
    result = []
    for protocol, info in protocols.items():
        ret = scan_models.scan(protocol, info)
        result.extend(ret)
    return jsonify({
        'code': 20000,
        'vuls': list(result)
    })
