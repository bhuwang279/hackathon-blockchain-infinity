import argparse
import asyncio
import logging
import sys

from zmq.asyncio import ZMQEventLoop

from sawtooth_sdk.processor.log import init_console_logging

from aiohttp import web

from infinity_rest_api.route_handler import RouteHandler
from infinity_rest_api.database import Database
from infinity_rest_api.messaging import Messenger


LOGGER = logging.getLogger(__name__)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Starts the Infinity REST API')

    parser.add_argument(
        '-B', '--bind',
        help='identify host and port for api to run on',
        default='localhost:8000')
    parser.add_argument(
        '-C', '--connect',
        help='specify URL to connect to a running validator',
        default='tcp://localhost:4004')
    parser.add_argument(
        '-t', '--timeout',
        help='set time (in seconds) to wait for a validator response',
        default=500)
    parser.add_argument(
        '--db-name',
        help='The name of the database',
        default='infinity')
    parser.add_argument(
        '--db-host',
        help='The host of the database',
        default='localhost')
    parser.add_argument(
        '--db-port',
        help='The port of the database',
        default='5432')
    parser.add_argument(
        '--db-user',
        help='The authorized user of the database',
        default='sawtooth')
    parser.add_argument(
        '--db-password',
        help="The authorized user's password for database access",
        default='sawtooth')
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='enable more verbose output to stderr')

    return parser.parse_args(args)


def start_rest_api(host, port, messenger, database):
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(database.connect())

    app = web.Application(loop=loop)
    # WARNING: UNSAFE KEY STORAGE
    # In a production application these keys should be passed in more securely
    app['aes_key'] = 'ffffffffffffffffffffffffffffffff'
    app['secret_key'] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

    messenger.open_validator_connection()

    handler = RouteHandler(loop, messenger, database)

    app.router.add_post('/authentication', handler.authenticate)

    app.router.add_post('/users', handler.create_user)
    app.router.add_get('/users', handler.list_users)
    app.router.add_get('/users/{user_id}', handler.fetch_user)

    app.router.add_post('/records', handler.create_record)
    app.router.add_get('/records', handler.list_records)
    app.router.add_get('/records/{record_id}', handler.fetch_record)
    app.router.add_post(
        '/records/{record_id}/transfer', handler.transfer_record)
    app.router.add_post('/records/{record_id}/update_location', handler.update_record_location)
    app.router.add_post('/records/{record_id}/update_for_sale', handler.update_record_for_sale)
    app.router.add_post('/records/{record_id}/update_stolen', handler.update_record_stolen)

    LOGGER.info('Starting Infinity REST API on %s:%s', host, port)
    web.run_app(
        app,
        host=host,
        port=port,
        access_log=LOGGER,
        access_log_format='%r: %s status, %b size, in %Tf s')


def main():
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)

    try:
        opts = parse_args(sys.argv[1:])

        init_console_logging(verbose_level=opts.verbose)

        validator_url = opts.connect
        if "tcp://" not in validator_url:
            validator_url = "tcp://" + validator_url
        messenger = Messenger(validator_url)

        database = Database(
            opts.db_host,
            opts.db_port,
            opts.db_name,
            opts.db_user,
            opts.db_password,
            loop)

        try:
            host, port = opts.bind.split(":")
            port = int(port)
        except ValueError:
            print("Unable to parse binding {}: Must be in the format"
                  " host:port".format(opts.bind))
            sys.exit(1)

        start_rest_api(host, port, messenger, database)
    except Exception as err:  # pylint: disable=broad-except
        LOGGER.exception(err)
        sys.exit(1)
    finally:
        database.disconnect()
        messenger.close_validator_connection()
