#!/usr/bin/env python3
import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
import json
import requests
import socket

logger = log_handler.setup_logger()

def verify_dns_resolution(lb_fqdn):
    try:
        logger.debug("Load Balancer FQDN resolved to: {}".format(socket.gethostbyname(lb_fqdn)))
        return True
    except:
        logger.info("Unable to resolve {}".format(lb_fqdn))
        return False


def verify_port_connectivity(LB_CONNECTIVITY_ENDPOINTS):
    results = {}
    for endpoint in LB_CONNECTIVITY_ENDPOINTS:
        result = {}
        logger.info('Checking connectivity for {}'.format(endpoint))

        result_name = "{}".format(endpoint)

        if not verify_dns_resolution(config.lb_fqdn):
            result['message'] = "Unable to resolve {}".format(config.lb_fqdn)
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)
            results[result_name] = result
            continue

        try:
            r = requests.get(endpoint, timeout=10, verify=False)
        except:
            logger.error("{} refused the connection..".format(endpoint))
            logger.debug("Caught exception during LB Check", exc_info=True)
            result['message'] = "{} refused the connection..".format(endpoint)
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)
            results[result_name] = result
            continue

        if r.status_code == 200:
            logger.info("{} responded!".format(endpoint))

            if config.arguments.enable_listeners:
                try:
                    json_r = json.dumps(r.json())
                except json.decoder.JSONDecodeError:
                    json_r = ''
                    logger.error('Couldnt JSON decode response from {}'.format(endpoint))
                    logger.error(r.content)

                if json_r == '{"status": "ok"}':
                    result['message'] = "-"
                    result['result'] = "{}Passed{}".format(config.OK, config.ENDC)
                else:
                    result['message'] = "{}responded but it didnt match the expected output. Did something else respond to it?".format(endpoint)
                    result['result'] = "{}Warning{}".format(config.WARNING, config.ENDC)
                    logger.error("{}responded but it didnt match the expected output. Did something else respond to it?".format(endpoint))
                    logger.error(r.content)
            else:
                result['message'] = "-"
                result['result'] = "{}Passed{}".format(config.OK, config.ENDC)
        else:
            logger.error("{} didn't respond with code 200..".format(endpoint))
            result['message'] = "{} didn't respond with code 200..".format(endpoint)
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)
            results[result_name] = result
        
        results[result_name] = result

    return results
