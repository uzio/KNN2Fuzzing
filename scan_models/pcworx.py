# coding:utf-8
from pymongo import MongoClient
from utils import get_search_param

module_type_to_key = {
    'ilc': 'ilc'
}


def scan(keys):
    mongo = MongoClient()
    db = mongo.fuzz
    vul = db.vulnerability
    result = []
    param = get_search_param(keys, module_type_to_key)
    if param == '':
        return result
    result.extend(vul.find({'$text': {'$search': param}}))

    return result


if __name__ == '__main__':
    # 产品型号 https://www.phoenixcontact.com/online/portal/us/pxc/product_list_pages/!ut/p/z1/vVRNb8IwDP01HKM4aVLaY-nQ2AQbDBi0lyptUwjqF22AsV-_Fk47jGqaWBQpjhU_51l-xj5eYz8XR7URWhW5SJu755vBYrAYDqfUJK8zPoCnB-4Ox-yNjMYMv2Mf-1GuS73F3qGWeQ9OMuxBJlRjllURHyJd9yBVtQ5KsZH1xbupRJaJMJVBVOS6KtJUVnVQIkoQtLsHccKooLGNEs4oYjxmyALDQIQnQE0uhRGFbe4yUjH2LAKSUZOixJQ2YpZlIIv0KeI0TPoJBU6ljVc3yTgE-7e5XuPhh-VAV7zXxPcD-kiAjBiZPHLTgplLxy_Gw9DpE8Cro5InvMyLKmtqP_8lvRF0ZaB_zNABT-4KP7ovvH3f4tjGXeGnf_39c1fzNpNA7fZ732nk3khWfmi8_ne9r1pWHRq-PLgh0rnMg-U8mK7d5byr5eBaR5WVqYqUnhSxTLGnq4Ns3SJqpyT2aimqaHsZDzexyiyzjLNC3vPxdFokmRta34-zATsmws_k7HwBRzPsNw!!/#Z7_2G101H41MG5680QC2LN3DEA7H0
    key = {'Firmware Date': 'Mar  2 2012',
           'PLC Type': 'ILC 330 ETH',
           'Firmware Version': '3.95T',
           'Firmware Time': '09:39:02',
           'Model Number': '2737193'}
    print(len(scan(key)))
