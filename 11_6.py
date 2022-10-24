# coding:utf-8
import time
import math
import protocols.s7comm
import Pretreatment as Pre#
from InitSet import InitSet #
from get_inet import get_net  #

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
    'title': 'Data write fuzzing test ',
    'des':  'Data write fuzzing test ',
    'id':   'beta_1',
    'type': '1',
    'creator': 'uzio',
    'create_time': '10/26/2021',
    'protocol': 'siemens'
}

def fuzz(params):
    SRC_TSAP = params['SRC_TSAP']# '\x01\x00'  # 设备地址 发送方
    DST_TSAP = params['DST_TSAP']#'\x01\x02'  # 设备地址 接受方
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
                                                                    Parameters=S7SetConParameter(
                                                                        PDULength=0x00f0,
                                                                        MaxAmQcalling=0x0004,
                                                                        MaxAmQcalled=0x0004,
                                                                    ))

    SETUP_COMM_PARAMETER_TEMPLATE = Template(name='setup comm template', fields=[
        ScapyField(SETUP_COMM_PARAMETER_PACKET,
                   name='setup comm', fuzzable=False),
    ])      # 设置连接。第一次连接，获取许可，EOT=1没有触发1568漏洞 # 第二次连接，正式连接

    READ_SZL_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ProtocolId=0x32, ROSCTR="Job", # S7comm协议
                                                            Parameters=S7WriteVarParameterReq(  # S7写入参数请求包
                                                                Function=RandEnumKeys(S7_JB_FUNCTION),#RandByte(), # 0x05写入 # 0x29 CPU stop
                                                                Items=S7WriteVarItemsReq(
                                                                    BitAddress=RandShort()*RandByte(), # 包含所选存储区中寻址变量的偏移量
                                                                    VariableSpecification=0x12,#RandByte(), #结构的主要类型 对于读/写消息，它总是具有值0x12，代表变量规范
                                                                    AREAType=RandEnumKeys(S7_AREA_TYPE),#RandByte(132), # 寻址变量的存储区域， 0x84为数据库 0x80为 Direct peripheral access    #TODO 
                                                                    BlockNum=RandShort())),  # DB块号
                                                            Data=S7WriteVarDataItemsReq(
                                                                ReturnCode=RandByte(),
                                                                TransportSize=0x07,  # 0x07 Real access, len is in bytes
                                                                Data=RandTermString(RandNum(1,20),'\x00'),  # 随机生成数据，RandNum()随机指定长度 等价于random.randint(1,20)
                                                            )
                                                            )  # 提交SNAP工作内容，发送出的数据包
    
    # 设置筛选关键字
    InitSet.setFilterKey(READ_SZL_PACKET,READ_SZL_PACKET)

    READ_SZL_TEMPLATE = Template(name='Data write时，Parameter中ItemCount=0x76', multiple=6, fields=[
        ScapyField(READ_SZL_PACKET, name='read szl', # 处理数据包的基础方法
                   fuzzable=True, fuzz_count=params['FUZZ_COUNT']),
    ])  # 发送数据包作为模板，对该模板进行模糊化变异。  ItemCount=RandByte()的部分会变异。TODO 向期望方向变异。
    model = GraphModel()
    model.connect(COTP_CR_TEMPLATE)
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)
    #以上调用KITTY框架中模糊测试的模块
    s7comm_target = TcpTarget(
        name='s7comm target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])#模糊测试主机等信息
    s7comm_target.set_expect_response(True)#打印响应包信息
    fuzzer = ServerFuzzer()#调用模糊器
    fuzzer.set_interface(WebInterface(port=26001))
    fuzzer.set_model(model)#设置调用KITTY框架中模糊测试的模块
    fuzzer.set_target(s7comm_target)#设置模糊测试主机
    fuzzer.set_delay_between_tests(0)#设置两次测试间延迟
    fuzzer.start()#运行调用KITTY框架中模糊测试的模块
    fuzzer.stop()


if __name__ == '__main__':
    # ip
    ip = get_net()[0]
    interface_name = get_net()[1]

    rack=0  #  cpu rack
    slot=1  # cpu slot

    params = {'FUZZ_COUNT': 1000,
            'DELAY': 0,
            'TARGET_IP': ip,
            'SRC_TSAP':'\x01\x00',
            'DST_TSAP':'\x01'+struct.pack('B', rack * 0x20 + slot),
            'TIME_OUT': 2,
            'INTERFACE': interface_name,
            }
    fuzz(params)
