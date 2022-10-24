# coding:utf-8
import broadlink


def link():
    """
    获取排插
    :return: 排插mp1实例
    """
    device = broadlink.discover()
    device.auth()
    return device


def set_power(index, status):
    device = link()
    device.set_power(index, status)


def get_power_status():
    device = link()
    return device.check_power()


if __name__ == '__main__':
    status = get_power_status()
    print(status)