# coding=utf-8
import uuid
import socket
from kitty.targets.server import ServerTarget
from scapy.all import *
from scapy.layers.inet import Ether


class EthTarget(ServerTarget):
    '''
    EthTarget直接在第二层数据链路组包
    '''
    def __init__(self, name, targetIP, logger=None):
        '''
        :param name: name of the target
        :param src: 源mac地址
        :param dst: 目的mac地址
        :param targetIP: 目的mIP地址
        :param logger: logger for the object (default: None)
        '''
        super(EthTarget, self).__init__(name, logger)
        self.src = self._get_mac_address()
        self.targetIP = targetIP
        self.dst = self._getTargetMacAdd()
        if self.targetIP is None:
            raise ValueError('targetIP may not be None')
        self.expect_response = False

    def _get_mac_address(self):
        # 获取本机mac地址
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    def _getTargetMacAdd(self):
        # 根据目标IP获取mac地址
        IpScan = self.targetIP
        try:
            ans, unans = srp(scapy.all.Ether(dst="FF:FF:FF:FF:FF:FF") / scapy.all.ARP(pdst=IpScan), timeout=2)
        except Exception as e:
            print(e)
        else:
            for send, rcv in ans:
                ListMACAddr = rcv.sprintf("%Ether.src%")
                return ListMACAddr

    def _send_to_target(self, data):
        e = Ether(type=0x0800, src=self.src, dst=self.dst)
        sock = conf.L2socket()
        sock.send(e/data)
        self.response = sock.recv(1000)

    def _receive_from_target(self):
        return self.response

