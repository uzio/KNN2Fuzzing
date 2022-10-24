#coding:utf-8
import netifaces
import logging

def get_net():
    '''
    自动获取当前本机ip和网卡
    '''
    for interface_name in netifaces.interfaces():
        if interface_name.startswith('lo'):
            continue # TODO: continue if network interface is down
        addresses = netifaces.ifaddresses(interface_name)
        if netifaces.AF_INET in addresses:
            for item in addresses[netifaces.AF_INET]:
                if 'addr' in item:
                    # logging.debug('Found likely IP {0} on interface {1}'.format(item['addr'], interface_name))
                    net = [item['addr'],interface_name]
                    return net
    
    default_ip = '127.0.0.1'
    logging.warning('Count not detect likely IP, returning {0}'.format(default_ip))
    return '127.0.0.1'