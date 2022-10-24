#!/usr/local/bin/python
# encoding: utf-8
import os
import csv
from tqdm import tqdm

def Digitization(filepath):
    '''元数据数值化处理'''
    fr = open(filepath)

    newfilename = filepath.split("/")[-1].split(".")[0].split('_')[0]+'_normal'+'.csv'
    wrpath =  os.path.dirname(__file__) + '/Data/temp/'
    if not os.path.exists(wrpath):
        os.makedirs(wrpath)

    newfilepath = wrpath + newfilename

    fw = open(newfilepath,'wb')
    csv_writer = csv.writer(fw)
    lines = fr.readlines() # 按行读取
    line_nums = len(lines) # 获取记录数量
    
    print('\n>标准化处理进程：')
    for i in tqdm(range(line_nums)):
        line = lines[i].strip().split(',')
        item = []
        for j in range(len(line)):
            if j < (len(line)-1):
                data = int(line[j],16)# hexString2int
                item.append(MinMaxScaler(data, len(line[j])))
            else:
                item.append(line[j])
        csv_writer.writerow(item)
    fw.close()
    fr.close()

    return newfilepath


def MinMaxScaler(data, lenth, radix=16):
    '''
    针对元数据进行归一化

    data := 元数据
    lenth := 数据占用长度
    radix := 进制 
    '''
    return float(data) / (radix**lenth - 1)



# if __name__ == '__main__':
#     name = Digitization('./701.csv')
#     print "标准化完成,输出文件为%s"%name
    