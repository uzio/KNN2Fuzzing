import siemens
import modbus
import omron
import wincc
import clearscada
import redlion
import ethip
import snmp
import pcworx
import dnp3
import bacnet
import wincc


def scan(model, keys):
    if model == 'siemens':
        return siemens.scan(keys)
    elif model == 'modbus':
        return modbus.scan(keys)
    elif model == 'omron':
        return omron.scan(keys)
    elif model == 'wincc':
        return wincc.scan(keys)
    elif model == 'clearscada':
        return clearscada.scan(keys)
    elif model == 'crimson':
        return redlion.scan(keys)
    elif model == 'ethip':
        return ethip.scan(keys)
    elif model == 'snmp':
        return snmp.scan(keys)
    elif model == 'bacnet':
        return bacnet.scan(keys)
    elif model == 'wincc':
        return wincc.scan(keys)
    elif model == 'dnp3':
        return dnp3.scan(keys)
    return []

