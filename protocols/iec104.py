#! /usr/bin/env python
# coding:utf-8
# Author: yongpan Liu
from scapy.all import conf
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import TCP

class IEC_Apci_ParameterRsq(Packet):
    fields_desc = [
        ByteField("Start", 0x68),
        ByteField("ApduLen", 0x0e),
        ShortField("Tx",0x0200),
        ShortField("Rx", 0x0000),
    ]


class IEC_Asdu_ParameterRsq(Packet):
    fields_desc = [
        ByteField("TypeId", 0x01),
        ShortField("Unknow", 0x0101),
        ByteField("OA", 0x00),
        ShortField("Addr", 0x0100),
        IntField("IOA", 0x00000000),
    ]
