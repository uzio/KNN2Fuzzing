# coding:utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import ScapyField
from scapy.layers.inet import TCP
from scapy.all import RandShort

RANDSEED = int(RandShort())

INFO = {
    'title': 'TCP协议check sum字段风暴测试',
    'des':  '校验和字段即源端口是一个16位长度的字段，针对其大小，进行风暴测试',
    'id':   '1',
    'type': '1',
    'creator': 'shaoshuai',
    'create_time': '05/2/2019',
    'protocol': 'tcp'
}


def fuzz(params):
    packet = TCP(chksum=RandShort())
    template = Template(name='tcp sport fuzz', fields=[
        ScapyField(packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    target = TcpTarget(name='target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])
    target.set_expect_response(False)
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_skip_env_test()
    fuzzer.set_target(target)
    fuzzer.set_delay_between_tests(1)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':

    params={'FUZZ_COUNT':2,
            'DELAY':1,
            'TARGET_IP':'192.168.1.188',
            'TIME_OUT':2,
            }
    fuzz(params)

