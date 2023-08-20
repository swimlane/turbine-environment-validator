#!/usr/bin/env python3
import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
import requests
import socket
import json

logger = log_handler.setup_logger()

def verify_dns_resolution(node_fqdn):
    try:
        logger.debug("Node FQDN resolved to: {}".format(socket.gethostbyname(node_fqdn)))
        return True
    except:
        logger.info("Unable to resolve {}".format(node_fqdn))
        return False

def verify_port_connectivity():
    results = {}
    for fqdn in config.arguments.additional_node_fqdn:
        result = {}

        for port in config.INTRA_CLUSTER_PORTS:
            logger.info('Checking connectivity for {}:{}'.format(fqdn, port))
            result[port] = "Skipped"
            try:
                r = requests.get('http://{}:{}/health'.format(fqdn, port), timeout=10)
            except:
                logger.error("{}:{} refused the connection..".format(fqdn, port))
                logger.debug("Caught exception during port check ", exc_info=True)
                result[port] = "{}Failed{}".format(config.FAIL, config.ENDC)

            if r.status_code == 200:
                logger.info("{}:{} responded!".format(fqdn, port))
                if json.dumps(r.json()) == '{"status": "ok"}':
                    result[port] = "{}Passed{}".format(config.OK, config.ENDC)
                else:
                    result[port] = "{}Warning{}".format(config.WARNING, config.ENDC)
                    logger.error( "{}:{} responded but it didnt match the expected output. Did something else respond to it?".format(fqdn, port))
                    logger.error(r.content)
            else:
                logger.error("{}:{} didn't respond with code 200..".format(fqdn, port))
                result[port] = "{}Failed{}".format(config.FAIL, config.ENDC)

        results[fqdn] = result

    return results