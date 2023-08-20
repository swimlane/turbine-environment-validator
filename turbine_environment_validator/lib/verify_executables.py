#!/usr/bin/env python3
import os
import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
from shutil import which
logger = log_handler.setup_logger()

def get_executable(name):
    """Check whether `name` is on PATH and marked as executable."""

    return which(name)

def check_installed_executables(_executables):
    executables = [item['value'] for item in _executables]
    logger.debug('Checking for executables {}'.format(executables))
    results = {}

    for exe in executables:

        result = {
            'path': '-',
            'message': '-'
        }

        r = get_executable(exe)
        
        if r is not None:
            logger.debug('{} is installed but is not allowed'.format(r))
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)
            result['message'] = "{} is not allowed to be pre-installed".format(exe)
            result['path'] = r
        else:
            logger.debug('{} is not installed.'.format(exe))
            result['result'] = "{}Passed{}".format(config.OK, config.ENDC)
        
        results[exe] = result

    return results