import os
import psutil
import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
import subprocess
import distro
import platform


logger = log_handler.setup_logger()


def run_command(cmd):
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        logger.info("run_command")
        logger.info(result)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return str(e.output)


def check_ubuntu():
    release_info = run_command('lsb_release -rs')
    if release_info in config.ALLOWED_OS['ubuntu']:
        return True
    else:
        return False


def check_centos_rhel_ol():
    release_info = run_command('cat /etc/redhat-release')
    version = release_info.split(' ')[2]
    if "CentOS" in release_info or "RHEL" in release_info or "Oracle Linux" in release_info:
        if version in config.ALLOWED_OS['redhat']:
            return True
        else:
            return False
    return False


def check_amazon_linux():
    if os.path.exists('/etc/system-release'):
        with open('/etc/system-release', 'r') as file:
            release_info = file.read()
            if "Amazon Linux 2" in release_info:
                return True
    return False


def get_compute():
    try:
        cpu_cores = psutil.cpu_count(logical=True)
    except Exception as e:
        logger.error(f"Error obtaining CPU core count: {e}")
        cpu_cores = 0
        return cpu_cores, False
    return cpu_cores, True


def get_memory():
    try:
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    except Exception as e:
        logger.error(f"Error obtaining RAM: {e}")
        ram_gb = 0
        return ram_gb, False
    return ram_gb, True


def storage():
    try:
        partitions = psutil.disk_partitions()
        if partitions:
            storage_gb = round(psutil.disk_usage(partitions[0].mountpoint).total / (1024 ** 3), 2)
        else:
            logger.error("No disk partitions found.")
            storage_gb = None
    except PermissionError:
        logger.error("Permission error while accessing disk info.")
        storage_gb = None
    except Exception as e:
        logger.error(f"Error obtaining storage: {e}")
        storage_gb = None

    return str(storage_gb)


def get_additional_info():
    logger.info(run_command('lscpu'))
    logger.info(run_command('cat /proc/meminfo'))

def os_info():
    os_support = False
    os_info = distro.name()
    os_architecture = platform.architecture()[0]
    logger.info("os_info:"+ os_info)
    logger.info("os_arch:" + os_architecture)

    try:
        os_release = run_command('cat /etc/os-release')
        if "ubuntu" in os_release.lower():
            os_support = check_ubuntu()
        elif "centos" in os_release.lower() or "rhel" in os_release.lower() or "oracle linux" in os_release.lower():
            os_support = check_centos_rhel_ol()
        elif "amazon linux" in os_release.lower():
            os_support = check_amazon_linux()
        else:
            os_support = False
    except Exception as e:
        print("An error occurred:", str(e))

    if os_architecture != '64bit':
        os_support = False

    return os_info, os_architecture, os_support


def log_format(msg, _type):
    if _type:
        return "{}{}{}".format(config.OK, msg, config.ENDC)
    else :
        return "{}{}{}".format(config.FAIL, msg, config.ENDC)


def calculate_size(s):
    last_char = s[-1].lower()
    if last_char == 't':
        return int(s[:-1]) * 1000
    elif last_char == 'g':
        return int(s[:-1])
    else:
        return 0


def get_storage_details(_storage, _type):
    try:
        # Execute lsblk command and capture its output
        result = subprocess.run(['lsblk', '-dno', 'NAME,ROTA,SIZE'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        logger.info(result)
        # Dictionary to store memory type against each device
        memory_types = []

        for line in lines:  # Skip header row
            if not line.startswith('sd'):
                continue
            memory_type = {}
            name, rota, size = line.split()
            memory_type['name'] = name
            memory_type['type'] = 'HDD' if rota == '1' else 'SSD'
            memory_type['size'] = calculate_size(size)
            logger.info("memory_type check")
            storage_supported = [item['name'] for item in _storage if memory_type['size'] >= int(item['size'])]
            logger.info("storage_supported check")
            storage_supported = ', '.join(storage_supported)
            logger.info("join")
            if memory_type['type'].lower() != _type.lower():
                storage_result = log_format('Storage Type not matched.', False)
                storage_recommendation = log_format('Upgrade storage to ' + _type, False)
            else:
                storage_result = f"{log_format('Supports', True)} {storage_supported} " \
                    if len(storage_supported) > 0 else log_format('Failed. Does not support any type', False)
                storage_recommendation = 'NA' if len(storage_supported) > 0 \
                    else log_format('Storage size upgrade required.', False)

            memory_type['result'] = storage_result
            memory_type['recommendation'] = storage_recommendation
            memory_types.append(memory_type)
        return memory_types, True

    except Exception as e:
        logger.info(e)
        return [], False
