# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.icmp import EthTarget
from katnip.model.low_level.scapy import *
from scapy.layers.inet import IP, ICMP

RANDSEED = int(RandShort())
INFO = {
    'title': 'ICMP协议 sequence 字段模糊',
    'des':  '在ICMP协议中，sequence字段是16位，指定IP承载的运输层协议，此用例针对这个字段进行模糊测试',
    'id':   '1',
    'type': '1',
    'protocol': 'icmp',
    'creator': 'liuyongpan',
    'create_time': '04/11/2019'
}


def fuzz(params):
    packet = IP(dst=params['TARGET_IP'], proto=1)/ICMP(seq=RandShort())
    template = Template(name='icmp fuzz', fields=[
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
