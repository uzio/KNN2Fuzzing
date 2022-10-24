# coding:utf-8
from pymongo import MongoClient
from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId, InvalidId
from datetime import datetime
import hashlib

login = Blueprint('login', __name__)
client = MongoClient()
db_fuzz = client.fuzz
users = db_fuzz.users


@login.route('/', methods=['POST'])
def do_login():
    request_data = request.get_json()
    username = request_data['username']
    password = request_data['password']
    user = users.find_one({'username': username})
    digest = hashlib.sha256(password).hexdigest()
    if user is None:
        return jsonify({'msg': '用户不存在'}), 403
    if user['password'] != digest:
        return jsonify({'msg': '密码错误'}), 403
    return jsonify({
        'msg': '登陆成功',
        'token': user['_id'],
        'username': username,
        'role': user['role']
    }), 200


@login.route('/register', methods=['PUT'])
def register():
    request_data = request.get_json()
    if 'token' not in request_data or \
        'data' not in request_data:
        return jsonify({'msg': '信息不完整'}), 400
    token = request_data['token']
    form = request_data['data']
    if 'username' not in form or \
        'password' not in form or \
        'password2' not in form or \
        'role' not in form:
        return jsonify({'msg': '表单信息不完整'}), 400

    if form['password2'] != form['password']:
        return jsonify({'msg': '密码不一致'}), 400

    if len(form['username']) == 0:
        return jsonify({'msg': '用户名为空'}), 400

    target = users.find_one({'username': form['username']})
    if target:
        return jsonify({'msg': u'用户名"%s"已存在' % form['username']}), 400

    if len(form['password']) == 0:
        return jsonify({'msg': '密码为空'}), 400

    password = form['password']
    password2 = form['password2']
    if password != password2:
        return jsonify({'msg': '密码不一致'}), 400

    try:
        user = users.find_one({'_id': ObjectId(token)})
    except InvalidId:
        return jsonify({
            'msg': '用户ID错误'
        }), 401

    if user['role'] == 'normal':  # 普通用户权限无法创建其他用户
        return jsonify({
            'msg': u'普通用户"%s"无法创建其他用户' % user['username']
        }), 401

    digest = hashlib.sha256(password).hexdigest()
    users.insert_one({
        'username': form['username'],
        'password': digest,
        'role': form['role'],
        'description': form['description'],
        'time': datetime.now()
    })
    return jsonify({}), 200


@login.route('/info', methods=['POST'])
def get_info():
    request_data = request.get_json()
    user_id = request_data['token']
    try:
        user = users.find_one({'_id': ObjectId(user_id)})
    except InvalidId:
        return jsonify({
            'msg': '用户ID错误'
        }), 401
    return jsonify({
        'role': user['role'],
        'username': user['username']
    }), 200


@login.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        data = request.values
        page = int(data['page'])
        page -= 1
        if page <= 0:
            page = 0
        page_size = int(data['pageSize'])
        result = users.find().skip(page*page_size).limit(page_size)
        count = users.find().count()
        return jsonify({'users': list(result), 'count': count}), 200

    elif request.method == 'POST':  # 删除用户
        request_data = request.get_json()
        if 'token' not in request_data or \
           'username' not in request_data:
            return jsonify({'msg': '表单信息不完整'}), 400

        if request_data['username'] == 'admin':
            return jsonify({
                'msg': u'无法删除管理员'
            }), 404

        user_id = request_data['token']
        user = users.find_one({'_id': ObjectId(user_id)})
        if user is None:
            return jsonify({
                'msg': '请登陆后再删除'
            }), 300
        if user['role'] != 'admin':
            return jsonify({
                'msg': u'普通用户"%s"无法删除用户' % user['username']
            }), 401
        users.delete_one({'username': request_data['username']})
        return jsonify({
                'msg': '请登陆后再删除'
            }), 200
