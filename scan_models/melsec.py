from pymongo import MongoClient

module_type_to_key = {
    'melsec': 'melsec'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = ['mitsubishi', 'melsec']
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result
