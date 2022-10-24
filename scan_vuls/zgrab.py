# coding=utf-8
import os
import subprocess


def scan(zgrab_address, ips, config_path):
    """
    用于调用zgrab来扫描目标
    """
    args = [
        zgrab_address,
        'multiple',
        '-c',
        '{}.ini'.format(os.path.join(config_path, 'hardware'))
    ]  # 使用zgrab2的多模块扫描
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(ips)
    except:
        process.kill()
        stdout, stderr = process.communicate()
    retcode = process.poll()
    if retcode:
        print(stderr)
        raise subprocess.CalledProcessError(retcode, args, output=stdout)
    return stdout, stderr, retcode
