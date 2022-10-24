
vendors = ['johnson', 'siemens', 'tridium']

scripts = [{

}]


def get_vendor(vendor_key):
    for name in vendors:
        if name in vendor_key.lower():
            return name
    return ''


def convert(module_info, module_type_to_key):
    for key in module_type_to_key.keys():
        if not isinstance(key, str):
            continue
        try:
            if key.lower() in module_info.lower():
                return module_type_to_key[key]
        except AttributeError:
            break
    return ''


def get_search_param(keys, module_type_to_key):
    param = []
    for key in keys:
        value = keys[key]
        converted = convert(value, module_type_to_key)
        if converted != '':
            param.append(converted)
    return ' '.join(param)
