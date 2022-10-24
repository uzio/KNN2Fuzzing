# coding:utf-8
import pymongo
from get_inet import get_net
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from kitty.interfaces import WebInterface# kitty自带web界面
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import ScapyField
from protocols.cotp import *
from protocols.s7comm import *

RANDSEED = int(RandShort())

INFO = {
    'title':'Data Read时，模糊 Parameter中 Item部分 Parameter Length',
    'des':  'Data Read时，模糊 Parameter中 Item部分 Parameter Length ',
    'id':   '1',
    'type': '1',
    'creator': 'sunzeen',
    'create_time': '04/22/2021',
    'protocol':'siemens'
}

def fuzz(params):
    '''模糊测试'''
    SRC_TSAP = '\x01\x00'# 源传输服务访问点 COTP CR请求的参数
    DST_TSAP = '\x01\x01'# 目标传输服务访问点 COTP CR请求的参数
    COTP_CR_PACKET = TPKT() / COTPCR()
    COTP_CR_PACKET.Parameters = [COTPOption() for i in range(3)]
    COTP_CR_PACKET.PDUType = "CR"  # Connect Request
    COTP_CR_PACKET.Parameters[0].ParameterCode = "tpdu-size"
    COTP_CR_PACKET.Parameters[0].Parameter = "\x0a"
    COTP_CR_PACKET.Parameters[1].ParameterCode = "src-tsap"
    COTP_CR_PACKET.Parameters[1].Parameter = SRC_TSAP
    COTP_CR_PACKET.Parameters[2].ParameterCode = "dst-tsap"
    COTP_CR_PACKET.Parameters[2].Parameter = DST_TSAP

    COTP_CR_TEMPLATE = Template(name='cotp cr template', fields=[
        ScapyField(COTP_CR_PACKET, name='cotp cr', fuzzable=False),
    ])

    SETUP_COMM_PARAMETER_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ROSCTR="Job", Parameters=S7SetConParameter())
    SETUP_COMM_PARAMETER_TEMPLATE = Template(name='setup comm template', fields=[
        ScapyField(SETUP_COMM_PARAMETER_PACKET, name='setup comm', fuzzable=False),
    ])


    READ_SZL_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ProtocolId=0x32,ROSCTR="Job",
                                                        Parameters=S7ReadVarParameterReq(
                                                            Items=S7ReadVarItemsReq(
                                                                ParameterLength=RandByte(),
                                                                BlockNum=0x0001, # DB number choice
                                                                Address=0x000020 # Address Start
                                                            )),
                                                        )

    READ_SZL_TEMPLATE = Template(name='Data Read时，模糊 Parameter中 Item部分 Parameter Length', fields=[
        ScapyField(READ_SZL_PACKET, name='read szl', fuzzable=True, fuzz_count=params['FUZZ_COUNT']),
    ])
    model = GraphModel()
    model.connect(COTP_CR_TEMPLATE)
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)
    s7comm_target = TcpTarget(name='s7comm target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])
    s7comm_target.set_expect_response(True)
    fuzzer = ICSFuzzer(params)
    # fuzzer.set_interface(EmptyInterface())# 定义fuzzer使用的交互界面
    fuzzer.set_interface(WebInterface(port=26000))# 定义fuzzer使用的交互界面为kitty自带web界面
    fuzzer.set_model(model)
    fuzzer.set_skip_env_test()
    fuzzer.set_target(s7comm_target)
    fuzzer.set_delay_between_tests(0.1)# 定义每个测试用例发送之间的延迟
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':
    # mongodb
    # mongo=pymongo.MongoClient()
    # db=mongo["fuzz"]
    # collection=db.get_collection("jobs")
    # fields={"params.JOB_ID":True}
    # job=collection.find_one({"title" : "56"},fields)
    # ip
    ip = get_net()[0]
    interface_name = get_net()[1]
    
    params={'FUZZ_COUNT':2,
            'DELAY':1,
            'TARGET_IP':ip,
            'TIME_OUT':2,
            'JOB_ID':"6_17",#job['params']['JOB_ID'],
            'INTERFACE':interface_name,
            }
    fuzz(params)

