#!/usr/bin/env python3
import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
import subprocess

logger = log_handler.setup_logger()

def check_service_running(service):

    try:
        sp = subprocess.Popen(
                                    [
                                        "systemctl",
                                        "is-active",
                                        service
                                    ],
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.STDOUT
                                  )
    except FileNotFoundError:
        logger.error("Something went wrong with trying to check if {} is running. Does this system use systemctl?")
        return False    

    streamdata = sp.communicate()[0]
    logger.debug('{} enabled return code: {}'.format(service, sp.returncode))
    if sp.returncode == 0:
        logger.debug('{} is active'.format(service))
        return True
    else:
        logger.debug('{} is inactive'.format(service))
        return False

def check_service_enabled(service):

    try:
        sp = subprocess.Popen(
                                    [
                                        "systemctl",
                                        "is-enabled",
                                        service
                                    ],
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.STDOUT
                                  )
    except FileNotFoundError:
        logger.error("Something went wrong with trying to check if {} is enabled. Does this system use systemctl?")
        return False 

    streamdata = sp.communicate()[0]
    logger.debug('{} enabled return code: {}'.format(service, sp.returncode))
    if sp.returncode == 0:
        logger.debug('{} is enabled'.format(service))
        return True
    else:
        logger.debug('{} is disabled'.format(service))
        return False


def get_service_status(executables):
    results = {}
    for ntp_executable in executables :
        results[ntp_executable] = {}
        results[ntp_executable]['running'] = "{}False{}".format(config.FAIL, config.ENDC)
        results[ntp_executable]['enabled'] = "{}False{}".format(config.FAIL, config.ENDC)

        if check_service_running(ntp_executable):
            results[ntp_executable]['running'] = "{}True{}".format(config.OK, config.ENDC)
        else:
            results[ntp_executable]['running'] = "{}False{}".format(config.FAIL, config.ENDC)

        if check_service_enabled(ntp_executable):
            results[ntp_executable]['enabled'] = "{}True{}".format(config.OK, config.ENDC)
        else:
            results[ntp_executable]['enabled'] = "{}False{}".format(config.FAIL, config.ENDC)

    return results