from webdav3.client import Client
from decouple import config


WEBDAV_DIR = config("WEBDAV_DIR")
WEBDAV_USERNAME = config("WEBDAV_USERNAME")
WEBDAV_PASSWORD = config("WEBDAV_PASSWORD")


def auth_basic():

    options = {
        'webdav_hostname': WEBDAV_DIR,
        'webdav_login':    WEBDAV_USERNAME,
        'webdav_password': WEBDAV_PASSWORD,
        'verbose': True
    }
    return Client(options)
