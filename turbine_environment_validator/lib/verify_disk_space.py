#!/usr/bin/env python3
import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
import os

logger = log_handler.setup_logger()


def check_write_permission(directory):
    return os.access(directory, os.W_OK)


def check_directory_size(directories):
    results = {}

    for item in directories:
        directory = item['path']
        minimum_size = item['minimum_size']
        # for directory, minimum_size in item:
        logger.debug('Checking size of {}'.format(directory))

        result = {}

        try:
            df_output_lines = [s.split() for s in os.popen("df -BG {}".format(directory)).read().splitlines()]
            total = df_output_lines[1][1]
            used = df_output_lines[1][2]
            free = df_output_lines[1][3]
            percentage = df_output_lines[1][4]
        except:
            logger.error('{} cannot be found.'.format(directory))
            result['Total Space Size'] = "-"
            result['Percentage Used'] = "-"
            result['message'] = "{} could not be found".format(directory)
            result['minimum'] = minimum_size
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)
            results[directory] = result
            continue

        logger.debug('Partition size \nTotal: {total}\nUsed: {used}\nFree: {free}, Percentage Used: {percentage}'.format(
            total=total,
            used=used,
            free=free,
            percentage=percentage
            )
        )

        result['Total Space Size'] = total
        result['Percentage Used'] = percentage

        # Subtract 3% from the minimum to account for discrepancies in provisioning
        int_min_size = int(minimum_size.replace('G',''))
        min_size_adjusted =  int_min_size - (int_min_size * .05)
        logger.debug('{} is the calculated minimum needed size for {}'.format(min_size_adjusted, directory))

        if int(total.replace('G','')) >= min_size_adjusted:
            logger.info('{} has at least {} worth of space.'.format(directory, minimum_size))
            result['message'] = "-"
            result['minimum'] = minimum_size
            result['result'] = "{}Passed{}".format(config.OK, config.ENDC)
        else:
            logger.error('{} is less than {} worth of space'.format(directory, minimum_size))
            result['message'] = "{} is not large enough.".format(directory)
            result['minimum'] = minimum_size
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)

        if not check_write_permission(directory):
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)
            if result['message'] == '-':
                result['message'] = "No Write Permission."
            result['message'] = result['message'] + " No Write Permission."

        results[directory] = result
    return results


def check_if_mount(DIRECTORY_MOUNT):
    results = {}
    for directory in DIRECTORY_MOUNT:
        result = {}

        is_mount = os.path.ismount(directory)

        if is_mount:
            result['message'] = "{} is a mount.".format(directory)
            result['result'] = "{}Passed{}".format(config.OK, config.ENDC)
        else:
            result['message'] = "{} is not a mounted directory.".format(directory)
            result['result'] = "{}Failed{}".format(config.FAIL, config.ENDC)
        results[directory] = result
    return results
