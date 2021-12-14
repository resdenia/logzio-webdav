from glob import glob
import json


def find_e():
    searched = []
    for f_name in glob('data_state/*.json'):
        with open(f_name, 'r') as json_file:
            data = json.load(json_file)
            searched.append(data['etag'])
    return searched
