# coding:utf-8
from flask import Blueprint, jsonify, request, abort, send_from_directory
from utils import mongose
from utils import tools
from bson.objectid import ObjectId, InvalidId
from .constants import PROTOCOLS, JobStatus
from utils import config

import os
import shutil
import time
import binascii

ws = Blueprint('workstation', __name__)
job_mongo = mongose('fuzz', 'jobs')
cases_mongo = mongose('fuzz', 'cases')
session_mongo = mongose('fuzz', 'sessionInfo')
report_mongo = mongose('fuzz', 'reports')


@ws.route('/', methods=['GET', 'POST'])
def index():
    mongo = job_mongo()
    if request.method == 'GET':
        data = mongo.find()
        return jsonify(list(data)), 200
    elif request.method == 'POST':
        data = request.json['data']
        data['time'] = time.time()
        data[' '] = 0
        data['status'] = JobStatus.CREATED
        data['case'] = []
        data['type'] = int(data['type'])
        result = mongo.insert_one(data)
        job_id = binascii.hexlify(result.inserted_id.binary)
        return jsonify({'status': 'success', 'job_id': job_id}), 201
    return abort(404)


@ws.route('/job/<id>', methods=['GET', 'POST', 'DELETE'])
def get_job(id):
    mongo = job_mongo()
    try:
        object_id = ObjectId(id)
    except InvalidId:
        return abort(404)
    if request.method == 'GET':
        job = mongo.find_one({'_id': object_id})
        if job is None:
            return abort(404)
        return jsonify(job), 200
    elif request.method == 'POST':
        data = request.json['data']
        job = mongo.update({'_id': object_id}, {'$set': data})
        return jsonify(job), 200
    elif request.method == 'DELETE':
        pcap_dir_path = os.path.join(config['scan_config_path'], 'pcap', id)
        if os.path.exists(pcap_dir_path):
            try:
                shutil.rmtree(pcap_dir_path)
            except OSError as e:
                print(e.message)
        mongo.delete_one({'_id': object_id})
        return jsonify({'msg': 'Delete success'})
    return abort(404)


@ws.route('/cases', methods=['GET'])
def get_cases():
    mongo = cases_mongo()
    cases = list(mongo.find({}, {'_id': 1, 'title': 1, 'protocol': 1}))
    result = {}
    for protocol in PROTOCOLS:
        result[protocol] = []
    for case in cases:  # 将测试用例按协议分类
        protocol = case['protocol']
        result[protocol].append(case)
    return jsonify(result), 200


@ws.route('/fuzz', methods=['POST'])
def start_fuzz():
    params = request.get_json()['params']
    params['FUZZ_COUNT'] = int(params['FUZZ_COUNT'])
    params['INTERFACE'] = 'en0'  # todo 前端请求
    mongo = job_mongo()
    mongo.find_one_and_update({'_id': ObjectId(params['JOB_ID'])},
                              {'$set': {'params': params, 'status': JobStatus.TO_FUZZ}})
    return jsonify({'status': 'success'}), 200


@ws.route('/fuzz_status/<job_id>', methods=['GET'])
def get_fuzz_status(job_id):
    job_collection = job_mongo()
    job = job_collection.find_one({'_id': ObjectId(job_id)})
    if job is None:
        return jsonify({'msg': 'job id error'}), 404
    session_collection = session_mongo()
    session_info = session_collection.find_one()
    return jsonify({'job': job, 'sessionInfo': session_info}), 200


@ws.route('/download/<job_id>/<test_id>')
def download_pcap(job_id, test_id):
    pcap_path = os.path.join(config['scan_config_path'], 'pcap', job_id)
    return send_from_directory(pcap_path, test_id+'.pcap', as_attachment=True)


@ws.route('/network_status/<job_id>', methods=['GET'])
def get_network_status(job_id):
    mongo = job_mongo()
    job = mongo.find_one({'_id': ObjectId(job_id)})
    if job is None:
        return jsonify({'msg': 'Job id error'}), 404
    if u'params' not in job:
        return jsonify({'msg': 'No ip in the request'}), 404
    params = job['params']
    delay = tools.response_time(params['TARGET_IP'])
    return jsonify({'delay': delay}), 200


@ws.route('/report', methods=['POST'])
def get_case_report():
    request_data = request.get_json()
    job_id = request_data['jobId']
    case_id = request_data['caseId']
    mongo = report_mongo()
    reports = mongo.find({'job_id': job_id, 'case_id': case_id})
    return jsonify({'reports': list(reports)}), 200
