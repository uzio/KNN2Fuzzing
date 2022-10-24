#!/usr/local/bin/python
# encoding: utf-8

import Pretreatment as Pre
import os
import re
import logging
import numpy as np
from tqdm import tqdm


class InitSet():
    '''
    数据预处理及模型初始化

    参数说明：
    -name: 数据文件名(包含拓展名)
    -path: 数据文件路径 (pcap默认路径: Pretreatment/Data/raw/pcap, csv默认路径: Pretreatment/Data/raw/csv )
    -update: (bool) 是否使用新增数据重新生成种子集

    功能说明：

    '''
    def __init__(self, name=None, path=None, update=False):
        
        if name is not None:
            self.exname = name.split('.')[-1] # 获取拓展名
        else:
            self.seed = os.path.dirname(Pre.__file__) + '/Data/seed/'+ 'seed.csv'
            return

        if path is None:
            if self.exname == 'pcap':
                self.path = os.path.dirname(Pre.__file__) + '/Data/raw/pcap/'+ name
            elif self.exname == 'csv':
                self.path = os.path.dirname(Pre.__file__) +'/Data/raw/csv/' + name
            else:
                logging.error('\n#! 不支持的文件类型 !#\n')
                raise
        else:
            if self.exname in ['pcap', 'csv']:
                self.path = path
            else:
                logging.error('\n#! 不支持的文件类型 !#\n')
                raise

        if os.path.exists(self.path):
            logging.info('\n\n+文件路径: '+self.path+'\n')
        else:
            logging.error('\n#! 文件在默认路径下不存在 !#\n')
            raise
        
        # 分类基准
        self.standard = os.path.dirname(Pre.__file__) + '/Data/temp/standard_normal.csv'
        if not (os.path.isfile(self.standard)):
            os.system('touch {}'.format(self.standard))
        
        # 种子集
        self.update = update
        if self.update: 
            selpath = self.Init4Mod()

            while(True):
                flag = str(input("\n请选择目标标签以生成种子集：")) 
                if flag not  in self.flags:
                    print('#! 非期望输入，请在给出的标签中进行选择.\n>>允许的标签：{}'.format(self.flags)) #  非法输入的处理
                else:
                    break

            self.seed = self.setSeed(flag, selpath)
        else:
            self.seed = os.path.dirname(Pre.__file__) + '/Data/seed/'+ 'seed.csv'

    def Init4Data(self):
        '''
        数据初始化
        '''
        if self.exname == 'pcap':
            rawpath = Pre.pcap2csv(self.path)
            self.path = rawpath
        elif self.exname == 'csv':
            rawpath = self.path
        else:
            logging.error('\n#! 不支持的文件类型 !#\n')
            raise
        
        datapath =  Pre.Digitization(rawpath) # 数据标准化

        return datapath

 
    def standardUpdate(self, standard, isadd=True):
        '''
        更新分类基准文件

        -standard : 新增分类基准文件路径
        -isadd : 是否在原先基准文件中追加
        '''
        new = Pre.Digitization(standard)
        gather = Pre.sc(new)
        gather.writeCSV(gather.data, self.standard,is_add=isadd)

        print('\n>>分类基准已更新>>')

    
    ##
    def divide(self, path):
            '''
            划分数据集
            '''
            fr = open(path)
            lines = fr.readlines() # 按行读取数据集
            line_nums = len(lines) # 获取记录的数量
            print('\n'+path.split('/')[-1].split('.')[0]+u'条目总数：%d'%line_nums)

            l = len(lines[0].strip().split(',') ) # 记录划分的列数

            X_mat = np.zeros((line_nums,(l-1))) 
            y_label = []

            for i in range(line_nums):
                line = lines[i].strip().split(',')
                item_mat = []
                for j in range(l-1):
                    item_mat.append(float(line[j])) # 字符串处理
                
                X_mat[i , 0:] = item_mat[0:(l-1)] # 选择特征
                y_label.append(item_mat[-1]) # 类标

            y = []
            for  n in y_label:
                y.append(int(n))
            y = np.array(y, dtype = int)
            
            return X_mat, y, len(lines)

    def Init4Mod(self):
        '''
        分类模型初始化
        '''
        print('\n>>>更新分类模型>>>')

        train = self.divide(self.standard) # 分类基准
        test = self.divide(self.Init4Data()) # 待分类

        print("\n>分类：")
        self.flags = [] # 类别标签

        #分类文件路径
        selected = os.path.dirname(Pre.__file__) + '/Data/selected/'+ 'selected.csv' 
        if not os.path.exists(selected):
            logging.error('\n#! 已分类文件不存在 !#\n')
            raise
        
        record = Pre.sc(selected,selected)
        sele_dat = Pre.sc(selected).data # 已分类数据记录

        toselect = self.path
        if not os.path.exists(toselect):
            logging.error('\n#! 待分类文件不存在 !#\n')
            raise

        to_dat = Pre.sc(toselect,toselect).data # 待分类数据记录

        for i in tqdm(range(test[2])):
            flag = str(Pre.FK.classify(test[0][i], train[0],train[1],3)) # TODO 参数k是否开放为可设置参数
            to_dat[i][-1] = flag # 标记分类

            if flag not in self.flags:
                self.flags.append(flag)

        print ('\n现有分类标签：')
        print self.flags

        sele_dat.extend(to_dat)
        record.writeCSV(sele_dat, is_add=True) 
        selpath = record.changeCSV(record.newfilepath) # 返回分类完成的数据集

        return selpath 


    def setSeed(self, filters, ori, col=-1):
        '''
        生成种子集

        -filters: 选作生成种子集的数据的标签(列表形式)
        -ori: 待筛数据路径
        -col: 分类标签所在列的序号(默认为最后一列)
        '''

        seedpath = os.path.dirname(Pre.__file__) + '/Data/seed/seed.csv'
        if not os.path.exists(os.path.dirname(seedpath)):
            os.makedirs(os.path.dirname(seedpath))
            
        sav = Pre.sc(ori,seedpath)
        sav.writeCSV(sav.selectCSV(filters,col)) # TODO 设置种子集的大小
        print('\n>>种子集已生成>>\n')
        return seedpath

    @staticmethod
    def setFilterKey(pkt1, pkt2):
        '''
        比较变异数据包差异区块，生成筛选关键字
        '''
        p1=Pre.psp.pkt_split(pkt1)
        p2=Pre.psp.pkt_split(pkt2)
        
        diffs = set()
        keys = set(p1.keys() +p2.keys())
        for k in keys:
            if cmp(p1.get(k), p2.get(k)):
                diffs.add(k)

        path=os.path.dirname(Pre.__file__) + '/Mod/' + 'filterKey.txt'
        if not os.path.exists(os.path.dirname(path)):
            logging.info('\n#!创建筛选关键字记录!#\n')
        with open(path,'wb') as f:
            for k in diffs:
                f.write(k+'\r\n') #XXX 初始化筛选关键字

# if __name__ == '__main__':
#     r = InitSet('demo_raw.csv', './demo_raw.csv', update=True)
