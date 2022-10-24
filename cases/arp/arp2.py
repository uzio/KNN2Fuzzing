# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.arp import EthTarget
from katnip.model.low_level.scapy import *
from scapy.layers.l2 import ARP

RANDSEED = int(RandShort())
INFO = {
    'title': 'ARP协议风暴测试2',
    'des':  '在ARP协议中，针对广播域进行风暴测试',
    'id':   '1',
    'type': '1',
    'protocol': 'arp',
    'creator': 'shaoshuai',
    'create_time': '04/27/2019'
}


def fuzz(params):
    packet = ARP(pdst=params['TARGET_IP'], hwsrc='f0:18:98:4e:b8:a4', hwdst='ff:ff:ff:ff:ff:ff')
    template = Template(name='arp fuzz', fields=[
        ScapyField(packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    target = EthTarget(name='target', targetIP=params['TARGET_IP'])
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_target(target)
    fuzzer.set_delay_between_tests(params['DELAY'])
    fuzzer.set_skip_env_test(True)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':
    params={'FUZZ_COUNT': 2,
            'DELAY': 1,
            'TARGET_IP': '192.168.1.188',
            'TIME_OUT': 2,
            }
    fuzz(params)
