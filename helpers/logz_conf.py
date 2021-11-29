from decouple import config


def config_data():
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'logzioFormat': {
                'format': '{"additional_field": "value"}',
                'validate': False
            }
        },
        'handlers': {
            'logzio': {
                'class': 'logzio.handler.LogzioHandler',
                'level': 'INFO',
                'formatter': 'logzioFormat',
                'token': config('LOGZIO_SHIPPING_KEY'),
                'logzio_type': 'superAwesomeLogzioLogger',
                'logs_drain_timeout': 5,
                'url': config('LOGZIO_LISTENER_URL')
            }
        },
        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': ['logzio'],
                'propagate': True
            }
        }
    }
