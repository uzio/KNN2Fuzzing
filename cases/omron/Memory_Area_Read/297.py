# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.udp import UdpTarget
from katnip.model.low_level.scapy import *
from protocols.omron_fins import *

RANDSEED = int(RandShort())

INFO = {
    'title':'Memory Area Read,模糊 Service_ID',
    'des':  'Memory Area Read,模糊 Service_ID',
    'id':   '2',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '05/04/2019',
    'protocol':'omron_fins'
}

def fuzz(params):

    Packet = OMRON_Header(Service_ID=RandByte())/MemoryReadCommand_Data()
    template = Template(name='Memory Area Read,模糊 Service_ID', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])


    model = GraphModel()
    model.connect(template)
    modbus_target = UdpTarget(name='modbus target', host= params['TARGET_IP'], port=9600, timeout=params['TIME_OUT'])
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
            'TARGET_IP':'192.168.1.189',
            'TIME_OUT':2,
            }
    fuzz(params)
