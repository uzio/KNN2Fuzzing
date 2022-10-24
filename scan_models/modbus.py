from pymongo import MongoClient
from scan_models.utils import convert

module_type_to_key = {
    'bmx': 'm340'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = [convert(keys[key], module_type_to_key) for key in keys]
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result


if __name__ == '__main__':
    key = {
        'CPU Module': 'BMX P34 2020',
        'Vendor Name': 'Schneider Electric  ',
        'Category': 'M340'
    }
    print(len(scan(key)))
