from pymongo import MongoClient
from scan_models.utils import convert
pattern = r'.*{}.*'

module_type_to_key = {
    'snmp': 'snmp'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = [convert(key, module_type_to_key) for key in keys]
    keys.append("snmp")
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result


if __name__ == '__main__':
    key = {

    }
    print(len(scan(key)))
