from pymongo import MongoClient


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = ['clearscada']
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result
