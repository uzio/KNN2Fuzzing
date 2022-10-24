# coding=utf-8
from kitty.model import Template
from kitty.interfaces import WebInterface
from kitty.fuzzers import ServerFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import *
from protocols.modbus_tcp import *

RANDSEED = int(RandShort())

INFO = {
    'title':'写多个线圈',
    'des':  '模糊ReferenceNumber',
    'id':   '1',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/11/2019',
    'protocol':'modbus'
}

def fuzz(params):

    Packet = ModbusHeaderRequest(func_code=0x0f, unit_id=0x01) / WriteMultipleCoilsRequest(
        ReferenceNumber=RandShort())
    template = Template(name='写多个线圈', fields=[
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
    fuzzer = ServerFuzzer()#调用模糊器
    fuzzer.set_interface(WebInterface(port=26001))
    fuzzer.set_model(model)
    fuzzer.set_target(modbus_target)
    fuzzer.set_delay_between_tests(params['DELAY'])
    fuzzer.set_skip_env_test(True)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':
    params = {'FUZZ_COUNT': 2,
              'DELAY': 1,
              'TARGET_IP': '0.0.0.0',
              'TIME_OUT': 2,
              }
    fuzz(params)

