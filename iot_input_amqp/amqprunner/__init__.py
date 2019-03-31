import logging
import os
from threading import Thread
import time

from odoo.service import server
from odoo.tools import config

from .consumer import AmqpConsumer

_logger = logging.getLogger(__name__)

START_DELAY = 5

# Here we monkey patch the Odoo server to start the job runner thread
# in the main server process (and not in forked workers). This is
# very easy to deploy as we don't need another startup script.


class AmqpRunnerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        scheme = (os.environ.get('ODOO_AMQP_SCHEME') or
                  config.misc.get("amqp", {}).get('scheme'))
        host = (os.environ.get('ODOO_AMQP_HOST') or
                config.misc.get("amqp", {}).get('host') or
                config['http_interface'])
        port = (os.environ.get('ODOO_AMQP_PORT') or
                config.misc.get("amqp", {}).get('port') or
                config['http_port'])
        broker = (os.environ.get('ODOO_AMQP_BROKER') or
                config.misc.get("amqp", {}).get('broker') or
                config['amqp_broker'])
        _logger.info(broker)
        self.runner = AmqpConsumer(scheme=scheme or 'http',
                                   host=host or 'localhost',
                                   port=port or 8069,
                                   amqp_url=broker, user='admin',
                                   password='admin')

    def run(self):
        # sleep a bit to let the workers start at ease
        time.sleep(START_DELAY)
        self.runner.run()

    def stop(self):
        self.runner.close()


amqp_thread = None

orig_prefork_start = server.PreforkServer.start
orig_prefork_stop = server.PreforkServer.stop
orig_threaded_start = server.ThreadedServer.start
orig_threaded_stop = server.ThreadedServer.stop


def prefork_start(server, *args, **kwargs):
    global amqp_thread
    _logger.error('prefork starting')
    res = orig_prefork_start(server, *args, **kwargs)
    if not config['stop_after_init']:
        _logger.info("starting jobrunner thread (in prefork server)")
        amqp_thread = AmqpRunnerThread()
        amqp_thread.start()
    return res


def prefork_stop(server, graceful=True):
    global amqp_thread
    if amqp_thread:
        amqp_thread.stop()
    res = orig_prefork_stop(server, graceful)
    if amqp_thread:
        amqp_thread.join()
        amqp_thread = None
    return res


def threaded_start(server, *args, **kwargs):
    global amqp_thread
    _logger.error('threaded starting')
    res = orig_threaded_start(server, *args, **kwargs)
    if not config['stop_after_init']:
        _logger.info("starting jobrunner thread (in threaded server)")
        amqp_thread = AmqpRunnerThread()
        amqp_thread.start()
    return res


def threaded_stop(server):
    global amqp_thread
    if amqp_thread:
        amqp_thread.stop()
    res = orig_threaded_stop(server)
    if amqp_thread:
        amqp_thread.join()
        amqp_thread = None
    return res


server.PreforkServer.start = prefork_start
server.PreforkServer.stop = prefork_stop
server.ThreadedServer.start = threaded_start
server.ThreadedServer.stop = threaded_stop
