# coding=utf-8
from scapy.packet import *
from scapy.fields import *

#hart_IP  header部分
class  hart_IP_header(Packet):
    fields_desc = [
       ByteField("Version",0x01),
       ByteField("MessageType", 0x00),
       ByteField("MessageID", 0x00),
       ByteField("Status", 0x00),
       ShortField("SequenceNumber", 0x0002),
       ShortField("MessageLength", 0x000d)
    ]


class  hart_IP_Body(Packet):
    fields_desc = [
       ByteField("hostType",0x01),
       IntField("InactivityCloseTimer", 0x00007530),
    ]

class  hart_IP_PassBody(Packet):
    fields_desc = [
       ByteField("FrameType",0x82),
       StrFixedLenField("LongAddress","\x26\x4e\x00\x00\xd2",5),
       ByteField("Commend",0x00),
       ByteField("Length",0x00),
       ByteField("CheckSum",0x38)
    ]
