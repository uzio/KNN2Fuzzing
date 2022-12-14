#! /usr/bin/env python
# coding:utf-8
# Author: WenZhe Zhu
from scapy.all import conf
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import TCP


modbus_function_codes = {
    0x01: "Read Coils Request",
    0x02: "Read Discrete Inputs Request",
    0x03: "Read Holding Registers",
}

modbus_exceptions = {
    0x01: "Illegal Function Code",
    0x02: "Illegal Data Address",
    0x03: "Illegal Data Value",
    0x04: "Server Device Failure",
    0x05: "Acknowledge",
    0x06: "Server Device Busy",
    0x08: "Memory Parity Error",
    0x10: "Gateway Path Unavailable",
    0x11: "Gateway Target Device Failed to Respond"
}


class ModbusHeaderRequest(Packet):
    fields_desc = [
        ShortField("trans_id", 0x0003),  #  事务ID, 客户机发起，服务器复制，用于事务处理配对   客户机启动
        ShortField("proto_id", 0x0000),  #  协议标识符号  0= Modbus 协议
        ShortField("length", None),      #  长度  从本字节下一个到最后                      客户机启动
        ByteField("unit_id", 0x00),      #  单元标识符  客户机发起，服务器复制 串口链路或其他总线上远程终端标识 (只占一个字节)
        # ByteEnumField("func_code", 0x03, modbus_function_codes),
        ByteField("func_code",0x00)
        # ShortField("data",0x11)
        ]
    '''
    当 post_build()  被调用的时候， p  是当前的协议层， pay  是有效载荷，这就
    已经构建好了，我们想要我们的长度是将所有的数据都放到分隔符之后的全部长
    度，所以我们在 post_build()  中添加他们的计算。
    
    
    这里主要是因为后面的长度值依赖于前面的
    '''
    def post_build(self, p, pay):
        if self.length is None:
            l = len(pay) + 2
            '''
            struct.pack(">H", l) 参考博客
            https://blog.csdn.net/jackyzhousales/article/details/78030847
            >表示大端 ， H 表示 unsigned short
            p = p[:4] + struct.pack(">H", l) + p[6:]
            表示, p[:4]表示前4个自己 + 长度（2Bytes）+单元标识符+ 功能码 + 数据(pay)      
            '''
            p = p[:4] + struct.pack(">H", l) + p[6:]
        return p + pay

    def guess_payload_class(self, payload):
        try:
            return modbus_request_classes[self.func_code]
        except KeyError:
            pass
        return None


class ModbusHeaderResponse(Packet):
    fields_desc = [
        ShortField("trans_id", 0x0003),
        ShortField("proto_id", 0x0000),
        ShortField("length", None),
        ByteField("unit_id", 0x00),
        ByteEnumField("func_code", 0x03, modbus_function_codes)
        ]

    def post_build(self, p, pay):
        if self.length is None:
            l = len(pay) + 2
            p = p[:4] + struct.pack(">H", l) + p[6:]
        return p + pay

    def guess_payload_class(self, payload):
        try:
            return modbus_response_classes[self.func_code]
        except KeyError:
            pass
        try:
            if self.func_code in modbus_error_func_codes.keys():
                return GenericError
        except KeyError:
            pass
        return None


# PDU 0x01
class ReadCoilsRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("BitCount", 0x0000),  # Bit count (1-2000)

        ]


class ReadCoilsRequest_v1(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("BitCount", 0x0000),  # Bit count (1-2000)
        ShortField("ertraField", 0x0000)
        ]

class ReadCoilsRequest_v2(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000)
        ]



class ReadCoilsResponse(Packet):
    fields_desc = [
        BitFieldLenField("ByteCount", None, 8, count_of="CoilsStatus"),
        StrLenField("CoilsStatus", '', length_from=lambda pkt: pkt.ByteCount)
    ]


# PDU 0x02
class ReadDiscreteInputsRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("BitCount", 0x0000)  # Bit count (1-2000)
        ]


class ReadDiscreteInputsRequest_v1(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("BitCount", 0x0000),  # Bit count (1-2000)
        ShortField("ertraField", 0x0000)
        ]

class ReadDiscreteInputsRequest_v2(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ]



class ReadDiscreteInputsResponse(Packet):
    fields_desc = [
        BitFieldLenField("ByteCount", None, 8, count_of="InputStatus"),
        FieldListField("InputStatus", [0x00], ByteField("Data", 0x00), count_from=lambda pkt: pkt.ByteCount)]


# PDU 0x03
class ReadHoldingRegistersRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("WordCount", 0x0000)
        ]

class ReadHoldingRegistersRequest_v1(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("WordCount", 0x0000),
        ShortField("ertraField", 0x0000)
        ]

class ReadHoldingRegistersRequest_v2(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ]


class ReadHoldingRegistersResponse(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="RegisterValue"),
        FieldListField("RegisterValue", None, ShortField("Data", 0x0),
                       length_from=lambda pkt: pkt.ByteCount)
        ]


# PDU Data_Read
class ReadInputRegistersRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("WordCount", 0x0000)
        ]

class ReadInputRegistersRequest_v1(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("WordCount", 0x0000),
        ShortField("ertraField",0x0000)
        ]

class ReadInputRegistersRequest_v2(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000)
        ]


class ReadInputRegistersResponse(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="RegisterValue"),
        FieldListField("RegisterValue", None, ShortField("data", 0x0),
                       length_from=lambda pkt: pkt.ByteCount)
        ]


# PDU Data_write    写一个线圈操作  PDU 协议数据单元
class WriteSingleCoilRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),  # from 0x0000 to 0xFFFF
        ShortField("Data", 0x8888)             # 0x0000 == Off, 0xFF00 == On
        ]


class WriteSingleCoilRequest_v1(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),  # from 0x0000 to 0xFFFF
        ShortField("Data", 0x8888),             # 0x0000 == Off, 0xFF00 == On
        ShortField("ertraField", 0x0000)
        ]

class WriteSingleCoilRequest_v2(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),  # from 0x0000 to 0xFFFF
        ]


class WriteSingleCoilResponse(Packet):  # The answer is the same as the request if successful
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),  # from 0x0000 to 0xFFFF
        ShortField("Value", 0x0000)             # 0x0000 == Off, 0xFF00 == On
        ]


# PDU 0x06
class WriteSingleRegisterRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("Value", 0x0000),
        ]

class WriteSingleRegisterRequest_v1(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("Value", 0x0000),
        ShortField("ertraField", 0x0000)
        ]

class WriteSingleRegisterRequest_v2(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000)
        ]



class WriteSingleRegisterResponse(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("Value", 0x0000)
        ]


# PDU 0x07
# TODO: need fix this later
# class ReadExceptionStatusRequest(Packet):
#     fields_desc = []
#
#
# class ReadExceptionStatusResponse(Packet):
#     fields_desc = [ByteField("startingAddr", 0x00)]


# PDU 0x0F
class WriteMultipleCoilsRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        FieldLenField("BitCount", None, fmt="H", count_of="Values"),  # Bit count (1-800)
        FieldLenField("ByteCount", None, fmt="B", length_of="Values", adjust=lambda pkt, x:x/8+1),
        FieldListField("Values",[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x1], BitField("data", 0x0, size=1), count_from=lambda pkt: pkt.BitCount)
    ]


class WriteMultipleCoilsRequest_v1(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        FieldLenField("BitCount", None, fmt="H", count_of="Values"),  # Bit count (1-800)
        FieldLenField("ByteCount", None, fmt="B", length_of="Values", adjust=lambda pkt, x:x / 16),
        FieldListField("Values", [], BitField("data", 0x0, size=1), count_from=lambda pkt: pkt.BitCount)
    ]



class WriteMultipleCoilsResponse(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("BitCount", 0x0001)
    ]


# PDU 0x10
class WriteMultipleRegistersRequest(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        FieldLenField("WordCount", None, fmt="H", count_of="Values"),  # Word count (1-100)
        FieldLenField("ByteCount", None, fmt="B", length_of="Values", adjust=lambda pkt, x: x),
        FieldListField("Values", [0x0001,0x0002], ShortField("data", 0x0000), count_from=lambda pkt: pkt.WordCount)
    ]


class WriteMultipleRegistersResponse(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        ShortField("WordCount", 0x0001)
    ]


# PDU 0x11
# TODO: Add later


# PDU 0x14
class ReadFileSubRequest(Packet):
    fields_desc = [ByteField("RefType", 0x06),
                   ShortField("FileNumber", 0x0001),
                   ShortField("Offset", 0x0003),
                   ShortField("Length", 0x0005)
                   ]


class ReadFileRecordRequest(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="Groups", adjust=lambda pkt, x: x),
        PacketListField("Groups", [], ReadFileSubRequest, length_from=lambda p: p.ByteCount)
    ]


class ReadFileSubResponse(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="Data", adjust=lambda pkt, x: x + 1),
        ByteField("RefType", 0x06),
        FieldListField("Data", [0x0000], XShortField("", 0x0000),
                       length_from=lambda pkt: (pkt.respLength - 1))
    ]


class ReadFileRecordResponse(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="Values", adjust=lambda pkt, x: x),
        PacketListField("Groups", [], ReadFileSubResponse, length_from=lambda p: p.ByteCount)
    ]


# PDU 0x15
class WriteFileSubRequest(Packet):
    fields_desc = [
        ByteField("RefType", 0x06),
        ShortField("FileNumber", 0x0001),
        ShortField("Offset", 0x0002),
        FieldLenField("Length", None, fmt="H", count_of="Data"),
        FieldListField("Data", [0x0000], XShortField("sss", 0x0003), count_from=lambda pkt: pkt.Length)
    ]


class WriteFileRecordRequest(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="Groups", adjust=lambda pkt, x: x),
        PacketListField("Groups", [], WriteFileSubRequest, length_from=lambda p: p.ByteCount)
    ]


class WriteFileSubResponse(Packet):
    fields_desc = [
        ByteField("RefType", 0x06),
        ShortField("FileNumber", 0x0001),
        ShortField("Offset", 0x0000),
        FieldLenField("Length", None, fmt="H", length_of="Data", adjust=lambda pkt, x: x),
        FieldListField("Data", [0x0000], XShortField("", 0x0000), length_from=lambda pkt: pkt.Length)
    ]


class WriteFileRecordResponse(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="Values", adjust=lambda pkt, x: x),
        PacketListField("Groups", [], WriteFileSubResponse, length_from=lambda p: p.ByteCount)
    ]


# PDU 0x16
class MaskWriteRegisterRequest(Packet):
    # and/or to 0xFFFF/0x0000 so that nothing is changed in memory
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        XShortField("AndMask", 0xffff),
        XShortField("OrMask", 0x0000)
    ]


class MaskWriteRegisterResponse(Packet):
    fields_desc = [
        ShortField("ReferenceNumber", 0x0000),
        XShortField("AndMask", 0xffff),
        XShortField("OrMask", 0x0000)
    ]


# PDU 0x17
class ReadWriteMultipleRegistersRequest(Packet):
    fields_desc = [
        ShortField("ReadReferenceNumber", 0x0000),
        ShortField("ReadWordCount", 0x0000),  # Word count for read (1-125)
        ShortField("WriteReferenceNumber", 0x0000),
        FieldLenField("WriteWordCount", None, fmt="H", count_of="RegisterValues"),  # Word count for write (1-100)
        FieldLenField("WriteByteCount", None, fmt="B", length_of="RegisterValues"),
        FieldListField("RegisterValues", [0x0000], ShortField("Data", 0x0000),
                       count_from=lambda pkt: pkt.WriteWordCount)
    ]


class ReadWriteMultipleRegistersResponse(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="B", length_of="RegisterValues"),
        FieldListField("RegisterValues", None, ShortField("data", 0x0),
                       length_from=lambda pkt: pkt.ByteCount)
    ]


# PDU 0x18
class ReadFIFOQueueRequest(Packet):
    fields_desc = [ShortField("ReferenceNumber", 0x0000)]


class ReadFIFOQueueResponse(Packet):
    fields_desc = [
        FieldLenField("ByteCount", None, fmt="H", length_of="FIFOValues",
                      adjust=lambda pkt, p: p * 2 + 2),
        FieldLenField("FIFOCount", None, fmt="H", count_of="FIFOValues"),
        FieldListField("FIFOValues", None, ShortField("data", 0x0),
                       length_from=lambda pkt: pkt.ByteCount)
    ]

#PDU 0x2B

class ReadDeviceID(Packet):

    fields_desc = [
        ByteField("MEIType", 0x0E), # MEI类型
        ByteField("ReadDevID",0x01),# 范围是 01/02/03/04， ReadDevID码
        ByteField("objectID",0x00), # 范围是 0x00~0xFF，   对象ID
    ]


# Error packet
class GenericError(Packet):
    fields_desc = [ByteEnumField("exceptCode", 1, modbus_exceptions)]


modbus_request_classes = {
    0x01: ReadCoilsRequest,
    0x02: ReadDiscreteInputsRequest,
    0x03: ReadHoldingRegistersRequest,
    0x04: ReadInputRegistersRequest,
    0x05: WriteSingleCoilRequest,
    0x06: WriteSingleRegisterRequest,
    # 0x07: ReadExceptionStatusRequest,  # TODO: Add later
    0x0F: WriteMultipleCoilsRequest,
    0x10: WriteMultipleRegistersRequest,
    # 0x11: ReportSlaveIdRequest,  # TODO: Add later
    0x14: ReadFileRecordRequest,
    0x15: WriteFileRecordRequest,
    0x16: MaskWriteRegisterRequest,
    0x17: ReadWriteMultipleRegistersRequest,
    0x18: ReadFIFOQueueRequest,
}

modbus_error_func_codes = {
    0x81: "ReadCoilsError",
    0x82: "ReadDiscreteInputsError",
    0x83: "ReadHoldingRegistersError",
    0x84: "ReadInputRegistersError",
    0x85: "WriteSingleCoilError",
    0x86: "WriteSingleRegisterError",
    0x87: "ReadExceptionStatusError",
    0x8F: "WriteMultipleCoilsError",
    0x90: "WriteMultipleRegistersError",
    0x91: "ReportSlaveIdError",
    0x94: "ReadFileRecordError",
    0x95: "WriteFileRecordError",
    0x96: "MaskWriteRegisterError",
    0x97: "ReadWriteMultipleRegistersError",
    0x98: "ReadFIFOQueueError",
}

modbus_response_classes = {
    0x01: ReadCoilsResponse,
    0x02: ReadDiscreteInputsResponse,
    0x03: ReadHoldingRegistersResponse,
    0x04: ReadInputRegistersResponse,
    0x05: WriteSingleCoilResponse,
    0x06: WriteSingleRegisterResponse,
    # 0x07: ReadExceptionStatusResponse,  # TODO: Add later
    0x0F: WriteMultipleCoilsResponse,
    0x10: WriteMultipleRegistersResponse,
    # 0x11: ReportSlaveIdResponse,  # TODO: Add later
    0x14: ReadFileRecordResponse,
    0x15: WriteFileRecordResponse,
    0x16: MaskWriteRegisterResponse,
    0x17: ReadWriteMultipleRegistersResponse,
    0x18: ReadFIFOQueueResponse
}


# TODO: this not work with StreamSocket
bind_layers(TCP, ModbusHeaderRequest, dport=502)
bind_layers(TCP, ModbusHeaderResponse, sport=502)
