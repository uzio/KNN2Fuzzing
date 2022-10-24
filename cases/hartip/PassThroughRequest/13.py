# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.udp import UdpTarget
from katnip.model.low_level.scapy import *
from protocols.hart_ip import *

RANDSEED = int(RandShort())

INFO = {
    'title':'hart_IP Pass Through request时，模糊 CheckSum',
    'des':  'hart_IP Pass Through request时，模糊 CheckSum',
    'id':   '1',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/27/2019',
    'protocol':'hartip'
}

def fuzz(params):

    Packet = hart_IP_header(MessageID=0x03,MessageLength=0x0011)/\
             hart_IP_PassBody(CheckSum=RandByte())
    template = Template(name='hart_IP Pass Through request时，模糊 CheckSum', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    modbus_target = UdpTarget(name='hart_ip target', host= params['TARGET_IP'], port=5094, timeout=params['TIME_OUT'])
    modbus_target.set_expect_response(False)
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_target(modbus_target)
    fuzzer.set_delay_between_tests(params['DELAY'])
    fuzzer.set_skip_env_test(True)
    fuzzer.start()
    fuzzer.stop()

if __name__ == '__main__':
    params={'FUZZ_COUNT':1,
            'DELAY':1,
            'TARGET_IP':'77.234.110.177',
            'TIME_OUT':5,
            }
    fuzz(params)
