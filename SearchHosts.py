#! /usr/bin/python
# -*- coding: UTF-8 -*-
import nmap
class SearchHosts():
    '''搜索目标网段内开放指定端口的主机'''
    def __init__(self, hosts, port):
        self.hosts = hosts
        self.port = port
        self.result = []

    def searchTCP(self):
        nm = nmap.PortScanner()
        nm.scan(self.hosts, arguments='-p '+self.port+' -sV')
        hosts_list = [(nm[x][u'tcp'].keys(), x, nm[x][u'tcp'][int(self.port)]['state'], nm[x][u'tcp'][int(self.port)]['name']) for x in nm.all_hosts()]
        
        for port, host, status, name in hosts_list:
            print('{0}: {1}  >>> {2} |  service: {3} '.format(host, port, status, name))
            params = {
                'port': '00',
                'host': '0.0.0.0',
                'status': 'failed',
                'name': 'unknown',
            }
            params['port'] = port
            params['host'] = host
            params['status'] = status
            params['name'] = name
            self.result.append(params)
        return self.result