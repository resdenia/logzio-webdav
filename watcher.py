from webdav3.client import Client
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime as dt

import json
import ast
from helpers.grok_validator import gr_validator
from helpers.logz_conf import config_data
from helpers.webdav import auth_basic
from helpers.find_etag import find_e
from helpers.compare_etag import compare_file_etag
from helpers.generate_custom_etag import generate_etag
from helpers.last_find import find_last_mod_date
import time
import logging
import logging.config
from decouple import config
import numpy as np
import os
import asyncio


LOGGING = config_data()

logging.config.dictConfig(LOGGING)

logger = logging.getLogger('superAwesomeLogzioLogger')

ROOT_DATA_STATE = {}
STATUS_LAST_LOG = {}


class Watcher:
    # DIRECTORY_TO_WATCH = "/usr/var/app/log-folder-receiver/"
    DIRECTORY_TO_WATCH = "/Users/resdeni/Documents/integrations/20-10-2021/webdav-python-custom/log-folder-receiver/"
    # WEBDAV_DIR = "http://192.168.0.105:8080/"
    # WEBDAV_USERNAME = "resdeni"
    # WEBDAV_PASSWORD = "resdeni"
    WEBDAV_DIR_LINK = config("WEBDAV_DIR_LINK")

    def status_log(self):
        with open('data_status.json', 'r') as outfile:
            if os.stat("data_status.json").st_size == 0:
                ROOT_DATA_STATE = {}
            else:
                ROOT_DATA_STATE = json.load(outfile)
        return

    def file_manager(self):
        # options = {
        #     'webdav_hostname': self.WEBDAV_DIR,

        #     'webdav_login':    self.WEBDAV_USERNAME,
        #     'webdav_password': self.WEBDAV_PASSWORD,
        #     'verbose': True
        # }
        # client = Client(options)
        try:
            client = auth_basic()
        except:
            print("Please check your credentials to webDab server")

        files3 = client.list(self.WEBDAV_DIR_LINK,  get_info=True)
        with open('data_status.json', 'r') as outfile:
            if os.stat("data_status.json").st_size == 0:
                ROOT_DATA_STATE = {}
            else:
                ROOT_DATA_STATE = json.load(outfile)
        for file in files3:
            splited_file = file['path'].split('/')[-1]
            if splited_file in ROOT_DATA_STATE:
                # print(ROOT_DATA_STATE[splited_file]['size'] != file['size'])
                # print(file['size'])
                # print('filesize in json')
                # print(ROOT_DATA_STATE[splited_file]['size'])
                if ROOT_DATA_STATE[splited_file]['size'] != file['size']:
                    print('found changes sizes changes')
                    kwargs = {
                        'remote_path': file["path"],
                        'local_path':  "/Users/resdeni/Documents/integrations/20-10-2021/webdav-python-custom/log-folder-receiver/"+ROOT_DATA_STATE[splited_file]['name'],
                        'callback':    self.callback
                    }
                    client.download_sync(**kwargs)
                    ROOT_DATA_STATE[splited_file]['size'] = file['size']
                    ROOT_DATA_STATE[splited_file]['modified'] = file['modified']
                    with open('data_status.json', 'w') as outfile:
                        json.dump(ROOT_DATA_STATE, outfile)
                    continue
                if ROOT_DATA_STATE[splited_file]['modified'] != file['modified']:
                    print('found changes modified changes')
                    kwargs = {
                        'remote_path': file["path"],
                        'local_path':  "/Users/resdeni/Documents/integrations/20-10-2021/webdav-python-custom/log-folder-receiver/"+ROOT_DATA_STATE[splited_file]['name'],
                        'callback':    self.callback
                    }
                    client.download_async(**kwargs)
                    ROOT_DATA_STATE[splited_file]['size'] = file['size']
                    ROOT_DATA_STATE[splited_file]['modified'] = file['modified']
                    with open('data_status.json', 'w') as outfile:
                        json.dump(ROOT_DATA_STATE, outfile)
                    continue

            else:
                print('found changes modified changes')
                ROOT_DATA_STATE[splited_file] = {'name': ''}
                ROOT_DATA_STATE[splited_file]['name'] = splited_file
                ROOT_DATA_STATE[splited_file]['modified'] = file['modified']
                ROOT_DATA_STATE[splited_file]['size'] = file['size']
                ROOT_DATA_STATE[splited_file]['created'] = file['created']
                ROOT_DATA_STATE[splited_file]['isdir'] = file['isdir']
                ROOT_DATA_STATE[splited_file]['etag'] = file['etag']
                kwargs = {
                    'remote_path': file["path"],
                    'local_path':  "/Users/resdeni/Documents/integrations/20-10-2021/webdav-python-custom/log-folder-receiver/"+ROOT_DATA_STATE[splited_file]['name'],
                    'callback':    self.callback
                }
                client.download_async(**kwargs)

                with open('data_status.json', 'w') as outfile:
                    json.dump(ROOT_DATA_STATE, outfile)

    def __init__(self):
        self.observer = Observer()

    def callback(self):
        print('downloaded')

    def run(self):
        event_handler = Handler()
        self.observer.schedule(
            event_handler, path=self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
                self.file_manager()
                self.status_log()
                print('here')
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        with open('data_status.json', 'r') as outfile:
            ROOT_DATA_STATE = json.load(outfile)

        if event.is_directory:
            return None

        elif event.event_type == 'created':

            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            # TODO: add new logic for skip all hidden fiels
            if not '.DS_Store' in event.src_path:
                # env from .env to check if we need to send logs historical
                print('created')
                if config('SEND_HISTORICAL_LOGS') == 'False':
                    # take name of the file
                    filename = event.src_path.split('/')[-1]

                    current_etag = ROOT_DATA_STATE[filename]['etag']
                    # finding etag for each file
                    list_of_etags = list(find_e('etag', ROOT_DATA_STATE))
                    generated_custom_etag = generate_etag(current_etag)

                    data_unique = compare_file_etag(
                        list_of_etags, current_etag)
                    if len(data_unique[generated_custom_etag]) > 1:
                        print('file duplicated')
                        updated_root_data = find_last_mod_date(filename,
                                                               data_unique[generated_custom_etag], ROOT_DATA_STATE)
                        with open('data_status.json', 'w') as outfile:
                            json.dump(updated_root_data, outfile)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)
            # TODO: add new logic for skip all hidden fiels
            if not '.DS_Store' in event.src_path:

                # Open file and read
                with open(event.src_path, 'r') as file:
                    filename = event.src_path.split('/')[-1]
                    # Take filename for opened file
                    # print(ROOT_DATA_STATE)
                    # Test: print(filename)
                    # reverse file data starts from the end
                    for line in reversed(list(file)):
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
                           # test: print("time_log " + time_log)
                            # taking date for check if we have new date
                            day_today = dt.today()
                            day_today_format = day_today.strftime(
                                '%Y-%m-%d %H:%M:%S.%f')
                           # test: print(day_today_format)
                            # check if file already sent logs. in previos iterations
                            if filename in ROOT_DATA_STATE:
                                objFile = ROOT_DATA_STATE[filename]
                                if not 'date_sent_logs' in objFile:
                                    print('cant be')
                                    if config('SEND_HISTORICAL_LOGS') == 'False':
                                        ROOT_DATA_STATE[filename]['date_sent_logs'] = day_today_format
                                    else:
                                        timerValid = dt.strptime(
                                            time_log, '%Y-%m-%d %H:%M:%S.%f %Z')
                                        print(time_log)
                                        ROOT_DATA_STATE[filename]['date_sent_logs'] = timerValid.strftime(
                                            '%Y-%m-%d %H:%M:%S.%f')
                                        # parse to valid format date
                            timerValid = dt.strptime(
                                time_log, '%Y-%m-%d %H:%M:%S.%f %Z')
                            date_sent_logs = ROOT_DATA_STATE[filename]['date_sent_logs']

                            # Parse pattern with first one

                            date_sent_logs_date = dt.strptime(
                                date_sent_logs, '%Y-%m-%d %H:%M:%S.%f')
                            date_sent_logs_timestamp = dt.timestamp(
                                date_sent_logs_date)
                            timerValid_timestamp = dt.timestamp(timerValid)
                            # check last time to send data
                            # print(timerValid)
                            # print(date_sent_logs)

                            if date_sent_logs_timestamp < timerValid_timestamp:
                                # Parse pattern with first one

                                data = None
                                if len(config('GROK_PATTERNS')) > 0:
                                    data = gr_validator(
                                        line)
                                # if grok is not matched

                                if data == None:
                                    data = {"message3": line}
                                    # send parsed logs
                                logger.info(data, {"additional": "parsed"})
                                # write status
                                # print(
                                #     ROOT_DATA_STATE[filename]['date_sent_logs'])
                                ROOT_DATA_STATE[filename]['date_sent_logs'] = timerValid.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
                                with open('data_status.json', 'w') as outfile:
                                    json.dump(ROOT_DATA_STATE, outfile)

                        else:
                            # if we need to send logs without date
                            if not config('SEND_UNPARSE_LOGS') == 'False':
                                # take date today
                                day_today = dt.today()
                                day_today_format = day_today.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
                                if filename in ROOT_DATA_STATE:

                                    if not 'date_sent_logs' in ROOT_DATA_STATE[filename]:
                                        if not config('SEND_HISTORICAL_LOGS') == 'False':
                                            logger.info(
                                                line, {"additional": "unparsed"})
                                    else:
                                        date_sent_logs = ROOT_DATA_STATE[filename]['date_sent_logs']
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
                                            ROOT_DATA_STATE[filename]['date_sent_logs'] = timerValid.strftime(
                                                '%Y-%m-%d %H:%M:%S.%f')
                objFile = ROOT_DATA_STATE[filename]
                if not 'date_sent_logs' in objFile:
                    day_today = dt.today()
                    day_today_format = day_today.strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    ROOT_DATA_STATE[filename]['date_sent_logs'] = day_today_format
                with open('data_status.json', 'w') as outfile:
                    json.dump(ROOT_DATA_STATE, outfile)


if __name__ == '__main__':
    w = Watcher()
    # w.connect()
    w.run()
