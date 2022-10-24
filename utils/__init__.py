# -*- coding: utf-8 -*-
from pymongo import MongoClient
from .config import ICSConfig
import os


def mongose(db, collection):
    def get_mongo():
        return MongoClient()[db][collection]
    return get_mongo


def get_collection(db, collection):
    return MongoClient()[db][collection]

# ROOT_PATH = os.path.split(os.path.realpath(os.path.join(os.getcwd(), "../..")))[0] # 获取根路径(问题)
ROOT_PATH = os.getcwd() # (原)获取根路径
CONFIG_PATH = os.path.join(ROOT_PATH, 'ics.ini')# 生成ics.ini的绝对路径
config = ICSConfig(config_path=CONFIG_PATH)
