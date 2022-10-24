#! /usr/bin/env python
# coding:utf-8
# Author: yongpan Liu
from scapy.all import conf
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import UDP


# Omron Header
class OMRON_Header(Packet):
    fields_desc = [
        XByteField("OMRON_ICF_Field", 0x80),
        XByteField("Reserved", 0x00),
        XByteField("Gateway_Count", 0x02),
        XByteField("Destination_network_address", 0x00),
        XByteField("Destination_node_address", 0x00),
        XByteField("Destination_unit_address", 0x00),
        XByteField("Source_network_address", 0x00),
        XByteField("Source_node_number", 0x22),
        XByteField("Source_unit_address", 0x00),
        XByteField("Service_ID", 0x01),
        XShortField("Command_code", 0x0102),
    ]


#Memory Area Read
class MemoryReadCommand_Data(Packet):
    fields_desc = [
        XByteField("Memory_Area_Code", 0x82),
        XShortField("Beginning_Address", 0x0000),
        XByteField("Beginning_Address_bits", 0x00),
        XShortField("Number_of_items", 0x000c),
    ]

#Memory Area Write
class MemoryWriteCommand_Data(Packet):
    fields_desc = [
        XByteField("Memory_Area_Code", 0x82),
        XShortField("Beginning_Address", 0x0000),
        XByteField("Beginning_Address_bits", 0x00),
        XShortField("Number_of_items", 0x0002),
        XIntField("Command_Data",0x000c0022)#Command_Data的长度由Number_of_items决定
    ]

