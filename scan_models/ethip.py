from pymongo import MongoClient
from utils import convert

port = 44818
ip = "166.250.228.16"  # for test
pattern = r'.*{}.*'

module_type_to_key = {
    '1766': 'MicroLogix 1400'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    params = [convert(keys[key], module_type_to_key) for key in keys]
    if 'Product name' in keys:
        params.append(keys['Product name'])
    params = ' '.join(params)
    result.extend(vul.find({'$text': {'$search': params}}))
    return result


if __name__ == '__main__':
    key = {
        "Device IP": "100.10.10.110",
        "Vendor ID": "Rockwell Automation/Allen-Bradley",
        "Device type": "Communications Adapter",
        "Serial number": "0x00af5206",
        "Product name": "1766-ENBT/A"
    }
    print(len(scan(key)))
