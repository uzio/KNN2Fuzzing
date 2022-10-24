from pymongo import MongoClient
from scan_models.utils import convert

port = 102
pattern = r'.*{}.*'

module_type_to_key = {
    'IM151': 'ET200',
    'simatic 300': 's7-300',
    '6ES7': 's7'
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
                "is_s7":True,
                "module_id": "6ES7 212-1BE40-0XB0 ",
                "hardware": ""
            }
    print(len(scan(key)))
