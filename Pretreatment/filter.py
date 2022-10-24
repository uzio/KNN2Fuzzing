#!/usr/local/bin/python
# encoding: utf-8

import os
import math
import logging
import Pretreatment as Pre


def filter(dataSet, pkt_split, obj=None):
    '''
    筛包
    
    $
        obj={
            'Conn', 
            'PID', 
            'ROSCTR', 
            'RID', 
            'PDUR', 
            'Para_Lenth',
             'Data_Lenth', 
             'Func', 
             'ItemCount', 
             'Items', 
             'Data'}
    '''
    if obj is None:
        path=os.path.dirname(__file__) + '/Mod/' + 'filterKey.txt'
        if not os.path.exists(os.path.dirname(path)):
            logging.warning('\n>>>筛选条件未设置，跳过筛选>>>')
            return True
        with open(path,'r') as f:
            objs=f.readlines() #XXX 改进为遍历读取所有记录，逐条筛选

    obj_flag={'Conn':0, 'PID':1, 'ROSCTR':2, 'RID':3, 'PDUR':4, 'Para_Lenth':5, 'Data_Lenth':6, 'Func':7, 'ItemCount':8, 'Items':9, 'Data':10}
    
    for obj in objs:
        obj=obj.strip()
        if obj not in obj_flag: #TODO 可以向仅判断一次改进
            logging.warning('\n>>>筛选条件未匹配，跳过筛选>>>')
            return True

        lenth = len(dataSet[0][obj_flag[obj]])
        for i in range(len(dataSet)):
            compa = Pre.binCount(
                Pre.str_bw_xor(
                    dataSet[i][obj_flag[obj]], pkt_split[obj])
            )  # 过筛
        if compa < math.ceil(0.5*lenth):  # 不同的位不足总位数一半的视为不合格
            return False
    return True