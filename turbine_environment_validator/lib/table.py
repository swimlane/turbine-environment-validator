#!/usr/bin/env python3
from prettytable import PrettyTable
import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
import turbine_environment_validator.lib.verify_system_spec as verify_system_spec
import json
logger = log_handler.setup_logger()

def write_log(f, s):
    print(s)
    f.write(s.replace('\033[91m', '').replace('\033[92m', '').replace('\033[93m', '').replace('\033[0m', ''))
    f.write("\n")


def print_table(checks):
    f = open(config.LOG_FILE_NAME, "a")

    x = PrettyTable()
    x.title = 'Prerequisites'
    x.field_names = ['Check', 'Message', 'Result']
    for k,v in checks['prerequisites'].items():
        row = [k, v['message'], v['result']]
        x.add_row(row)
    write_log(f, x.get_string())

    # compute table
    if config.COMPUTE:
        x = PrettyTable()
        x.title = 'Compute'
        x.field_names = ['# cores available', 'Message', 'Recommendation']
        row = list(checks['compute'].values())
        x.add_row(row)
        write_log(f, x.get_string())

    # memory table
    if config.MEMORY:
        x = PrettyTable()
        x.title = 'Memory'
        x.field_names = ['# GB available', 'Message', 'Recommendation']
        row = list(checks['memory'].values())
        x.add_row(row)
        write_log(f, x.get_string())

    # storage table
    if config.STORAGE:
        x = PrettyTable()
        x.title = 'storage'
        x.field_names = ['Device', 'Type', 'Size (GB)', 'Message', 'Recommendation']
        for _row in checks['storage']:
            x.add_row(_row.values())
        write_log(f, x.get_string())

    # if config.arguments.verify_disk_space:
    if config.DIRECTORY_SIZES:
        x = PrettyTable()
        x.title = 'Directory Sizes'
        x.field_names = ['Directory', 'Total Space Size (GB)', 'Percentage Used', 'Message', 'Minimum Requirement (GB)', 'Result']
        for k,v in checks['directory_size_checks'].items():
            row = [*v.values()]
            row.insert(0,k)
            x.add_row(row)
        write_log(f, x.get_string())

    if config.DIRECTORY_MOUNT:
        x = PrettyTable()
        x.title = 'Mount Info'
        x.field_names = ['Directory', 'Message', 'Result']
        for k,v in checks['is_own_partition_checks'].items():
            row = [*v.values()]
            row.insert(0,k)
            x.add_row(row)
        write_log(f, x.get_string())

    if config.NETWORK:
        x = PrettyTable()
        x.title = 'Network Info'
        x.field_names = ['Proxy Scheme', 'Proxy Address']
        for scheme in checks['http_proxy_config']:
            row = [scheme, checks['http_proxy_config'][scheme]]
            x.add_row(row)
        write_log(f, x.get_string())

    #
    # if config.arguments.verify_lb:
    if config.LB_CONNECTIVITY_ENDPOINTS:
        x = PrettyTable()
        x.title = 'Load Balancer'
        x.field_names = ['Endpoint', 'Message', 'Result']
        for k,v in checks['load_balancer_port_checks'].items():
            row = [*v.values()]
            row.insert(0,k)
            x.add_row(row)
        write_log(f, x.get_string())

    # if config.arguments.verify_public_endpoints and not config.arguments.offline:
    if config.FIREWALL:
        x = PrettyTable()
        x.title = 'Firewall'
        x.field_names = ['Endpoint', 'Status Code', 'Result']
        for k,v in checks['public_endpoint_checks'].items():
            row = [*v.values()]
            row.insert(0,k)
            x.add_row(row)
        write_log(f, x.get_string())

    if config.NTP:
        x = PrettyTable()
        x.title = 'Time Syncing Services'
        x.field_names = ['Service', 'Running', 'Enabled']
        for k,v in checks['ntp_checks'].items():
            row = [*v.values()]
            row.insert(0,k)
            x.add_row(row)
        write_log(f, x.get_string())

    #

    x = PrettyTable()
    x.title = 'Operating System Info'
    x.field_names = ['Name', 'Version', 'Message', 'Result']
    row = checks['os_details'].values()
    x.add_row(row)
    write_log(f, x.get_string())

    if config.DISALLOWED_EXECUTABLES:
        x = PrettyTable()
        x.title = 'Disallowed Executables'
        x.field_names = ['Executable', 'Path ','Message', 'Result']
        for k,v in checks['disallowed_executables'].items():
            row = [*v.values()]
            row.insert(0,k)
            x.add_row(row)
        write_log(f, x.get_string())

    if config.DNS:
        x = PrettyTable()
        x.title = 'DNS lookup'
        x.field_names = ['Domain', 'Lookup', 'Reverse Lookup', 'Message']
        ind = True
        for item in checks['dns']:
            if ind:
                row = [config.DNS,item['lookup'], item['reverse_lookup'], item['message']]
                ind = False
            else:
                row = ["",item['lookup'], item['reverse_lookup'], item['message']]
            x.add_row(row)
        write_log(f, x.get_string())



    # if config.arguments.verify_intra_cluster_ports and config.arguments.additional_node_fqdn:
    #     field_names = config.INTRA_CLUSTER_PORTS
    #     field_names.insert(0,'Node')
    #     x = PrettyTable()
    #     x.title = 'Intra-Cluster Communication'
    #     x.field_names = field_names
    #     for k,v in checks['intra_port_connectivity'].items():
    #         row = [*v.values()]
    #         row.insert(0,k)
    #         x.add_row(row)
    #     print(x.get_string())


    write_log(f, "|{}|".format('-'*141))
    write_log(f, "|{:^150}|".format('{}!!! Additional Manual Checks !!!{}'.format(config.WARNING, config.ENDC)))
    write_log(f, "|{:^150}|".format('{}Each SPI Node must have a unique hostname as determined by hostnamectl.{}'.format(config.WARNING, config.ENDC)))
    write_log(f, "|{:^150}|".format('{}Each SPI Node should have DNS-resolvable hostnames.{}'.format(config.WARNING, config.ENDC)))
    write_log(f, "|{:^150}|".format('{}Each SPI Node must have reliable and consistent time. An NTP daemon is recommended.{}'.format(config.WARNING, config.ENDC)))
    write_log(f, "|{}|".format('_'*141))

    logger.info("Reading additional cpu and memory information and writing to log file.")
    f.write(verify_system_spec.run_command('lscpu'))
    f.write("\n")
    f.write(verify_system_spec.run_command('cat /proc/meminfo'))
    f.write("\n")
    f.write("---Logging System and Network Specifications files used---\n")
    f.write("\n")
    f.write(json.dumps(config.SYSTEM_SPEC, indent = 1))
    f.write("\n")
    f.write(json.dumps(config.NETWORK_SPEC, indent = 1))

    _log = "Log File "+ config.LOG_FILE_NAME + " stored!"
    log_file_msg = "{}{}{}".format(config.WARNING, _log, config.ENDC)
    write_log(f, log_file_msg)

    f.close()
