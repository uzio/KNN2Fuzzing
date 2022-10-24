# coding:utf-8
from flask import Blueprint, jsonify, request, abort
from utils.broadlink_helper import get_power_status, set_power

import time

settings = Blueprint('settings', __name__)


@settings.route('/power', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        status = get_power_status()
        result = []
        for k, v in status.items():
            result.append({'name': k, 'status': v})
        return jsonify(result), 200
    elif request.method == 'POST':
        request_data = request.get_json()
        operation_type = request_data['type']
        if operation_type == 1:  # 普通开关操作
            status = request_data['status']
            target_id = int(request_data['id'])
            set_power(target_id, status)
        else:  # 重启
            target_id = int(request_data['id'])
            set_power(target_id, False)
            time.sleep(1)
            set_power(target_id, True)
        return jsonify({'status': 'success'}), 200

    return abort(404)

