import os
import subprocess
import psutil

import turbine_environment_validator.lib.log_handler as log_handler
logger = log_handler.setup_logger()


def is_root():
    return os.geteuid() == 0


def is_in_sudo_group():
    try:
        output = subprocess.check_output("groups", shell=True).decode()
        return "sudo" in output or "wheel" in output
    except:
        return False


def has_sudo_rights():
    try:
        # Check if the user can run sudo without password
        output = subprocess.check_output("sudo -l", shell=True, stderr=subprocess.STDOUT).decode()
        if "not allowed" in output:
            return False
        else:
            return True
    except:
        return False


def is_user_admin():
    if is_root() or is_in_sudo_group() or has_sudo_rights():
        return True
    else:
        return False


def is_numa_disabled():
    try:
      numa_enabled = os.path.exists("/sys/devices/system/node/node0/numa_enabled")
      return True if not numa_enabled else False
    except:
      return False


def is_ip_forwarding_enabled():
    try:
        output = subprocess.check_output("sysctl -a", shell=True, stderr=subprocess.STDOUT).decode()
        if "net.ipv4.ip_forward = 1" in output:
            return True, "-"
        else:
            return False, "Enable IP forwarding in /etc/sysctl.conf"
    except:
        return False, "Linux command sysctl failed"


def is_swapping_disabled():
    try:
        swap = psutil.swap_memory()
        if swap.total > 0:
            return False, "Disable Swap memory in /etc/fstab"
        else:
            return True, "-"
    except:
        return False, "Checking for Swap memory failed"
