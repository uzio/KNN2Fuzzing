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
    'title': 'IEC/ISO 61850 MMS协议 Init Request类型报文Proposed DataStructure Nesting Level字段',
    'des':  'Proposed DataStructure Nesting Level字段控制在MMS协议中Init Request报文最多能够嵌套多少层',
    'id':   '1',
    'type': '1',
    'creator': 'shaoshuai',
    'create_time': '05/07/2019',
    'protocol': 'mms'
}

def fuzz(params):
    session_present_acs_data = [
        0x0d, 0xb3, 0x05, 0x06, 0x13, 0x01, 0x00, 0x16,
        0x01, 0x02, 0x14, 0x02, 0x00, 0x02, 0x33, 0x02,
        0x00, 0x01, 0x34, 0x02, 0x00, 0x02, 0xc1, 0x9d,
        0x31, 0x81, 0xa3, 0xa0, 0x03, 0x80, 0x01, 0x01,
        0xa2, 0x81, 0x92, 0x80, 0x02, 0x07, 0x80, 0x81,
        0x04, 0x00, 0x00, 0x00, 0x01, 0x82, 0x04, 0x00,
        0x00, 0x00, 0x02, 0xa4, 0x23, 0x30, 0x0f, 0x02,
        0x01, 0x01, 0x06, 0x04, 0x52, 0x01, 0x00, 0x01,
        0x30, 0x04, 0x06, 0x02, 0x51, 0x01, 0x30, 0x10,
        0x02, 0x01, 0x03, 0x06, 0x05, 0x28, 0xca, 0x22,
        0x02, 0x01, 0x30, 0x04, 0x06, 0x02, 0x51, 0x01,
        0x88, 0x02, 0x06, 0x00, 0x61, 0x60, 0x30, 0x5e,
        0x02, 0x01, 0x01, 0xa0, 0x59, 0x60, 0x57, 0x80,
        0x02, 0x07, 0x80, 0xa1, 0x07, 0x06, 0x05, 0x28,
        0xca, 0x22, 0x01, 0x01, 0xa2, 0x04, 0x06, 0x02,
        0x29, 0x02, 0xa3, 0x03, 0x02, 0x01, 0x02, 0xa6,
        0x04, 0x06, 0x02, 0x29, 0x01, 0xa7, 0x03, 0x02,
        0x01, 0x01, 0xbe, 0x32, 0x28, 0x30, 0x06, 0x02,
        0x51, 0x01, 0x02, 0x01, 0x03, 0xa0, 0x27, 0xa8,
        0x25
    ]  # ISO 8327 session protocol 以及 ISO 8823 presentation protocol 以及 ISO 8650-1 Association Control Service

    init_request_detail = {
        0x80, 0x01, 0x01, 0x81, 0x03, 0x05, 0xfb, 0x00,
        0x82, 0x0c, 0x03, 0x6e, 0x1d, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x64, 0x00, 0x01, 0x98
    }

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
    mms_initiate_request = MMSInitiateRequestPdu(localDetailCalling=32000,
                                                 proposedMaxServOutstandingCalling=20,
                                                 proposedMaxServOutstandingCalled=20,
                                                 proposedDataStructureNestingLevel=RandInt())
    INIT_REQUEST_PACKET = TPKT() / \
                          COTPDT(EOT=1) / \
                          Raw(bytearray(session_present_acs_data)) / \
                          MMS(PDU=mms_initiate_request) / \
                          Raw(bytearray(init_request_detail))
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
    fuzzer.set_delay_between_tests(1)
    fuzzer.start()
    fuzzer.stop()


if __name__ == '__main__':

    params={'FUZZ_COUNT':2,
            'DELAY':1,
            'TARGET_IP':'192.168.1.150',
            'TIME_OUT':2,
            }
    fuzz(params)

