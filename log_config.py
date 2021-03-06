import logging.config


handlers = []

config = {
    'version': 1,
    'formatters': {
        'debug_ftm': {
            'format': '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
        },
        'default_fmt': {
            'format': '%(asctime)s - %(name)s - %(message)s'
        },
    },
    'handlers': {
        'debugging': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'debug_ftm',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default_fmt',
            'mode': 'a',
            'maxBytes': 15*1024*1024,
            'backupCount': 3,
            'encoding': None,
            'delay': 0,
            'filename': 'logs/log.log'
        },
        'query_to_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default_fmt',
            'mode': 'a',
            'maxBytes': 15*1024*1024,
            'backupCount': 3,
            'encoding': None,
            'delay': 0,
            'filename': 'logs/query.log'
        },
    },
    'loggers': {
        'handlers': {
            'handlers': handlers,
            'level': 0,
            'propagate': False,
        },
        'db': {
            'handlers': handlers,
            'level': 0,
            'propagate': False,
        },
        'scripts': {
            'handlers': handlers,
            'level': 0,
            'propagate': False,
        },
        'main': {
            'handlers': handlers,
            'level': 0,
            'propagate': False,
        },
        'sqlalchemy.engine': {
            'handlers': ['query_to_file'],
            'level': logging.INFO,
            'propagate': False,
        }
    },
}


def load_config(debug=False):
    handlers.append('file')
    if debug:
        handlers.append('debugging')
        set_level(logging.DEBUG)
    else:
        set_level(logging.INFO)
    logging.config.dictConfig(config)


def set_level(lvl):
    for loggers in config['loggers']:
        if 'sqlalchemy.engine' == loggers:
            # skip change level for logger sqlalchemy.engine
            continue
        config['loggers'][loggers]['level'] = lvl
    #logging.getLogger('sqlalchemy.engine').setLevel(lvl)
