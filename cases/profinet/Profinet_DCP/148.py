# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.eth import EthTarget
from katnip.model.low_level.scapy import *
from protocols.ProfinetProtocols import *

RANDSEED = int(RandShort())
INFO = {
    'title':'Profinet DCP 模糊 Service ID',
    'des':  'Profinet DCP 模糊 Service ID',
    'id':   '1',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '05/04/2019',
    'protocol':'profinet'
}

def fuzz(params):
    Packet = ProfinetAcyclicRealTime(FrameID=0xfefe)/DCPIdentityRequest(ServiceID=RandByte())
    template = Template(name='Profinet DCP 模糊 Service ID', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    modbus_target = EthTarget(name='profinet target',targetIP=params['TARGET_IP'])
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
    params={'FUZZ_COUNT':2,
            'DELAY':1,
            'TARGET_IP':'192.168.1.188',
            'TIME_OUT':2,
            }
    fuzz(params)
