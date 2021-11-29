from helpers.generate_custom_etag import generate_etag
from datetime import datetime as dt


def find_last_mod_date(file_name, array_etag, root_data):

    print(array_etag)
    for key, value in root_data.items():
        gen_etag = generate_etag(root_data[key]['etag'])
        if root_data[key]['etag'] in array_etag:
            date_sent_from_files = root_data[key]['date_sent_logs']

            if not 'date_sent_logs' in root_data[key]:
                root_data[file_name]['date_sent_logs'] = date_sent_from_files

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

      # print("Age: " + value + "\n")
    return root_data
    # date_last = 'test'

    # return date_last
