# coding:utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import ScapyField
from protocols.cotp import *
from protocols.s7comm import *

RANDSEED = int(RandShort())

INFO = {
    'title': 'Data write时，模糊Parameter中Function ',
    'des': 'Data write时，模糊Parameter中Function ',
    'id': '1',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '04/11/2019',
    'protocol': 'siemens'
}


def fuzz(params):
    SRC_TSAP = '\x01\x00'
    DST_TSAP = '\x01\x01'
    COTP_CR_PACKET = TPKT() / COTPCR()
    COTP_CR_PACKET.Parameters = [COTPOption() for i in range(3)]
    COTP_CR_PACKET.PDUType = "CR"  # Connect Request
    COTP_CR_PACKET.Parameters[0].ParameterCode = "tpdu-size"
    COTP_CR_PACKET.Parameters[0].Parameter = "\x0a"
    COTP_CR_PACKET.Parameters[1].ParameterCode = "src-tsap"
    COTP_CR_PACKET.Parameters[1].Parameter = SRC_TSAP
    COTP_CR_PACKET.Parameters[2].ParameterCode = "dst-tsap"
    COTP_CR_PACKET.Parameters[2].Parameter = DST_TSAP

    COTP_CR_TEMPLATE = Template(name='cotp cr template', fields=[
        ScapyField(COTP_CR_PACKET, name='cotp cr', fuzzable=False),
    ])

    SETUP_COMM_PARAMETER_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ROSCTR="Job", Parameters=S7SetConParameter())
    SETUP_COMM_PARAMETER_TEMPLATE = Template(name='setup comm template', fields=[
        ScapyField(SETUP_COMM_PARAMETER_PACKET, name='setup comm', fuzzable=False),
    ])

    READ_SZL_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ProtocolId=0x32, ROSCTR="Job",

                                                        Parameters=S7WriteVarParameterReq(
                                                            Function=RandByte(),
                                                            Items=S7WriteVarItemsReq()),
                                                        Data=S7WriteVarDataItemsReq()
                                                        )

    READ_SZL_TEMPLATE = Template(name='Data write时，模糊Parameter中Function', fields=[
        ScapyField(READ_SZL_PACKET, name='read szl', fuzzable=True, fuzz_count=params['FUZZ_COUNT']),
    ])
    model = GraphModel()
    model.connect(COTP_CR_TEMPLATE)
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)
    s7comm_target = TcpTarget(name='s7comm target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])
    s7comm_target.set_expect_response(True)
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_skip_env_test()
    fuzzer.set_target(s7comm_target)
    fuzzer.set_delay_between_tests(1)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':
    params = {'FUZZ_COUNT': 2,
              'DELAY': 1,
              'TARGET_IP': '192.168.1.188',
              'TIME_OUT': 2,
              }
    fuzz(params)

