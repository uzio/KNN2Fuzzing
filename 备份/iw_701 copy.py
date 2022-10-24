# coding:utf-8
import pymongo
import time
import Pretreatment as Pre#
from InitSet import InitSet #
from get_inet import get_net  #
# from SCSV import SCSV as sc #
from kitty.model import Template
from kitty.interfaces import WebInterface
from kitty.fuzzers import ServerFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import *
from protocols.cotp import *
from protocols.s7comm import *

RANDSEED = int(RandShort())

INFO = {
    'title': 'Data write时，Parameter中ItemCount=0x76 ',
    'des': 'Data write时，Parameter中ItemCount=0x76',
    'id':   'beta_1',
    'type': '1',
    'creator': 'uzio',
    'create_time': '06/16/2021',
    'protocol': 'siemens'
}

def pkt_split(pkt):
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
        ##
        'PID': Header[0:2],  # Protocol ID
        'ROSCTR': Header[2:4],
        'RID': Header[4:8],  # Redundancy Idetification
        'PDUR': Header[8:12],  # Potocol Data Unit referencr
        'Para_Lenth': Header[12:16],
        'Data_Lenth': Header[16:20],
        ##
        'Func': Param[0:2],
        'ItemCount': Param[2:4],
        'Items': Param[4:],
    }
    return ps

def fuzz(params):
    SRC_TSAP = '\x01\x00'  # 设备地址 发送方
    DST_TSAP = '\x01\x02'  # 设备地址 接受方
    COTP_CR_PACKET = TPKT() / COTPCR()
    COTP_CR_PACKET.Parameters = [COTPOption() for i in range(3)]  # 循环3次
    COTP_CR_PACKET.PDUType = "CR"  # Connect Request设置PDU数据类型CR
    COTP_CR_PACKET.Parameters[0].ParameterCode = "tpdu-size"  # 设置PDU数据长短
    COTP_CR_PACKET.Parameters[0].Parameter = "\x0a"  # PDU数据长度值
    COTP_CR_PACKET.Parameters[1].ParameterCode = "src-tsap"  # 调用 设备地址 发送方
    COTP_CR_PACKET.Parameters[1].Parameter = SRC_TSAP
    COTP_CR_PACKET.Parameters[2].ParameterCode = "dst-tsap"  # 调用 设备地址 接受方
    COTP_CR_PACKET.Parameters[2].Parameter = DST_TSAP

    COTP_CR_TEMPLATE = Template(name='cotp cr template', fields=[
        ScapyField(COTP_CR_PACKET, name='cotp cr', fuzzable=False),
    ])  # 调用KITTY框架中COTP模板数据包

    SETUP_COMM_PARAMETER_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ROSCTR="Job",
                                                                    Parameters=S7SetConParameter())
    # 设置第一次连接，获取许可，EOT=1没有触发1568漏洞
    SETUP_COMM_PARAMETER_TEMPLATE = Template(name='setup comm template', fields=[
        ScapyField(SETUP_COMM_PARAMETER_PACKET,
                   name='setup comm', fuzzable=False),
    ])  # 第二次连接，正式连接

    access = True
    while access:
        READ_SZL_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ProtocolId=0x32, ROSCTR="Job",  # 0x32 S7comm协议
                                                            Parameters=S7WriteVarParameterReq(  # S7写入参数请求包
                                                                ItemCount=RandByte(),  # 0x76,对应Items
                                                                Items=S7WriteVarItemsReq(
                                                                    ItemCount=0x0003,  # 对应Data
                                                                    BlockNum=0x0001)),  # DB块号
                                                            Data=S7WriteVarDataItemsReq(
                                                                TransportSize=0x05,  # 0x05写入
                                                                Data='\x01\x02\x16'  # 对应ItemCount，有3段
                                                            )
                                                            )  # 提交SNAP工作内容，发送出的数据包
        # TODO
        # READ_SZL_PACKET["S7Header"].show()
        rule = InitSet('demo_raw.csv')
        # dataSet = sc('./701_selected.csv' .readCSV()  # 读取701_selected.csv数据集
        dataSet = Pre.sc(rule.seed).readCSV()

        ps = pkt_split(READ_SZL_PACKET)
       
        compa = Pre.binCount(Pre.str_bw_xor(
            dataSet[0][8], ps['ItemCount']))  # 过筛，异或运算筛选

        if compa > 2:  # 不同位大于2有效
            access = False

    READ_SZL_TEMPLATE = Template(name='Data write时，Parameter中ItemCount=0x76', fields=[
        ScapyField(READ_SZL_PACKET, name='read szl',
                   fuzzable=True, fuzz_count=params['FUZZ_COUNT']),
    ])  # 发送数据包作为模板，对该模板进行模糊化-变异。  ItemCount=RandByte()的部分会变异。理解向期望方向变异。
    model = GraphModel()
    model.connect(COTP_CR_TEMPLATE)
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)
    #以上调用KITTY框架中模糊测试的模块
    s7comm_target = TcpTarget(
        name='s7comm target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])#模糊测试主机等信息
    s7comm_target.set_expect_response(True)#打印响应包信息
    fuzzer = ServerFuzzer()#调用模糊测试分析器
    fuzzer.set_interface(WebInterface(port=26001))
    fuzzer.set_model(model)#设置调用KITTY框架中模糊测试的模块
    fuzzer.set_target(s7comm_target)#设置模糊测试主机
    fuzzer.set_delay_between_tests(0.1)#设置两侧测试延迟
    fuzzer.start()#运行调用KITTY框架中模糊测试的模块
    fuzzer.stop()


if __name__ == '__main__':
    # ip
    ip = get_net()[0]
    interface_name = get_net()[1]

    params = {'FUZZ_COUNT': 1,
              'DELAY': 0,
              'TARGET_IP': ip,
              'TIME_OUT': 2,
              'JOB_ID': '701',
              'INTERFACE': interface_name,
              }
    fuzz(params)
