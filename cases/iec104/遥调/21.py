# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import *
from protocols.iec104 import *


RANDSEED = int(RandShort())

INFO = {
    'title': 'IEC 104 遥调，模糊 OA',
    'des':   'IEC 104 遥调，模糊 OA ',
    'id':   '1',
    'type': '1',
    'creator': 'lyp',
    'create_time': '04/27/2019',
    'protocol': 'iec104'
}

def fuzz(params):

    Setup_Packet =IEC_Apci_ParameterRsq(ApduLen=0x04,Tx=0x0700)
    Setup = Template(name='IEC 104 主站发出连接请求报文', fields=[
        ScapyField(Setup_Packet,
                   name='template',
                   fuzzable=False,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])

    Packet =IEC_Apci_ParameterRsq()/IEC_Asdu_ParameterRsq(OA=RandByte())
    templete = Template(name='IEC 104 遥调，模糊 OA', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])

    model = GraphModel()
    model.connect(Setup)
    model.connect(Setup,templete)
    target = TcpTarget(name='ethernet ip target', host=params['TARGET_IP'], port=2404, timeout=params['TIME_OUT'])
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
    params = {'FUZZ_COUNT': 2,
              'DELAY': 1,
              'TARGET_IP': '188.38.143.185',
              'TIME_OUT': 5,
              }
    fuzz(params)

