from pymongo import MongoClient

module_type_to_key = {
    'niagara': 'niagara'
}


def convert(module_type, type_to_key):
    for key in type_to_key.keys():
        if key in module_type:
            return type_to_key[key]
    return module_type


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = [convert(key, module_type_to_key) for key in keys]
    keys.append('niagara')
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result


if __name__ == '__main__':
    print(len(scan({})))
