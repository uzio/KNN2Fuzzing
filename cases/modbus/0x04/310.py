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
    'title':'读输入寄存器时，丢弃长度字段',
    'des':  '读输入寄存器时，丢弃长度字段',
    'id':   '6',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/11/2019',
    'protocol':'modbus'
}

def fuzz(params):
    Packet = ModbusHeaderRequest(func_code=0x04, unit_id=0x01) / ReadInputRegistersRequest_v2(
        ReferenceNumber=RandShort())
    template = Template(name='读输入寄存器时，丢弃长度字段', fields=[
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
