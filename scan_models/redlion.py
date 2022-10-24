from pymongo import MongoClient

module_type_to_key = {
    'redlion': 'red lion'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = ['red', 'lion']
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result


if __name__ == '__main__':
    print(len(scan({})))
