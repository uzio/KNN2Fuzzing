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
    'title':'写文件记录，模糊总字节数 ByteCount',
    'des':  '写文件记录，模糊总字节数 ByteCount',
    'id':   '2',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/11/2019',
    'protocol':'modbus'
}

def fuzz(params):

    Packet = ModbusHeaderRequest(func_code=0x15, unit_id=0x01) / WriteFileRecordRequest(
        ByteCount=RandByte())
    template = Template(name='写文件记录，模糊总字节数 ByteCount', fields=[
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
