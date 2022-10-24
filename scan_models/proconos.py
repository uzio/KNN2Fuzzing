from pymongo import MongoClient

module_type_to_key = {
    'proconos': 'proconos'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = ['proconos']
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result
