# coding=utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import *
from protocols.dnp3 import *

RANDSEED = int(RandShort())

INFO = {
    'title':'dnp3 read File时，模糊 FileDataObject 中的 FileControlMode 字段',
    'des':  'dnp3 read File时，模糊 FileDataObject 中的 FileControlMode 字段',
    'id':   '1',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/27/2019',
    'protocol':'dnp3'
}

def fuzz(params):

    Packet = dnp3_ReadFileReq(FileDataObject=[dnp3_FileDataObject(FileControlMode=RandShort())])
    template = Template(name='dnp3 read File时，模糊 FileDataObject 中的 FileControlMode 字段', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])
    model = GraphModel()
    model.connect(template)
    modbus_target = TcpTarget(name='dnp3 target', host= params['TARGET_IP'], port=20000, timeout=params['TIME_OUT'])
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
            'TARGET_IP':'166.149.131.186',
            'TIME_OUT':5,
            }
    fuzz(params)
