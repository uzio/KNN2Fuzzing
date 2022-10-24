from pymongo import MongoClient

module_type_to_key = {
    'dnp3': 'dnp3'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = ['dnp3']
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result


if __name__ == '__main__':
    print(len(scan({})))
