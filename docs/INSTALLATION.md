# Installation and execution of Ansible modules for Dell ObjectScale

## Prerequisites

Before installing the Ansible modules for Dell ObjectScale, ensure the following requirements are met:

- **Ansible**: Version 2.15 or later
- **Python**: Version 3.9 or later
- **pip**: Python package manager
- **Dell ObjectScale**: Version 4.3 or later with management endpoint accessible

## Installation of Dependencies

The ObjectScale Ansible collection uses a vendored OpenAPI-generated client library. All required Python dependencies are specified in `requirements.txt`.

### Install Python Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install:
- `packaging` - Package version handling
- `urllib3>=2.7.0` - HTTP client library
- `certifi>=14.5.14` - SSL certificate handling
- `python-dateutil>=2.7.0` - Date/time utilities
- `typing_extensions>=4.6.1` - Type hints support
- `pydantic>=2.0.0` - Data validation

**Note**: The ObjectScale client library is vendored in `plugins/module_utils/objectscale_client/` and does not require separate installation.

## Building collections

Build the collection from source code using this command:

```bash
ansible-galaxy collection build
```

For more details on how to build a tar ball, please refer to: [Building the collection](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_distributing.html#building-your-collection-tarball)

## Installing collections

### Online installation of collections

Install the latest collection hosted in [Ansible Galaxy](https://galaxy.ansible.com/dellemc/objectscale):

```bash
ansible-galaxy collection install dellemc.objectscale -p <install_path>
```

### Offline installation of collections

Download the latest tar build from [Ansible Galaxy](https://galaxy.ansible.com/dellemc/objectscale) or [Automation Hub](https://console.redhat.com/ansible/automation-hub/repo/published/dellemc/objectscale) and install it:

```bash
ansible-galaxy collection install dellemc-objectscale-1.0.0.tar.gz -p <install_path>
```

Set the environment variable to include the installation path:

```bash
export ANSIBLE_COLLECTIONS_PATHS=$ANSIBLE_COLLECTIONS_PATHS:<install_path>
```

## Using collections

### Collection import in playbooks

To use any Ansible module, ensure that the proper FQCN (Fully Qualified Collection Name) is embedded in the playbook:

```yaml
collections:
  - dellemc.objectscale
```

### Using modules in tasks

Use the proper FQCN (Fully Qualified Collection Name) before the module name in tasks. Refer to this example:

```yaml
tasks:
  - name: Get namespace details
    dellemc.objectscale.namespace_info:
      objectscale_host: "{{ objectscale_host }}"
      objectscale_username: "{{ objectscale_username }}"
      objectscale_password: "{{ objectscale_password }}"
      validate_certs: "{{ validate_certs }}"
```

### Generating Ansible documentation

Generate Ansible documentation for a specific module using the FQCN:

```bash
ansible-doc dellemc.objectscale.namespace_info
```

## Ansible modules execution

The Ansible server must be configured with the ObjectScale Ansible collection and Python dependencies to run the playbooks. The [module documentation](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/) provides detailed information on different Ansible modules, their functions, and syntax.

### ObjectScale Management Endpoint Configuration

Each module requires the following parameters to connect to the ObjectScale management endpoint:

- **objectscale_host** (required): IP address or FQDN of the ObjectScale management endpoint
- **objectscale_port** (optional): Port number for the management endpoint (default: 4443)
- **objectscale_username** (required): Username for authentication
- **objectscale_password** (required): Password for authentication
- **validate_certs** (optional): Enable or disable SSL certificate verification (default: true)
- **timeout** (optional): Timeout in seconds for HTTP requests (default: 30)

### Example playbook

Create a playbook file (e.g., `objectscale_example.yml`):

```yaml
---
- name: Manage Dell ObjectScale resources
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    objectscale_host: "10.0.0.1"
    objectscale_username: "admin"
    objectscale_password: "password"
    validate_certs: false

  tasks:
    - name: Get VDC information
      dellemc.objectscale.vdc_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
      register: vdc_info

    - name: Display VDC details
      ansible.builtin.debug:
        var: vdc_info
```

Run the playbook:

```bash
ansible-playbook objectscale_example.yml
```

## SSL certificate validation

### Using custom CA certificates

If your ObjectScale management endpoint uses a custom CA certificate:

1. Copy the CA certificate to the "/etc/pki/ca-trust/source/anchors" path:

```bash
sudo cp /path/to/ca-certificate.crt /etc/pki/ca-trust/source/anchors/
```

2. Set the "REQUESTS_CA_BUNDLE" environment variable:

```bash
export REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/ca-certificate.crt
```

3. Update the CA trust store:

```bash
sudo update-ca-trust extract
```

4. In your playbook, set `validate_certs: true` to enable certificate validation.

### Disabling certificate validation

For development or testing environments with self-signed certificates, you can disable certificate validation:

```yaml
validate_certs: false
```

**Warning**: Disabling certificate validation is not recommended for production environments.

## Results

Each module returns the updated state and details of the entity. For example, the namespace module returns the updated details of the namespace. Sample results are shown in each module's documentation.

## Ansible execution environment

Ansible can also be installed in a container environment. Ansible Builder provides the ability to create reproducible, self-contained environments as container images that can be run as Ansible execution environments.

### Building a container image

1. Install the ansible builder package:

```bash
pip3 install ansible-builder
```

2. Ensure the `execution-environment.yml` is at the root of the collection and create the execution environment:

```bash
ansible-builder build --tag objectscale-ee:latest --container-runtime docker
```

3. After the image is built, run the container:

```bash
docker run -it objectscale-ee:latest /bin/bash
```

4. Verify collection installation:

```bash
ansible-galaxy collection list
```

5. Run a playbook in the container:

```bash
docker run --rm -v $(pwd):/runner objectscale-ee:latest ansible-playbook objectscale_example.yml
```

## Development Setup

For developers who want to contribute to the ObjectScale Ansible collection:

### Install development dependencies

```bash
pip install -r dev-requirements.txt
```

### Generate client library from OpenAPI spec

The ObjectScale client library is generated from the OpenAPI specification. To regenerate it:

```bash
make generate
```

This command:
1. Downloads the OpenAPI generator CLI
2. Filters the OpenAPI specification to include only required APIs
3. Generates the Python client library
4. Formats and validates the generated code

### Run linting

```bash
make lint
```

### Run unit tests

```bash
make test
```

### Generate module documentation

```bash
make docs
```

This generates simplified RST documentation for all modules in the `docs/modules/` directory.

## Troubleshooting

### Connection errors

If you encounter connection errors to the ObjectScale management endpoint:

1. Verify the `objectscale_host` and `objectscale_port` are correct
2. Ensure network connectivity to the management endpoint
3. Check firewall rules allow access to the management endpoint port (default: 4443)
4. Verify credentials are correct

### SSL certificate errors

If you encounter SSL certificate validation errors:

1. Verify the CA certificate is properly installed (see SSL certificate validation section)
2. Check that `REQUESTS_CA_BUNDLE` environment variable is set correctly
3. Try disabling certificate validation temporarily for testing: `validate_certs: false`

### Module not found errors

If you encounter "module not found" errors:

1. Verify the collection is installed: `ansible-galaxy collection list`
2. Check that the FQCN is correct in your playbook
3. Verify `ANSIBLE_COLLECTIONS_PATHS` environment variable includes the installation path

### Import errors

If you encounter import errors related to dependencies:

1. Verify all dependencies are installed: `pip list`
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check Python version compatibility (3.9+)

## Support

For issues, questions, or contributions, please refer to:

- [GitHub Issues](https://github.com/dell/ansible-objectscale/issues)
- [Dell Community Forum](https://www.dell.com/community/Automation/bd-p/Automation)
- [Ansible Forum](https://forum.ansible.com/)
