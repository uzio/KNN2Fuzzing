# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import *
from protocols.cip import *
from protocols.enip_tcp import *

RANDSEED = int(RandShort())

INFO = {
    'title': '通过EtherNet/IP获取PLC模糊数量后的接口',
    'des':  '通过Ethernet/IP的List Identity来获取目标PLC接口，模糊目标接口数量',
    'id':   '1',
    'type': '1',
    'creator': 'shaoshuai',
    'create_time': '04/11/2019',
    'protocol': 'ethernet/ip'
}


def fuzz(params):
    Packet = ENIP_TCP(command_id=0x64) / scapy_all.Raw(RandString(2))
    template = Template(name='ethernet ip request', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    target = TcpTarget(name='ethernet ip target', host=params['TARGET_IP'], port=44818, timeout=params['TIME_OUT'])
    target.set_expect_response(True)
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_target(target)
    fuzzer.set_delay_between_tests(params['DELAY'])
    fuzzer.set_skip_env_test(True)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':
    params = {'FUZZ_COUNT': 2,
              'DELAY': 1,
              'TARGET_IP': '192.168.1.173',
              'TIME_OUT': 2,
              }
    fuzz(params)

