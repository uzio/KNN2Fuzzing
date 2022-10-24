from pymongo import MongoClient


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = ['niagara', 'niagara ax']
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    mongo.close()
    return result


if __name__ == '__main__':
    key = {
        'Protocol': 'bacnet',
        'Vendor ID': 'siemens',
        'Version': '9.0.0.4256'
    }
    print(len(scan(key)))
