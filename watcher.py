
from datetime import datetime as dt
import threading
import codecs
# from multiprocessing import Process
# import queue
from pathlib import Path

import io
import pickle
import json
import time
import logging
import logging.config
from decouple import config
import numpy as np
import os
from helpers.grok_validator import gr_validator
from helpers.logz_conf import config_data
from helpers.webdav import auth_basic
from helpers.find_etag import find_e
from helpers.compare_etag import compare_file_etag
from helpers.generate_custom_etag import generate_etag
from helpers.last_find import find_last_mod_date


LOGGING = config_data()

logging.config.dictConfig(LOGGING)

logger = logging.getLogger('superAwesomeLogzioLogger')

STATUS_LAST_LOG = {}

threadLock = threading.Lock()


class Watcher:
    ROOT_DATA_STATE = {}
    WEBDAV_DIR_LINK = config("WEBDAV_DIR_LINK")

    def send_logs_from_created_file(self, file_data, filename, buffer):

        if config('SEND_HISTORICAL_LOGS') == 'False':
            # take name of the file

            current_etag = file_data['etag']
            # finding etag for each file
            list_of_etags = list(find_e())
            generated_custom_etag = generate_etag(current_etag)
            data_unique = compare_file_etag(
                list_of_etags, current_etag)

            if generated_custom_etag in data_unique and len(data_unique[generated_custom_etag]) > 1:
                print('file duplicated')
                # file duplicated
                updated_root_data = find_last_mod_date(filename,
                                                       data_unique[generated_custom_etag], file_data)
                with open("data_state/__" + filename + ".json", 'w') as outfile:
                    json.dump(updated_root_data, outfile)
            else:
                self.send_logs_from_modified_file(
                    file_data, filename, buffer)
        else:
            self.send_logs_from_modified_file(
                file_data, filename, buffer)
        return True

    def send_logs_from_modified_file(self, file_data, filename, buffer):
        if not filename.startswith('.'):
            # Open file and read
            buffer_parsed = buffer.decode().splitlines()

            # reverse file data starts from the end
            for line in reversed(buffer_parsed):
                # if we have empty string continue to the next line
                if line == '':
                    continue
                # spliting string to receive date
                ts = line.split()
                # add checks if it's have groked value
                if len(ts) > 1:
                    # parse date from line with log
                    time_log_unparsed = ts[0] + \
                        " " + ts[1] + " " + ts[2]
                    # remove brackets => []
                    time_log = time_log_unparsed[1:-1]
                    # taking date for check if we have new date
                    day_today = dt.today()
                    day_today_format = day_today.strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    # test: print(day_today_format)
                    # check if file already sent logs. in previos iterations
                    objFile = file_data
                    if not 'date_sent_logs' in objFile:
                        if config('SEND_HISTORICAL_LOGS') == 'False':
                            file_data['date_sent_logs'] = day_today_format
                        else:
                            timerValid = dt.strptime(
                                time_log, '%Y-%m-%d %H:%M:%S.%f %Z')
                            file_data['date_sent_logs'] = timerValid.strftime(
                                '%Y-%m-%d %H:%M:%S.%f')
                            # parse to valid format date
                    timerValid = dt.strptime(
                        time_log, '%Y-%m-%d %H:%M:%S.%f %Z')
                    date_sent_logs = file_data['date_sent_logs']

                    # Parse pattern with first one

                    date_sent_logs_date = dt.strptime(
                        date_sent_logs, '%Y-%m-%d %H:%M:%S.%f')
                    date_sent_logs_timestamp = dt.timestamp(
                        date_sent_logs_date)
                    timerValid_timestamp = dt.timestamp(timerValid)
                    # check last time to send data

                    if date_sent_logs_timestamp < timerValid_timestamp:
                        # Parse pattern with first one
                        data = None
                        if len(config('GROK_PATTERNS')) > 0:
                            data = gr_validator(
                                line)
                            # if grok is not matched

                        if data == None:
                            data = {"message": line}
                            # send parsed logs
                        logger.info(data, {"additional": "parsed"})
                        # write status
                        file_data['date_sent_logs'] = timerValid.strftime(
                            '%Y-%m-%d %H:%M:%S.%f')
                        with open("data_state/__" + filename + ".json", 'w') as outfile:
                            json.dump(file_data, outfile)
                else:
                  # if we need to send logs without date
                    if not config('SEND_UNPARSE_LOGS') == 'False':
                        # take date today
                        day_today = dt.today()
                        day_today_format = day_today.strftime(
                            '%Y-%m-%d %H:%M:%S.%f')

                        if not 'date_sent_logs' in file_data:
                            if not config('SEND_HISTORICAL_LOGS') == 'False':
                                logger.info(
                                    line, {"additional": "unparsed"})
                        else:
                            date_sent_logs = file_data['date_sent_logs']
                            date_sent_logs_date = dt.strptime(
                                date_sent_logs, '%Y-%m-%d %H:%M:%S.%f')
                            date_sent_logs_timestamp = dt.timestamp(
                                date_sent_logs_date)
                            timerValid = dt.strptime(
                                day_today_format, '%Y-%m-%d %H:%M:%S.%f')
                            timerValid_timestamp = dt.timestamp(
                                timerValid)

                            if date_sent_logs_timestamp <= timerValid_timestamp:
                                logger.info(
                                    line, {"additional": "unparsed"})
                                file_data['date_sent_logs'] = timerValid.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
            objFile = file_data
            if not 'date_sent_logs' in file_data:
                day_today = dt.today()
                day_today_format = day_today.strftime(
                    '%Y-%m-%d %H:%M:%S.%f')
                file_data['date_sent_logs'] = day_today_format
            with open("data_state/__" + filename + ".json", 'w') as outfile:
                json.dump(file_data, outfile)
            return True

    def file_manager(self):
        try:
            # connect to webdav
            client = auth_basic()
            files3 = client.list(self.WEBDAV_DIR_LINK,  get_info=True)
        except:
            print("Please check your credentials to webDav server")
        # assign empty array to the threads
        threads = []
        for file in files3:
            splited_file = file['path'].split('/')[-1]
            my_file = Path("data_state/__" + splited_file + ".json")
            # check if is hidden file
            if splited_file.startswith('.'):
                continue
            if my_file.is_file():
                with open("data_state/__" + splited_file + ".json", 'r') as outfile:
                    ROOT_DATA_STATE = json.load(outfile)

                if ROOT_DATA_STATE['size'] != file['size']:
                    print('found changes, modified file')

                    ROOT_DATA_STATE['size'] = file['size']
                    ROOT_DATA_STATE['modified'] = file['modified']
                    try:
                        buffer = io.BytesIO()
                        res1 = client.resource(file["path"])
                        res1.write_to(buffer)
                        pickled = codecs.encode(pickle.dumps(
                            buffer.getvalue()), "base64").decode()
                        unpickled = pickle.loads(
                            codecs.decode(pickled.encode(), "base64"))
                    # self.send_logs_from_modified_file(
                    #     ROOT_DATA_STATE[splited_file], splited_file, unpickled, ROOT_DATA_STATE)
                        thread = threading.Thread(target=self.send_logs_from_modified_file, args=(
                            ROOT_DATA_STATE, splited_file, unpickled), daemon=True)
                        thread.setDaemon(True)
                        thread.start()
                        threads.append(thread)
                        with open("data_state/__" + splited_file + ".json", 'w') as outfile:
                            json.dump(ROOT_DATA_STATE, outfile)
                        continue
                    except Exception as e:
                        print(e)

                if ROOT_DATA_STATE['modified'] != file['modified']:
                    print('found changes, modified file')

                    ROOT_DATA_STATE['size'] = file['size']
                    ROOT_DATA_STATE['modified'] = file['modified']
                    try:
                        buffer = io.BytesIO()
                        res1 = client.resource(file["path"])
                        res1.write_to(buffer)
                        pickled = codecs.encode(pickle.dumps(
                            buffer.getvalue()), "base64").decode()
                        unpickled = pickle.loads(
                            codecs.decode(pickled.encode(), "base64"))
                    # self.send_logs_from_modified_file(
                    #     ROOT_DATA_STATE, splited_file, unpickled, ROOT_DATA_STATE)
                        thread = threading.Thread(target=self.send_logs_from_modified_file, args=[
                            ROOT_DATA_STATE, splited_file, unpickled], daemon=True)
                        thread.setDaemon(True)
                        thread.start()
                        threads.append(thread)
                        with open("data_state/__" + splited_file + ".json", 'w') as outfile:
                            json.dump(ROOT_DATA_STATE, outfile)
                        continue
                    except Exception as e:
                        print(e)

            else:
                print('found changes file-created')
                ROOT_DATA_STATE = {'name': ''}
                ROOT_DATA_STATE['name'] = splited_file
                ROOT_DATA_STATE['modified'] = file['modified']
                ROOT_DATA_STATE['size'] = file['size']
                ROOT_DATA_STATE['created'] = file['created']
                ROOT_DATA_STATE['isdir'] = file['isdir']
                ROOT_DATA_STATE['etag'] = file['etag']

                try:
                    if not splited_file.startswith('.'):
                        buffer = io.BytesIO()
                        res1 = client.resource(file["path"])
                        res1.write_to(buffer)

                        pickled = codecs.encode(pickle.dumps(
                            buffer.getvalue()), "base64").decode()
                        unpickled = pickle.loads(
                            codecs.decode(pickled.encode(), "base64"))

                        # self.send_logs_from_created_file(
                        #     ROOT_DATA_STATE[splited_file], splited_file, unpickled, ROOT_DATA_STATE)
                        thread = threading.Thread(target=self.send_logs_from_created_file, args=[
                                                  ROOT_DATA_STATE, splited_file, unpickled], daemon=True)
                        thread.start()
                        threads.append(thread)
                except Exception as e:
                    print(e)
                with open('data_state/__'+splited_file+".json", 'w') as outfile:
                    json.dump(ROOT_DATA_STATE, outfile)
        # logic to the threads
        for thread_buffer in threads:
            thread_buffer.join()
        # thread list reset
        threads = []

    def run(self):
        try:
            while True:
                time.sleep(5)
                self.file_manager()
                print('ping')
        except:
            print("General Error")


if __name__ == '__main__':
    w = Watcher()
    # w.connect()
    w.run()
