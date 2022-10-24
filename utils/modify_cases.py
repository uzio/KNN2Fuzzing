# coding:utf-8
from datetime import datetime
import os
import shutil
import re


exclusion_files = ['case.py', 'pyc', '__', '.DS_Store']  # 不需要被修改的文件名


def filename(filename):
    return os.path.splitext(filename)[0]


def file_ext(filename):
    return os.path.splitext(filename)[1]


def modify_file(file_path, index):
    for exclusion_file in exclusion_files:  # 排除不相关的文件
        if exclusion_file in file_path:
            return
    index[0] += 1
    index = index[0]
    modify_lines = []
    dir_path = os.path.dirname(file_path)
    # if 'siemens' in file_path:
    #     print(index, file_path)
    #     new_file_path = os.path.join(dir_path, '{}.py'.format(index))
    #     os.rename(file_path, new_file_path)
    #     return
    print(index, file_path)
    if 'profinet' not in file_path:
        return
    with open(file_path, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            # if 'icssploit.' in line:
            #     line = line.replace('icssploit.', '')
            #
            # if 'from kitty.interfaces import WebInterface' in line:  # 不再需要WebInterface
            #     line = 'from kitty.interfaces.base import EmptyInterface\r\n'
            #
            # if 'from kitty.fuzzers import ServerFuzzer' in line:
            #     line = 'from ics_fuzzer import ICSFuzzer\r\n'  # 使用自定义的Fuzzer，将数据写入mongodb中

            # if '    fuzzer = ServerFuzzer()' in line:
            #     line = '    fuzzer = ICSFuzzer(params)\r\n'
            #
            # if '    fuzzer = ICSFuzzer()' in line:
            #     line = '    fuzzer = ICSFuzzer(params)\r\n'

            # if '    fuzzer.set_interface(WebInterface())' in line:
            #     line = '    fuzzer.set_interface(EmptyInterface())\r\n'
            #
            # if "    'protocol':'Omron_fins'" in line:
            #     line = "    'protocol':'omron_fins'\r\n"
            #
            # if "    'type': '1'," in line:
            #     now = datetime.now()
            #     date_time = now.strftime("%m/%d/%Y")
            #     line = "    'type': '1',\r\n    'creator': 'liuyongpan',\r\n    'create_time': '{}',\r\n".format(date_time)
            modify_lines.append(line)
    os.remove(file_path)
    # file_path = os.path.join(dir_path, '{}.py'.format(index))
    with open(file_path, 'w') as fp:
        fp.writelines(modify_lines)


def filter_dirs(file_path):  # 过滤不相关的文件夹，比如kittylogs文件夹
    if 'kittylogs' in file_path:
        shutil.rmtree(file_path)
        return True
    return False


def visit_directory(dir_path, index):
    """
    遍历目录
    :return:
    """

    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if filter_dirs(file_path):
            continue
        if not os.path.isdir(file_path):  # 目录
            modify_file(file_path, index)
        else:
            visit_directory(file_path, index)


def clean_pyc(dir_path):
    """
    清除xxx.pyc文件
    :param dir_path:
    :return:
    """
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if filter_dirs(file_path):
            continue
        if not os.path.isdir(file_path):  # 目录
            if '.pyc' in file_path:
                os.remove(file_path)
        else:
            clean_pyc(file_path)


def modify_cases():
    cases_path = '/Users/shaoshuai/SS/Fuzz/cases'
    index = [0]
    visit_directory(cases_path, index)


if __name__ == '__main__':
    # clean_pyc('/Users/shaoshuai/SS/Fuzz/cases')
    modify_cases()
