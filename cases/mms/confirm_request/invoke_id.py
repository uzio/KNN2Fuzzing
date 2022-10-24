# coding:utf-8
from kitty.model import Template
from kitty.interfaces.base import EmptyInterface
from ics_fuzzer import ICSFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import ScapyField
from protocols.cotp import *
from protocols.mms import *

RANDSEED = int(RandShort())

INFO = {
    'title': 'IEC/ISO 61850 MMS协议Confirmed Request类型报文Invoke ID字段',
    'des':  '在MMS协议中Confirmed Request报文Invoke ID字段标示当前会话ID',
    'id':   '1',
    'type': '1',
    'creator': 'shaoshuai',
    'create_time': '05/07/2019',
    'protocol': 'mms'
}


def fuzz(params):
    session_present_acs_data = [
        0x01, 0x00, 0x01, 0x00, 0x61, 0x0e, 0x30,
        0x0c, 0x02, 0x01, 0x03, 0xa0, 0x07,
    ]  # ISO 8327 session protocol 以及 ISO 8823 presentation protocol 以及 ISO 8650-1 Association Control Service

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
    mms_confirm_request = MMSConfirmedRequestPdu(invokeID=RandInt())
    INIT_REQUEST_PACKET = TPKT() / \
                          COTPDT(EOT=1) / \
                          Raw(bytearray(session_present_acs_data)) / \
                          MMS(PDU=mms_confirm_request)

    INIT_REQUEST_PACKET_TEMPLATE = Template(name='init request template', fields=[
        ScapyField(INIT_REQUEST_PACKET, name='init request', fuzzable=True, fuzz_count=params['FUZZ_COUNT']),
    ])

    model = GraphModel()
    model.connect(COTP_CR_TEMPLATE)
    model.connect(COTP_CR_TEMPLATE, INIT_REQUEST_PACKET_TEMPLATE)
    target = TcpTarget(name='target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])
    target.set_expect_response(True)
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_skip_env_test()
    fuzzer.set_target(target)
    fuzzer.set_delay_between_tests(params['DELAY'])
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':

    params={'FUZZ_COUNT':2,
            'DELAY':1,
            'TARGET_IP': '192.168.1.150',
            'TIME_OUT': 2,
            }
    fuzz(params)

