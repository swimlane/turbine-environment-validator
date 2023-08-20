#!/usr/bin/env python3
import subprocess
import sys
import shutil
import os

import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler

logger = log_handler.setup_logger()


def create_virtual_env():

    sp = subprocess.run(["python3 -m virtualenv pip-install-test-venv"],
                                stderr=subprocess.STDOUT,
                                encoding='UTF-8',
                                shell=True,
                                stdout=subprocess.PIPE
                              )

    if config.arguments.pip_config and sp.returncode == 0:
        try:
            shutil.copyfile(config.arguments.pip_config, 'pip-install-test-venv/pip.conf')
        except FileNotFoundError:
            logger.warning("Couldn't find file {} for pip config, continuing without it...".format(config.arguments.pip_config))

    if sp.returncode != 0:
        logger.error("Something went wrong with trying to create a virtualenv. Is virtualenv installed?")
        logger.debug(sp.stdout)
        return False
    else:
        logger.debug("Virtualenv created to test pip with config file")
        return True


def attempt_pip_install():
    result = {
        "pip": {}
    }

    if not create_virtual_env():
        result['pip']['message'] = "Failed to configure the venv to test pip with, is python3-virtualenv installed?"
        result['pip']['results'] = "{}Failed{}".format(config.FAIL, config.ENDC)
        return result

    logger.info("Attempting to install pip package example-package")
    sp = subprocess.run(["pip-install-test-venv/bin/python -m pip install example-package --retries 0 --timeout 5"],
                                stderr=subprocess.STDOUT,
                                encoding='UTF-8',
                                shell=True,
                                stdout=subprocess.PIPE
                              )

    if sp.returncode != 0:
        logger.error("Something went wrong with the pip install command..")
        logger.error(sp.stdout)
        result['pip']['message'] = "Something went wrong with the pip install command."
        result['pip']['results'] = "{}Failed{}".format(config.FAIL, config.ENDC)
    else:
        logger.info("Was able to install example-package from the configured pip repository!")
        result['pip']['message'] = "example-package was able to be installed from the configured PyPi server."
        result['pip']['results'] = "{}Passed{}".format(config.OK, config.ENDC)
    
    return result
