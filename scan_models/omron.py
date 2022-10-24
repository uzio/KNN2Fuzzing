from pymongo import MongoClient
from scan_models.utils import convert

port = 9600
pattern = r'.*{}.*'

# http://www.ia.omron.com/products/category/automation-systems/programmable-controllers/cp1/index.html
module_type_to_key = {
    'CP1': 'CP1',
    'CJ1': 'CJ1',
    'CJ2': 'CJ2'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    keys = [convert(key, module_type_to_key) for key in keys]
    keys.append('omron')
    keys = ' '.join(keys)
    result.extend(vul.find({'$text': {'$search': keys}}))
    return result


if __name__ == '__main__':
    key = {'Timer/Counter': '8',
           'No. of steps/transitions': '0',
           'For System Use': '\\x08',
           'Controller Model': 'CJ1M_CPU13          04.10',
           'No. DM Words': '32768',
           'Expansion DM Size': '0',
           'Controller Version': '04.10',
           'Memory Card Size': '0',
           'Kind of Memory Card': 'No Memory Card',
           'IOM size': '23',
           'Program Area Size': '40'}
    print(len(scan(key)))
