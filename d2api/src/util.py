from json import JSONDecoder

def _make_unique(key, dct):
    counter = 0
    unique_key = key

    while unique_key in dct:
        counter += 1
        unique_key = f'{key}_{counter}'
    return unique_key

def _parse_object_pairs(pairs):
    dct = {}
    for key, value in pairs:
        if key in dct:
            key = _make_unique(key, dct)
        dct[key] = value

    return dct

decode_json = JSONDecoder(object_pairs_hook = _parse_object_pairs).decode