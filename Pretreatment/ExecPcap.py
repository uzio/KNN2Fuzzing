#!/usr/local/bin/python
# encoding: utf-8

import os
import sys
import csv
import scapy
from scapy.all import *
from scapy.utils import PcapReader

###
## pcap2csv
###
def pcap2csv(pcapath):
    '''
    pcap转csv
    
    pcapath: pcap文件路径
    '''
    if not os.path.exists(pcapath):
        logging.error('\n#! 文件在默认路径下不存在 !#\n')
        raise
    rpkts = rdpcap(pcapath)

    filtered = []
    for i in range(len(rpkts)):
        pkts = str(rpkts[i]['Raw']).encode('hex')
        if pkts[17] == '1': # 给数据包设立筛选条件
            filtered.append(pkts)
        else:
            continue
    ##
    csvpath = os.path.dirname(__file__) + '/Data/raw/csv/' + pcapath.split("/")[-1].split(".")[0]+'_raw'+'.csv'
    if not os.path.exists(os.path.dirname(csvpath)):
        os.makedirs(os.path.dirname(csvpath))
    with open(csvpath,'wb') as f:
        fcsv = csv.writer(f)
        for pkt in filtered:
            Title = pkt[0:14]
            #
            Header = pkt[14:34]
            #
            Param = pkt[34:62]
            #
            Data = pkt[62:]
            ##
            PID = Header[0:2]# Protocol ID
            ROSCTR = Header[2:4]
            RID = Header[4:8]# Redundancy Idetification
            PDUR = Header[8:12]# Potocol Data Unit referencr
            Para_Lenth = Header[12:16]
            Data_Lenth = Header[16:20]
            ##
            Func = Param[0:2]
            if Func == 'f0': # 区分发送包和响应包
                continue
            ItemCount = Param[2:4]
            Items = Param[4:]

            flag = 'na'# 分类标志，待分类标记为 'na'
            fcsv.writerow([Title,PID,ROSCTR,RID,PDUR,Para_Lenth,Data_Lenth,Func,ItemCount,Items,Data,flag])
    f.close()
    return csvpath

# if __name__ == '__main__':
#     pcap2csv('../demo.pcap','test.csv')
