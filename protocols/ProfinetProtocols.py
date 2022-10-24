#!/usr/bin/env python
from scapy.all import *

#Profinet Precision Transparent Clock Protocol
class ProfinetPTCP(Packet):
    name = "Profinet Precision Transparent Clock Protcol"
    fields_desc=[ BitFieldLenField("Padding", 0, 96), #12 bytes padding
                 XShortField("SequenceID", 0xb7a0),
                 XShortField("Padding2",0x0000), #2 bytes padding
                 XIntField("Delay1ns",0x00000003),
                 XShortField("TLVHeader",0x0c06),
                 BitFieldLenField("PortMACAddress",0x06d5e4c87c15, 48),
                 XShortField("TLVHeader2",0x0000)]

#in an identity request the destination mac has to be Multicast (01-0e-cf-00-00-00)!
class DCPIdentityRequest(Packet):
    name = "DCP Identity Request"
    fields_desc=[ XByteField("ServiceID",0x05), #5=Identify
                 XByteField("ServiceType",0x00),
                 XIntField("Xid",0xff7d2f6b),
                 XShortField("Reserved",0x0801),
                 XShortField("DCPDataLength",0x0010),
                 XByteField("Option",0x02), #2=Device Properties
                 XByteField("Suboption",0x02), #2=Name of Station
                 XShortField("DCPBlockLength", 0x0b), #gives length of following field
                 BitFieldLenField("NameOfStation",0x16bddabc23e188ce, 88), #fix for 11 characters
                 XByteField("Padding", 0x00)
                  ]

class writeRequest(Packet):
    name = "Profinet IO Write Request"
    fields_desc=[ ByteField("VLAN", 4),
                 XByteField("Ethertype",0x0800),
                 ShortField("IPUDP", 28),
                 ByteField("RPC", 80),
                 ByteField("NDR", 20),
                 ByteField("WriteBlock", 64),
                 ByteField("WriteData", None),
                 ByteField("FCS", 4)  ]

#RT_CLASS_1 Frame: Unsynchronized communication within one subnet
class ProfinetAcyclicRealTime(Packet):
    name = "Profinet Acyclic Real-Time"
    fields_desc=[ XShortField("FrameID", 0xfefe)]


#RT_CLASS_2 Frame: Synchronized communication within one subnet
#ProfinetCyclicRealTimeFrame has to be after Ether-Frame
class ProfinetCyclicRealTimeFrame(Packet):
    name = "Profinet Real-Time-Frame"
    fields_desc=[ XShortField("FrameID", 0x0), #0x8000 (SPS) or 0x8061 (robot)
                XByteField("IOxS", 0x80), #good
                BitFieldLenField("Data", 0, 400), #a 51 bytes field for Data
                ShortField("CycleCounter", 0),
                XByteField("DataStatus", 0x35),  #0x35: Valid and Primary, OK and Run
                XByteField("TransferStatus", 0x00) ] #ok


#ProfinetAlarmFrame has to be after Ether-Frame and ProfinetAcyclicRealTime-Frame
class ProfinetAlarmFrame(Packet):
    name = "Profinet Alarm Frame"
    fields_desc=[ XShortField("AlarmDstEndpoint",0x0001),
                XShortField("AlarmSrcEndpoint",0x0001),
                XByteField("PDUType",0x04),
                XByteField("AddFlags",0x00),
                XShortField("SendSeqNum",0xbb04),
                XShortField("AckSeqNum",0xbb04),
                XShortField("VarPartLen",0x0004),
                XByteField("ErrorCode",0x81),
                XByteField("ErrorDecode",0x81),
                XByteField("ErrorCode1",0x07),
                XByteField("ErrorCode2",0x6e)
                  ]

