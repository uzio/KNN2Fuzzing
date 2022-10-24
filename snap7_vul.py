# coding:utf-8
"""
测试用例验证程序snap7 server_demo
"""
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from kitty.fuzzers import ServerFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import ScapyField
from protocols.cotp import TPKT,COTPCR,COTPDT #放弃使用*进行默认引入
from protocols.s7comm import RandShort,S7Header,S7SetConParameter,S7WriteVarParameterReq,RandByte,S7WriteVarItemsReq #放弃使用*进行默认引入

RANDSEED = int(RandShort())

INFO = {
    'title': 'Data write时，模糊Parameter中Item中的TransportSize ',
    'des': 'Data write时，模糊Parameter中Item中的TransportSize ',
    'id': '1',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/11/2019',
    'protocol':'siemens'
}

def fuzz(params):
    p1 = TPKT() / COTPCR()
    p2 = TPKT() / COTPDT() / S7Header(ROSCTR="Job", Parameters=S7SetConParameter())
    p3 = TPKT() / COTPDT() / S7Header(ROSCTR="Job", Parameters=S7WriteVarParameterReq(
        Function=0x5,
        ItemCount=RandByte(),
        Items=[S7WriteVarItemsReq()]
    ))

    COTP_CR_TEMPLATE = Template(name='cotp cr template', fields=[
        ScapyField(p1, name='cotp cr', fuzzable=False),
    ])

    SETUP_COMM_PARAMETER_TEMPLATE = Template(name='setup comm template', fields=[
        ScapyField(p2, name='setup comm', fuzzable=False),
    ])

    READ_SZL_TEMPLATE = Template(multiple=100, name='Data write时，模糊Parameter中Item中的TransportSize', fields=[
        ScapyField(p3, name='read szl', fuzzable=True, fuzz_count=params['FUZZ_COUNT']),
    ])
    model = GraphModel()
    model.connect(COTP_CR_TEMPLATE)
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)
    s7comm_target = TcpTarget(name='s7comm target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])
    s7comm_target.set_expect_response(False)
    fuzzer = ServerFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_skip_env_test()
    fuzzer.set_target(s7comm_target)
    fuzzer.set_delay_between_tests(1)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print(u'请输入./snap7_vul.py [IP]')
        sys.exit()

    params = {'FUZZ_COUNT': 15,
              'DELAY': 0,
              'TARGET_IP': sys.argv[1],
              'TIME_OUT': 2,
              }
    fuzz(params)

