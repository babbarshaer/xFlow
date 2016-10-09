# -*- coding: utf-8 -*-


""" xFlow """


import sys
import argparse
import logging
from logging.config import dictConfig


__author__ = "Jude D'Souza <dsouza_jude@hotmail.com>"
__version_info__ = (0, 1)
__version__ = '.'.join(map(str, __version_info__))


log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def _get_args():
    ''' Following are the usage options:

    xflow <CONFIG> [-v | --validate]
    xflow <CONFIG> [-c | --configure]
    xflow <CONFIG> [-p | --publish <STREAM> <DATA>]
    xflow <CONFIG> [--log-level <LEVEL>]

    '''
    parser = argparse.ArgumentParser(prog='xflow', usage='%(prog)s CONFIG [options]', description='xFlow | A serverless workflow architecture.')
    parser.add_argument('CONFIG', type=str, help='Absolute path to config file')
    parser.add_argument('-v', action='store_true', help='Validates the config file')
    parser.add_argument('-c', action='store_true', help='Configures lambdas, streams and the subscriptions')
    parser.add_argument('-p', type=str, nargs=2, metavar=("<STREAM>","<DATA>"), required=False, help='Publishes data to a stream')
    parser.add_argument('--log-level', type=str, default='INFO', help='Setting log level [DEBUG|INFO|WARNING|ERROR|CRITICAL]')
    return vars(parser.parse_args())


def setup_logging(log_level):
    logging_config = dict(
        version = 1,
        formatters = {
            'simple': {
                    'format': '%(asctime)s %(levelname)-8s %(message)s'
                }
            },
        handlers = {
            'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                    'level': log_level,
                    'stream': 'ext://sys.stdout'
                }
            },
        root = {
            'handlers': ['console'],
            'level': log_level,
            },
    )
    dictConfig(logging_config)
    return logging.getLogger(__name__)


def main():
    args = _get_args()
    level = args['log_level'].upper()
    level = log_levels.get(level, logging.INFO)
    log = setup_logging(log_level=level)

    import core, utils

    config_file = args['CONFIG']
    if not utils.file_exists(config_file):
        log.error('File %s does not exist' % (config_file))
        sys.exit(1)

    log.info('Validating config')
    try:
        core.Engine.validate_config(config_file)
    except core.ConfigValidationError as ex:
        log.error('Invalid config. %s' % (str(ex)))
        sys.exit(1)

    log.info('Initializing xFlow engine')
    engine = core.Engine(config_file)
    log.info('Config is valid')

    # Configure the lambdas, streams and subscriptions
    if args['c']:
        logging.info('Configuring xFlow Engine')
        engine.configure()
        logging.info('xFlow Engine configured')

    # Publish json data to stream
    if args['p']:
        stream = args['p'][0]
        data = args['p'][1]
        log.info('\nPublishing to stream: %s\n\nData: %s' % (stream, data))
        engine.publish(stream, data)
        log.info('Published')


if __name__ == '__main__':
    main()
