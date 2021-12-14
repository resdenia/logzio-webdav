from helpers.generate_custom_etag import generate_etag
from datetime import datetime as dt
from glob import glob
import json

# need to find last date update from dublicates...that not dublicate previous css


def find_last_mod_date(file_name, array_etag, root_data):

    print(array_etag)
    for f_name in glob('data_state/*.json'):
        with open(f_name, 'r') as json_file:
            data = json.load(json_file)

        if data['etag'] in array_etag:
            date_sent_from_files = root_data['date_sent_logs']

        if not 'date_sent_logs' in root_data:
            root_data['date_sent_logs'] = date_sent_from_files

        date_sent_logs_current = dt.strptime(
            root_data[file_name]['date_sent_logs'], '%Y-%m-%d %H:%M:%S.%f')
        date_sent_from_files_parsed = dt.strptime(
            date_sent_from_files, '%Y-%m-%d %H:%M:%S.%f')
        date_sent_logs_current_timestamp = dt.timestamp(
            date_sent_logs_current)
        date_sent_from_files_parsed_timestamp = dt.timestamp(
            date_sent_from_files_parsed)
        if date_sent_logs_current_timestamp < date_sent_from_files_parsed_timestamp:
            root_data[file_name]['date_sent_logs'] = date_sent_from_files_parsed.strftime(
                '%Y-%m-%d %H:%M:%S.%f')

    #   # print("Age: " + value + "\n")
    return root_data
    # date_last = 'test'

    # return date_last
