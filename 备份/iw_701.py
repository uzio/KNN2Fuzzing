# coding:utf-8
import pymongo
from get_inet import get_net # TODO
from kitty.model import Template
from kitty.interfaces import WebInterface
from kitty.fuzzers import ServerFuzzer
from kitty.model import GraphModel
from katnip.targets.tcp import TcpTarget
from katnip.model.low_level.scapy import *
from protocols.cotp import *
from protocols.s7comm import *

RANDSEED = int(RandShort())

INFO = {
    'title': 'Data write时，Parameter中ItemCount=0x76 ',
    'des': 'Data write时，Parameter中ItemCount=0x76',
   'id':   'beta_1',
    'type': '1',
    'creator': 'uzio',
    'create_time': '06/16/2021',
    'protocol':'siemens'
}


def fuzz(params):
    SRC_TSAP = '\x01\x00'
    DST_TSAP = '\x01\x02'
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
                                                            ItemCount= RandByte(),#0x76,
                                                            Items=S7WriteVarItemsReq(
                                                            ItemCount=0x0003,
                                                            BlockNum=0x0001)),
                                                        Data=S7WriteVarDataItemsReq(
                                                            TransportSize = 0x05,
                                                            Data = '\x01\x02\x16'
                                                        )
                                                    )
    # TODO 
    # READ_SZL_PACKET["S7Header"].show()
    # print repr_hex(str(READ_SZL_PACKET)) # 报文转为字节流
    # print("++++++")
    #
    READ_SZL_TEMPLATE = Template(name='Data write时，Parameter中ItemCount=0x76', fields=[
        ScapyField(READ_SZL_PACKET, name='read szl', fuzzable=True, fuzz_count=params['FUZZ_COUNT']),
    ])
    model = GraphModel()
    model.connect(COTP_CR_TEMPLATE)
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)
    s7comm_target = TcpTarget(name='s7comm target', host=params['TARGET_IP'], port=102, timeout=params['TIME_OUT'])
    s7comm_target.set_expect_response(True)
    fuzzer = ServerFuzzer()
    fuzzer.set_interface(WebInterface(port=26001))
    fuzzer.set_model(model)
    fuzzer.set_target(s7comm_target)
    fuzzer.set_delay_between_tests(0.1)
    fuzzer.start()
    # fuzzer.stop()

if __name__ == '__main__':
      # ip
    ip = get_net()[0]
    interface_name = get_net()[1]
    
    params={'FUZZ_COUNT':2,
            'DELAY':0,
            'TARGET_IP':ip,
            'TIME_OUT':2,
            'JOB_ID':'701',
            'INTERFACE':interface_name,
            }
    fuzz(params)

