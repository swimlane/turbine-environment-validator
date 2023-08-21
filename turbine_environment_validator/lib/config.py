#!/usr/bin/env python3
import os
import sys
import argparse
import socket
import json
import datetime

import turbine_environment_validator.lib.log_handler as log_handler
logger = log_handler.setup_logger()

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_executable_dir():
    """ Return the directory containing the running executable. """
    return os.path.dirname(sys.executable)


parser = argparse.ArgumentParser()
parser.add_argument("--use-color", type=str2bool, default=True,
                        help="Enable or Disable ANSI color codes. Useful for CI or non-interactive terminals.")

commands = parser.add_subparsers(dest='command')

version_action = commands.add_parser('version', help="Print the version and then exit.")

verify_action = commands.add_parser('verify', help="Run the environment verifier.")

listener_action = commands.add_parser('listener', help="Load Balancer Listener daemon.")

verify_action.add_argument("--system-spec", type=str, default=os.path.join(get_executable_dir(), 'system.json'),
                        help="path to System Specification JSON file")

verify_action.add_argument("--network-spec", type=str, default=os.path.join(get_executable_dir(), 'network.json'),
                       help="path to Network Specification JSON file")


listener_action.add_argument("--lb-fqdn", type=str, default=socket.gethostname(),
                        help="Load Balancer FQDN. Default is the hostname of the node running the verifier script.")

verify_action.add_argument("--offline", type=str2bool, default=False,
                        help="Run in Offline mode.")

verify_action.add_argument("--external-mongo", type=str2bool, default=False,
                        help="Standalone/ Atlas based MongoDB.")

verify_action.add_argument("--enable-listeners", type=str2bool, default=True,
                        help="Enable listeners if your load balancer has no healthy nodes.")

listener_action.add_argument("--network-spec", type=str, default=os.path.join(get_executable_dir(), 'network.json'),
                       help="path to Network Specification JSON file")

arguments = parser.parse_args()

if arguments.command == 'version':
    from .. import __version__
    print(__version__.__version__)
    sys.exit(0)

if arguments.command is None:
    parser.print_help()
    sys.exit(1)

if arguments.use_color:
    #Terminal ANSI color codes
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
else:
    OK = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''


def load_spec(spec):
    try:
        with open(spec, 'r') as file:
            spec_data = json.load(file)
        return spec_data
    except Exception as e:
        logger.error('error loading ' + spec + ' file. Please pass valid file')
        sys.exit(1)


def get_spec(key):
    _data = SYSTEM_SPEC.get(key, [])
    if not _data:
        return _data
    if arguments.external_mongo or SYSTEM_SPEC['external_mongodb'].lower() == "yes":
        data = _data['default_ext_mongo']
    else:
        data = _data['default']
    return data


if not arguments.network_spec:
    logger.info('No Network Specifications file provided. Reading Specifications from default file.')
    arguments.network_spec = 'network.json'

LB_CONNECTIVITY_PORTS = [
    6443,
    443,
    8800,
    4443
]
NETWORK_SPEC = load_spec(arguments.network_spec)

current_datetime = datetime.datetime.now()

formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

LOG_FILE_NAME = "PRE_INSTALL_CHECK_{}.txt".format(formatted_datetime)

if arguments.command == 'verify':

    if not arguments.system_spec:
        logger.info('No System Specifications file provided. Reading Specifications from default file.')
        arguments.system_spec = 'system.json'

    SYSTEM_SPEC = load_spec(arguments.system_spec)


    COMPUTE = get_spec('compute')
    MEMORY = get_spec('memory')
    STORAGE = get_spec('storage')

    DIRECTORY_SIZES = SYSTEM_SPEC.get('directory', [])
    DIRECTORY_MOUNT = SYSTEM_SPEC.get('directory_mount', [])
    DISALLOWED_EXECUTABLES = SYSTEM_SPEC.get('disallowed_executables', [])

    ALLOWED_OS = {
        "ubuntu": [],
        "redhat": []
    }

    for item in SYSTEM_SPEC.get('os', []):
        flavour = item['flavour'].lower()
        version = item['version']

        if flavour == 'ubuntu':
            ALLOWED_OS['ubuntu'].append(version)
        elif flavour in ['rhel', 'centos', 'oracle']:
            ALLOWED_OS['redhat'].append(version)

    ALLOWED_OS['ubuntu'] = list(sorted(set(ALLOWED_OS['ubuntu'])))
    ALLOWED_OS['redhat'] = list(sorted(set(ALLOWED_OS['redhat'])))

    NETWORK = {
        'http': None,
        'https': None,
        'ftp': None
    }
    _NETWORK = NETWORK_SPEC.get('network', []).get('proxy', [])
    for item in _NETWORK:
        scheme = item['proxy_scheme']
        address = item['proxy_address']

        if scheme in NETWORK:
            NETWORK[scheme] = address

    LOAD_BALANCER = NETWORK_SPEC.get('load_balancer', [])
    FIREWALL = NETWORK_SPEC.get('firewall', [])

    NTP = NETWORK_SPEC.get('ntp', [])
    INTRA_CLUSTER_PORTS = NETWORK_SPEC.get('intra_cluster_ports')
    DNS = NETWORK_SPEC.get('dns', "")

    lb_scheme = "https"
    lb_fqdn = socket.gethostname()
    LB_CONNECTIVITY_ENDPOINTS = []
    for item in LOAD_BALANCER:
        lb_endpoint = '{}://{}:{}/{}'.format(item.get('lb-schema', 'https'), item.get('lb-fqdn', socket.gethostname()), item.get('lb-port'), item.get('lb-endpoint'))
        LB_CONNECTIVITY_ENDPOINTS.append(lb_endpoint)

if arguments.command == 'listener':
    INTRA_CLUSTER_PORTS = NETWORK_SPEC.get('intra_cluster_ports')
