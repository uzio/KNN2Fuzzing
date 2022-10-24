# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import *
from protocols.modbus_tcp import *

RANDSEED = int(RandShort())

INFO = {
    'title':'读取错误的线圈地址',
    'des':  '线圈的地址范围为1-2000(0x07D0)，随机几个不在此范围内的地址，ReferenceNumber模糊化',
    'id':   '1',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/11/2019',
    'protocol':'modbus'
}

def fuzz(params):

    Packet = ModbusHeaderRequest(func_code=0x01, unit_id=0x01) / ReadCoilsRequest(
        ReferenceNumber=RandShort(),BitCount=RandChoice(0x07D0,0x07D0,0x07ff,0x08D0,0x0AD0,0x0ED0,0xffff))
    template = Template(name='读取错误的线圈地址', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    modbus_target = TcpTarget(name='modbus target', host= params['TARGET_IP'], port=502, timeout=params['TIME_OUT'])
    modbus_target.set_expect_response(True)
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_target(modbus_target)
    fuzzer.set_delay_between_tests(params['DELAY'])
    fuzzer.set_skip_env_test(True)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':
    params={'FUZZ_COUNT':2,
            'DELAY':1,
            'TARGET_IP':'192.168.1.173',
            'TIME_OUT':2,
            }
    fuzz(params)

