#!/usr/bin/env python3
import turbine_environment_validator.lib.log_handler as log_handler

from threading import Thread
from flask import Flask
import click

logger = log_handler.setup_logger()

app = Flask(__name__)


def serve_on_port(port):
    logger.info("Starting http listener on {}...".format(port))

    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return '{ "status" : "ok" }'

    try:
        app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
    except Exception:
        logger.error('Couldnt start listener on port {}, is something already listening? Ports below 1024 can only be spawned by root.'.format(port))
        logger.debug("Caught exception while starting listener thread ", exc_info=True)


def start_lb_listener_threads(LB_CONNECTIVITY_PORTS):
    for port in LB_CONNECTIVITY_PORTS:
        thread = Thread(target=serve_on_port, args=[port])
        thread.daemon = True
        thread.start()


def start_intra_cluster_listener_threads(INTRA_CLUSTER_PORTS):

    for listener in INTRA_CLUSTER_PORTS:
        listener_thread = Thread(target=serve_on_port, args=[listener])
        listener_thread.daemon = True

        listener_thread.start()
