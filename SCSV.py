#!/usr/local/bin/python
# encoding: utf-8
import os
import sys
import csv
import logging

class SCSV():
    '''
    筛选并保存csv数据

    -oldfilepath : 原数据文件路径
    -newfilepath : 目标数据文件路径，可选
    '''

    def __init__(self, oldfilepath, newfilepath = None):
        self.oldfilepath =oldfilepath
        self.newfilepath = newfilepath
        self.data = self.readCSV()


    def writeCSV(self, data, filepath=None, header=True):
        '''
        写入csv

        -data : 写入csv的数据

        -filepath : 写入文件路径，可选

        -header :
        --True : 写入表头
        --False : 跳过表头
        '''
        if filepath is None and self.newfilepath is not None:
            filepath = self.newfilepath
            if filepath is None:
                logging.error(u'文件目标写入路径缺失')
                raise
        with open(filepath,'wb') as f:
            writer = csv.writer(f)
            for row in data:
                if header:
                    writer.writerow(row)
                else:
                    header = True
                    continue

        f.close()


    def readCSV(self, header = False):
        '''
        读取csv，返回行数据构成的列表
            
        -header :
        --True : 丢弃表头
        --False : 保留表头
        '''
        data = []
        with open(self.oldfilepath,'rb') as f:
            reader = csv.reader(f)
            if header:
                head_row = next(reader)
            for row in reader:
                data.append(row)

        f.close()
        return data


    def selectCSV(self,  filters, flag, data = None,):
        '''
        筛选CSV数据

        -data: 待筛选数据，可选
        -filters : 筛选条件(队列，可多条件)
        -flag : 标签所处列

        例：
            selectCSV(data, ['0', '1'], 8) # 筛选data中带有0或1标签的数据，其中标签在第8列

            selectCSV(['0'], 6) # 筛选读取的数据文件中带有0标签的数据，其中标签在第6列
        '''
        if data is None:
            data = self.data
        filtered = []
        for row in data:
            if row[flag] in filters:
                filtered.append(row) 
        return filtered

if __name__ == '__main__':
    sc = SCSV('./S7_Job_WriteVar.csv','test00.csv')
    sc.writeCSV(sc.selectCSV(['01'],2), './test01.csv')