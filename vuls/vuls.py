# coding:utf-8
import pickle
import pymongo
from pymongo import MongoClient
from bson import ObjectId
from flask import Blueprint, jsonify, request
from redis import Redis
from rq import Queue, Worker
from utils.cnvd import import_vuls

# redis_client = Redis()
# queue = Queue(connection=redis_client, name='update_vuls', default_timeout='1h')


vuls = Blueprint('vuls', __name__)
client = MongoClient()
db_fuzz = client.fuzz
vulnerability = db_fuzz.vuls


@vuls.route('/', methods=['GET', 'POST'])
def get_vuls():
    if request.method == 'GET':
        data = request.values
        page = int(data['page'])
        page -= 1
        if page <= 0:
            page = 0
        page_size = int(data['pageSize'])
        result = vulnerability.find().sort([{u'公开日期', pymongo.DESCENDING}]).skip(page*page_size).limit(page_size)
        count = vulnerability.find().count()
        return jsonify({'vuls': list(result), 'count': count}), 200
    elif request.method == 'POST':
        data = request.get_json()
        vul_id = data['id']
        vulnerability.delete_one({'_id': ObjectId(vul_id)})
        return '', 200


@vuls.route('/import', methods=['POST'])
def up_load_vul():
    vul_file = request.files['file']
    content = vul_file.read()
    vul = pickle.loads(content)
    if vulnerability.find_one(vul):
        return jsonify({
            'msg': '重复添加'
        }), 200
    vulnerability.insert_one(vul)
    return jsonify({
        'msg': '添加成功'
    }), 200


@vuls.route('/online', methods=['POST', 'GET'])
def online_upload_vuls():
    # if request.method == 'POST':
    #     queue.enqueue(import_vuls)
    #     return jsonify({'status': 'updating'}), 200
    # worker = Worker.all(queue=queue)[0]
    # if worker.state == 'busy':
    #     return jsonify({'status': 'updating'}), 200
    return jsonify({'status': 'done'}), 200
