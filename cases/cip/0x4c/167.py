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
    'title': 'CIP协议中获取不同长度的tag值',
    'des':  '通过Ethernet/IP的connect manager请求来获取目标PLC所有tag值，但是获取长度不同',
    'id':   '1',
    'type': '1',
    'creator': 'shaoshuai',
    'create_time': '04/11/2019',
    'protocol': 'cip'
}


def fuzz(params):
    cip_pkt = CIP(service=0x4c, path=CIP_Path.make(class_id=RandShort(), instance_id=RandShort()))
    cip_pkt /= CIP_ReqReadOtherTag(start=0, length=RandShort())
    cip_pkt = send_rr_cm_cip(cip_pkt)
    Packet = send_rr_cip(cip_pkt)
    template = Template(name='cip request', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    modbus_target = TcpTarget(name='cip target', host=params['TARGET_IP'], port=44818, timeout=params['TIME_OUT'])
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
    params = {'FUZZ_COUNT': 2,
              'DELAY': 1,
              'TARGET_IP': '192.168.1.189',
              'TIME_OUT': 2,
              }
    fuzz(params)

