# coding:utf-8
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from utils.encode import JSONEncoder
from cases import init_cases, cases
from vuls import vuls
from workstation import ws
from login import login
from scan_vuls import scan_app
from settings import settings
from pymongo import MongoClient

import datetime
import hashlib
import os


def initial():
    """
    在后端第一次启动时配置admin用户
    """
    mongo = MongoClient()
    db = mongo.fuzz
    users = db.users
    if users.find_one({'username': 'admin'}) is None:
        username = 'admin'
        password = 'admin'
        digest = hashlib.sha256(password).hexdigest()
        user = {
            'username': username,
            'password': digest,
            'role': 'admin',
            'description': u'系统初始化时创建的管理员',
            'time': datetime.datetime.now()
        }
        users.insert(user)
    # init_cases()  # 加载用例信息


initial()
app = Flask(__name__, template_folder='dist', static_folder='dist', static_url_path='')
CORS(app)  # Todo 开发时添加, 用于解决跨域问题
app.json_encoder = JSONEncoder
app.register_blueprint(ws, url_prefix='/workstation')
app.register_blueprint(cases, url_prefix='/cases')
app.register_blueprint(login, url_prefix='/login')
app.register_blueprint(vuls, url_prefix='/vuls')
app.register_blueprint(scan_app, url_prefix='/scan_vuls')
app.register_blueprint(settings, url_prefix='/settings')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'dist'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
