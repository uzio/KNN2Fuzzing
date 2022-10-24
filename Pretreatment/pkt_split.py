#!/usr/local/bin/python
# encoding: utf-8

from scapy.all import repr_hex
    
def pkt_split(pkt):
    '''原生包拆分'''
    pkt = repr_hex(str(pkt))  # 对发送出的数据包16进制字符串转码
    # 以下是对发送出的数据包拆分
    Title = pkt[0:14],
    #
    Header = pkt[14:34]
    #
    Param = pkt[34:62]
    #
    Data = pkt[62:]
# 以下是对发送出的数据包进一步拆分 pkt_split
    ps = {
        ##Title
        'Conn':Title[:],
        ## Header
        'PID': Header[0:2],  # Protocol ID
        'ROSCTR': Header[2:4],
        'RID': Header[4:8],  # Redundancy Idetification
        'PDUR': Header[8:12],  # Potocol Data Unit referencr
        'Para_Lenth': Header[12:16],
        'Data_Lenth': Header[16:20],
        ## Param
        'Func': Param[0:2],
        'ItemCount': Param[2:4],
        'Items': Param[4:],
        ## Data
        'Data' : Data[:],
    }
    return ps