def find_e(key, value):
    for k, v in value.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find_e(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find_e(key, d):
                    yield result
