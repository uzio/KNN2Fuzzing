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

        if self.oldfilepath == self.newfilepath:
            self.newfilepath = os.path.dirname(self.newfilepath) + '/temp.csv'
            os.system('touch {}'.format(self.newfilepath))


    def writeCSV(self, data, filepath=None, header=True, is_add=False):
        '''
        写入csv

        -data : 写入csv的数据

        -filepath : 写入文件路径，可选

        -header :
        --True : 写入表头
        --False : 跳过表头

        -is_add : 是否为追加数据
        '''
        if filepath is None and self.newfilepath is not None:
            filepath = self.newfilepath
            if filepath is None:
                logging.error(u'#! 文件目标写入路径缺失 !#')
                raise
        
        if is_add:
            wtype = 'ab' # 追加
        else:
            wtype = 'wb' # 新建/覆写
            
        with open(filepath,wtype) as f:
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


    def selectCSV(self,  filters, col, data = None):
        '''
        筛选CSV数据

        -data: 待筛选数据，可选
        -filters : 筛选条件(队列，可多条件)
        -col : 标签所处列

        例：
            selectCSV(data, ['0', '1'], 8) # 筛选data中带有0或1标签的数据，其中标签在第8列

            selectCSV(['0'], 6) # 筛选读取的数据文件中带有0标签的数据，其中标签在第6列
        '''
        if data is None:
            data = self.data
        filtered = []
        for row in data:
            if row[col] in filters:
                filtered.append(row) 
        return filtered

    def changeCSV(self, chg_file, oldfile=None):
        '''
        更换csv文件
        
        -chg_file : 待更名文件路径
        -oldfile : 待删除的原名文件路径, 可选
        '''
        if oldfile is None:
            oldfile = self.oldfilepath
            
        name = '/' + oldfile.split('/')[-1]
        os.remove(oldfile)
        newfile = os.path.dirname(chg_file)+name
        os.rename(chg_file, newfile)
        return newfile

# if __name__ == '__main__':
# #     sc = SCSV('./S7_Job_WriteVar.csv','test00.csv')
# #     sc.writeCSV(sc.selectCSV(['01'],2), './test01.csv')
# #  sc = SCSV(os.path.dirname(__file__)+'/Data/seed/temp.csv')