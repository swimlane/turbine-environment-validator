import subprocess
import os
import shutil
import re


def install_nslookup():
    """
    Installs nslookup based on the package manager present.
    """
    try:
        if os.path.exists('/usr/bin/apt'):
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'dnsutils'], check=True)
        elif os.path.exists('/usr/bin/yum'):
            subprocess.run(['sudo', 'yum', 'install', '-y', 'bind-utils'], check=True)
        else:
            raise EnvironmentError("Unsupported OS or package manager.")
    except subprocess.CalledProcessError:
        raise EnvironmentError("Failed to install nslookup.")


def check_nslookup():
    """
    Check if nslookup is present. If not, install it.
    """
    if not shutil.which("nslookup"):
        install_nslookup()


def nslookup(domain):
    """
    Runs nslookup for a domain and returns the results in the specified format.
    """
    cmd = ['nslookup', domain]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        return [{"lookup": "No lookup IP found", "reverse_lookup": "-", "message": "Failed"}]

    lines = result.stdout.splitlines()
    ips = []

    ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    ips = [ip_pattern.search(line.decode()).group() for line in lines if ip_pattern.search(line.decode())]
    ips = filter(lambda ip: not ip.startswith('127'), ips)

    # if no valid IPs are found, return failure
    if not ips:
        return [{"lookup": "No lookup IP found", "reverse_lookup": "-", "message": "Failed"}]

    ips = list(set(ips))
    results = []

    for ip in ips:
        names = reverse_nslookup(ip)
        if names:
            results.append({"lookup": ip, "reverse_lookup": names[0].strip(), "message": "-"})
        else:
            results.append({"lookup": ip, "reverse_lookup": "-", "message": "Reverse lookup not found"})

    return results


def reverse_nslookup(ip):
    """
    Performs a reverse lookup for an IP address and returns the names.
    """
    cmd = ['nslookup', ip]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        return []

    lines = result.stdout.splitlines()
    names = []
    for line in lines:
        line = str(line)
        if "name" in line.lower():
            name = line.split()[-1]
            names.append(name)
    return names
