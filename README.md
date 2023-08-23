# Turbine-environment-validator
## Overview
This package contains everything you need to verify and ensure that your system adheres to specific requirements and configurations. The installer provided will perform checks on a Linux system using configurations provided in the system.json and network.json files. It can validate against the provided JSON schema files to ensure the correctness of configurations.

This binary will run through various checks for the Turbine Platform Installer. It is designed to be run by the customer to verify their environment before engaging PS for the installation. This script is highly configurable, with various options to skip checks. Most checks are enabled by default. See `turbine-environment-validator verify --help` for more information.

## Package Contents
* turbine-environment-validator: The main executable that performs system and network checks.
* system.json: Contains specifications related to the system such as compute, memory, storage, operating system support, directory requirements, and more.
* network.json: Specifies network-related configurations, including proxy settings, load balancer configurations, firewall configurations, NTP services, DNS configuration, and intra-cluster ports.
* system.schema.json: JSON schema for the system.json file. Ensures the structure and correctness of the configuration provided in the system.json file.
* network.schema.json: JSON schema for the network.json file. Ensures the structure and correctness of the configuration provided in the network.json file.

## Usage
If preparing for a new Swimlane installation.
For CentOS / Red Hat:
```
yum update -y
yum -y install centos-release-scl wget
yum -y install rh-python36
scl enable rh-python36 bash
yum install -y bind-utils
```

For Ubuntu:
```
apt -y install build-essential libssl-dev libffi-dev python-dev
apt -y install python3-pip dnsutils
pip install virtualenv
```

And finally, for either Ubuntu or CentOS / Red Hat:
```
wget https://github.com/swimlane/turbine-environment-validator/releases/download/1.0.0/turbine-environment-validator
chmod +x ./turbine-environment-validator
./turbine-environment-validator verify
```

### Running the Installer
- To run the installer using the default system.json and network.json shipped with the package:
`./turbine-environment-validator verify`
- If you want to use custom configuration files, specify them using the --system-spec and --network-spec options:
`./turbine-environment-validator verify --system-spec /path/to/custom_system.json --network-spec /path/to/custom_network.json`
- For the Load Balancer Listener daemon:
`./turbine-environment-validator listener`

## Arguments
- --use-color: Enable or disable ANSI color codes. Useful for CI or non-interactive terminals.
- version: Print the version and then exit.
- verify: Run the environment verifier.
    - --system-spec: Path to System Specification JSON file (Default: system.json in the package directory).
    - --network-spec: Path to Network Specification JSON file (Default: network.json in the package directory).
    - --offline: Run in Offline mode. Disable any online checks.
    - --enable-listeners: Enable listeners if your load balancer has no healthy nodes.
- listener: Load Balancer Listener daemon.
    - --lb-fqdn: Load Balancer FQDN (Default is the hostname of the node running the verifier script).
    - --network-spec: Path to Network Specification JSON file (Default: network.json in the package directory).


## Configuration GUI for system.json and network.json
While advanced users can directly edit the `system.json` and `network.json` using their preferred text editor, we understand that not everyone is comfortable with direct JSON editing. To simplify this process and make the configuration accessible to users of all technical levels, we've enabled a GUI-based approach. Users can now use the provided JSON schema files (system.schema.json and network.schema.json) on an online JSON editor for a more intuitive, visual configuration experience.

### Instructions
* Step 1: Access the Online JSON Editor
&emsp; Open your web browser and navigate to the [JSON Editor](https://json-editor.github.io/json-editor/).
* Step 2: Load the JSON Schema
&emsp;On the bottom of the JSON Editor page, you'll see a textarea. In the schema text area, load the contents of either system.schema.json or network.schema.json depending on which configuration you're aiming to create or modify.
Click on the "Update Schema" button. 
* Step 3: Create/Edit the Configuration
&emsp;Once the schema is loaded, the editor will present you with a GUI form based on the structure of the schema.
Fill in the necessary fields or modify existing ones as per your requirements. The editor will provide feedback and validations based on the schema, ensuring that you're creating a valid configuration.
* Step 4: Export the Configuration
&emsp;After making the necessary changes, save the generated system.json or network.json file and proceed with using the installer or any other steps as instructed.

### Note
Please ensure that the configurations are accurate and meet the requirements of your environment. If unsure, refer back to the main README.

## Known Issues:
On some operating systems, the script will fail with `error while loading shared libraries: libz.so.1: failed to map segment from shared object: Operation not permitted`. This occur usually if you are running the script as root and the `/tmp` directory is mounted with `noexec`. To work around this, you can either run the script as a non-root user, or you can set the `TMPDIR` environment variable to a writable and executable directory.

`turbine-environment-validator` is a [Swimlane](https://swimlane.com) open-source project; we believe in giving back to the open-source community by sharing some of the projects we build for our application. Swimlane is an automated cyber security operations and incident response platform that enables cyber security teams to leverage threat intelligence, speed up incident response and automate security operations.