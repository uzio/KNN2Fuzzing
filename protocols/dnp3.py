# coding=utf-8
from scapy.packet import *
from scapy.fields import *

#DataChunks 部分
class  dnp3_DataChunks(Packet):
    fields_desc = [
       StrFixedLenField("Data_Chunk","\xe0\xc1\x19\x46\x03\x5b\x01\x28\x00\x1a\x00\x0e\x00\x00\x00\x00",16),
       ShortField("Data_Chunk_CHecksum",0x1cb9)
    ]

class dnp3_DataChunks_v1(Packet):
    fields_desc = [
        StrFixedLenField("Data_Chunk", "\x74",1),
        ShortField("Data_Chunk_CHecksum", 0x1dee)
    ]


#不知怎么动态调整ShortField 字段的长度，暂时固定住
class dnp3_DataChunks_v3(Packet):
    fields_desc = [
        StrFixedLenField("Data_Chunk", "\x74\x78\x74",3),
        ShortField("Data_Chunk_CHecksum", 0x5eda)
    ]


class dnp3_DataChunks_v10(Packet):
    fields_desc = [
        StrFixedLenField("Data_Chunk","\x80\x68\x69\x20\x74\x68\x65\x72\x65\x20",10),
        ShortField("Data_Chunk_CHecksum", 0x653d)
    ]

#FileDataObject 字段
class  dnp3_FileDataObject(Packet):
    fields_desc = [
       ByteField("QualiferField",0x5b),
       ByteField("NumberOfItems",0x01),
       #Object
       ShortField("Size",0x2800),
       ShortField("FileOffset",0x1a00),
       ShortField("FileLength",0x0e00),
       IntField("FileAuthenticationKey",0x00000000),
       ShortField("FileControlMode",0x0100),
       ShortField("FileMaxBlockSize",0x0004),
       ShortField("FileRequestIdentifier",0x0400),
       StrLenField("FileName",None)
     ]

#删除文件
class  dnp3_DeleteFileReq(Packet):
    fields_desc = [
        ShortField("Start_Bytes", 0x0564),
        XByteField("Length", 0x38),
        XByteField("Control", 0xc4),
        ShortField("Destination", 0x0400),
        ShortField("Source", 0x0300),
        ShortField("Data_link_Header_Checksum", 0xf731),
        # ByteField("Tansport_Control", 0xf0),
        PacketListField (
        "Data_Chunks",
        [dnp3_DataChunks(Data_Chunk="\xf0\xc1\x1b\x46\x03\x5b\x01\x2a\x00\x1a\x00\x10\x00\x00\x00\x00",Data_Chunk_CHecksum=0x3004),
         dnp3_DataChunks(Data_Chunk="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",Data_Chunk_CHecksum=0xffff),
         dnp3_DataChunks(Data_Chunk="\x00\x12\x00\x2e\x2f\x68\x65\x6c\x6c\x6f\x77\x6f\x72\x6c\x64\x2e",Data_Chunk_CHecksum=0xa42d),
         dnp3_DataChunks_v3(),
        ],
        dnp3_DataChunks,count_from=4),
        ByteField("Application_Control",0xc1),
        ByteField("Function_Code", 0x19),
        PacketListField("FileDataObject",[dnp3_FileDataObject()],dnp3_FileDataObject,count_from=1)
    ]



#读取文件
class  dnp3_ReadFileReq(Packet):
    fields_desc = [
        ShortField("Start_Bytes", 0x0564),
        XByteField("Length", 0x36),
        XByteField("Control", 0xc4),
        ShortField("Destination", 0x0400),
        ShortField("Source", 0x0300),
        ShortField("Data_link_Header_Checksum", 0xf2c0),
        PacketListField ("Data_Chunks",
        [
        dnp3_DataChunks(Data_Chunk="\xe0\xc1\x19\x46\x03\x5b\x01\x28\x00\x1a\x00\x0e\x00\x00\x00\x00",Data_Chunk_CHecksum=0xb91c),
        dnp3_DataChunks(Data_Chunk="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00",Data_Chunk_CHecksum=0x47e6),
        dnp3_DataChunks(Data_Chunk="\x04\x04\x00\x2e\x2f\x74\x65\x73\x74\x66\x69\x6c\x65\x2e\x74\x78",Data_Chunk_CHecksum=0xea02),
        dnp3_DataChunks_v1()
        ],
        dnp3_DataChunks,count_from=4),
        #decode('hex')
        ByteField("Application_Control",0xc1),
        ByteField("Function_Code", 0x19),
        PacketListField("FileDataObject",[dnp3_FileDataObject()],dnp3_FileDataObject,count_from=1)
    ]


#写入文件
class  dnp3_WriteFileReq(Packet):
    fields_desc = [
        ShortField("Start_Bytes", 0x0564),
        XByteField("Length", 0x1f),
        XByteField("Control", 0xc4),
        ShortField("Destination", 0x0400),
        ShortField("Source", 0x0300),
        ShortField("Data_link_Header_Checksum", 0x4b1e),
        PacketListField ("Data_Chunks",
        [
        dnp3_DataChunks(Data_Chunk="\xe9\xca\x02\x46\x05\x5b\x01\x11\x00\x78\x56\x34\x12\x00\x00\x00",Data_Chunk_CHecksum=0x3def),
        dnp3_DataChunks_v10(),
        ],
        dnp3_DataChunks,count_from=2),
        #decode('hex')
        ByteField("Application_Control",0xca),
        ByteField("Function_Code", 0x02),
        PacketListField("FileDataObject",[dnp3_FileDataObject()],dnp3_FileDataObject,count_from=1)
    ]

#读文件
class  dnp3_ReadFileReq(Packet):
    fields_desc = [
        ShortField("Start_Bytes", 0x0564),
        XByteField("Length", 0x16),
        XByteField("Control", 0xc4),
        ShortField("Destination", 0x0400),
        ShortField("Source", 0x0300),
        ShortField("Data_link_Header_Checksum", 0x7031),
        PacketListField ("Data_Chunks",
        [
        dnp3_DataChunks(Data_Chunk="\xe1\xc2\x01\x46\x05\x5b\x01\x08\x00\x78\x56\x34\x12\x00\x00\x00",Data_Chunk_CHecksum=0x9c1f),
        dnp3_DataChunks_v1(Data_Chunk="\x00",Data_Chunk_CHecksum=0xffff),
        ],
        dnp3_DataChunks,count_from=2),
        #decode('hex')
        ByteField("Application_Control",0xc2),
        ByteField("Function_Code", 0x01),       #读操作
        PacketListField("FileDataObject",[dnp3_FileDataObject()],dnp3_FileDataObject,count_from=1)
    ]
