#!/usr/bin/env python3
import time
import logging


import turbine_environment_validator.lib.config as config
import turbine_environment_validator.lib.log_handler as log_handler
import turbine_environment_validator.lib.verify_disk_space as verify_disk_space
import turbine_environment_validator.lib.verify_load_balancer as verify_load_balancer
import turbine_environment_validator.lib.verify_ntp as verify_ntp
import turbine_environment_validator.lib.verify_public_endpoints as verify_public_endpoints
import turbine_environment_validator.lib.verify_executables as verify_executables
import turbine_environment_validator.lib.verify_cluster_ports as verify_cluster_ports
import turbine_environment_validator.lib.verify_system_spec as verify_system_spec
import turbine_environment_validator.lib.verify_prerequisites as verify_prerequisites
import turbine_environment_validator.lib.http_listener as http_listener
import turbine_environment_validator.lib.table as table
import turbine_environment_validator.lib.verify_dns as verify_dns


logger = log_handler.setup_logger()

FileOutputHandler = logging.FileHandler(config.LOG_FILE_NAME)
logger.addHandler(FileOutputHandler)

check_results = {
    "checks": {
        "compute": {},
        "memory": {},
        "storage": [],
        "os_details": {},
        "check_system_specs": {},
        "prerequisites": {},
        "memory_checks": {},
        "directory_size_checks": {},
        "is_own_partition_checks": {},
        "load_balancer_port_checks": {},
        "pip_checks": {},
        "swimlane_certificate_checks": {},
        "kots_certificate_checks": {},
        "additional_certificate_checks": {},
        "public_endpoint_checks": {},
        "ntp_checks": {},
        "hostnamectl_checks": {},
        "disallowed_executables": {},
        "intra_port_connectivity": {},
        "http_proxy_config": {},
        "dns":[],
        "additional_info": {}
    }
}


def log_format(msg, _type):
    if _type:
        return "{}{}{}".format(config.OK, msg, config.ENDC)
    else :
        return "{}{}{}".format(config.FAIL, msg, config.ENDC)


def main():
    logger.info('Starting Turbine Embedded Cluster environment verification...')

    if config.arguments.command == 'verify':

        # Prerequisites
        # Sudo user check
        sudo_check = verify_prerequisites.is_user_admin()
        sudo_message = "-" if sudo_check else "User should have Sudo access"

        check_results['checks']['prerequisites'].update({
            'Sudo/Root access': {
                "message": '-' if sudo_check else log_format(sudo_message, False),
                "result": log_format('Passed', True) if sudo_check else log_format('Failed', False),
            }
        })

        # NUMA check
        numa_check = verify_prerequisites.is_numa_disabled()
        numa_message = "-" if numa_check else "Disable NUMA in BIOS"
        check_results['checks']['prerequisites'].update({
            'NUMA (non-uniform memory access) disabled': {
                "message": '-' if numa_check else log_format(numa_message, False),
                "result":  log_format('Passed', True) if numa_check else log_format('Failed', False),
            }
        })

        # Compute check
        if config.COMPUTE:
            compute = config.COMPUTE
            cpu_available, check_cpu_status = verify_system_spec.get_compute()

            if not check_cpu_status:
                compute_check = {
                    '# cpu available': '-',
                    'Result': log_format('Error obtaining CPU core count', False),
                    'Recommendation': '-'
                }
            else:
                cpu_supported = [item['name'] for item in compute if cpu_available >= item['cpu']]
                cpu_supported = ', '.join(cpu_supported)
                compute_result = f"{log_format('Supports', True)} {cpu_supported} " if len(cpu_supported) > 0 else log_format('Failed. Does not support any type', False)
                compute_recommendation = '-' if len(cpu_supported) > 0 else log_format('CPU Upgrade required.', False )
                compute_check = {
                    '# cpu available': cpu_available,
                    'Result': compute_result,
                    'Recommendation': compute_recommendation
                }
            check_results['checks']['compute'].update(compute_check)

        # Memory check
        if config.MEMORY:
            memory = config.MEMORY
            memory_available, check_memory_status = verify_system_spec.get_memory()

            if not check_memory_status:
                memory_check = {
                    '# GB available': '-',
                    'Result': log_format('Error obtaining memory details', False),
                    'Recommendation': '-'
                }
            else:
                memory_supported = [item['name'] for item in memory if memory_available >= item['ram']]
                memory_supported = ', '.join(memory_supported)
                memory_result = f"{log_format('Supports', True)} {memory_supported} " if len(memory_supported) > 0 else log_format('Failed. Does not support any type', False)
                memory_recommendation = '-' if len(memory_supported) > 0 else log_format('Memory Upgrade required.', False )
                memory_check = {
                    '# GB available': memory_available,
                    'Result': memory_result,
                    'Recommendation': memory_recommendation
                }
            check_results['checks']['memory'].update(memory_check)

        # Storage Check
        if config.STORAGE:
            storage = config.STORAGE
            storage_type = config.SYSTEM_SPEC['storage'].get('type', 'ssd')
            storage_available, check_storage_status = \
                verify_system_spec.get_storage_details(storage, storage_type)

            if not check_storage_status:
                logger.error('storage checking failed. Does the OS support lsblk command? ')
                storage_available = [
                    {'name': '-', 'type': '-', 'size': '-',
                     'result': log_format('storage checking failed. Does the OS support lsblk command?', False),
                     'recommendation': '-'
                     }
                ]
            check_results['checks']['storage'] = storage_available

        os_info, os_architecture, os_support = verify_system_spec.os_info()
        os_recommendation = '-' if os_support else log_format('OS not supported.', False)

        os_details = {
            "info": f"{os_info} {os_architecture}",
            "message": os_recommendation,
            "result": log_format('Passed', True) if os_support else log_format('Failed', False)
        }
        check_results['checks']['os_details'] = os_details

        # Directory Sizes check
        if config.DIRECTORY_SIZES:
            check_results['checks']['directory_size_checks'].update(verify_disk_space.check_directory_size(config.DIRECTORY_SIZES))

        # Directory Mount Check
        if config.DIRECTORY_MOUNT:
            check_results['checks']['is_own_partition_checks'].update(verify_disk_space.check_if_mount(config.DIRECTORY_MOUNT))

        if config.DISALLOWED_EXECUTABLES:
            check_results['checks']['disallowed_executables'].update(verify_executables.check_installed_executables(config.DISALLOWED_EXECUTABLES))

        check_results['checks']['http_proxy_config'].update(config.NETWORK)

        # Endpoint check
        if config.FIREWALL and not config.arguments.offline:
            check_results['checks']['public_endpoint_checks'].update(
                verify_public_endpoints.check_endpoints(config.FIREWALL, config.NETWORK))

        # NTP Check
        if config.NTP:
            check_results['checks']['ntp_checks'].update(verify_ntp.get_service_status(config.NTP))

        if config.DNS:
            dns_res = verify_dns.nslookup(config.DNS)
            for res in dns_res:
                if res['reverse_lookup'] == '-':
                    res['message'] = log_format(res['message'], False)
            check_results['checks']['dns'] = dns_res

        # Load Balancer Check
        if config.LB_CONNECTIVITY_ENDPOINTS:
            http_listener.start_lb_listener_threads(config.LB_CONNECTIVITY_PORTS)
            logger.info('Sleeping for 90 seconds to allow LB to see that we are live')
            time.sleep(90)
            check_results['checks']['load_balancer_port_checks'].update(verify_load_balancer.verify_port_connectivity(config.LB_CONNECTIVITY_ENDPOINTS))

        table.print_table(check_results['checks'])

    if config.arguments.command == 'listener':
        http_listener.start_lb_listener_threads(config.LB_CONNECTIVITY_PORTS)
        http_listener.start_intra_cluster_listener_threads(config.INTRA_CLUSTER_PORTS)
        input("Web and Intra-Cluster Listeners are running, press enter to exit.")

if __name__ == "__main__":
    main()
