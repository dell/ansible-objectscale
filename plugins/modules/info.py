#!/usr/bin/python
# Copyright: (c) 2025, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering information from Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: info

version_added: '1.0.0'

short_description: Gather information about Dell ObjectScale entities

description:
- Gather information about Dell ObjectScale entities such as namespaces.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

options:
  objectscale_host:
    description:
    - IP address or FQDN of the ObjectScale management endpoint.
    type: str
    required: true

  objectscale_port:
    description:
    - Port number for the ObjectScale management endpoint.
    type: int
    default: 4443
    required: false

  objectscale_username:
    description:
    - Username for authenticating with the ObjectScale management endpoint.
    type: str
    required: true

  objectscale_password:
    description:
    - Password for authenticating with the ObjectScale management endpoint.
    type: str
    required: true

  validate_certs:
    description:
    - Boolean value to enable or disable SSL certificate verification.
    - Set to C(false) when certificates are not trusted.
    type: bool
    default: true
    required: false

  timeout:
    description:
    - Timeout in seconds for HTTP requests to the ObjectScale management endpoint.
    type: int
    default: 30
    required: false

  gather_subset:
    description:
    - List of string variables to specify the entities for which information
      should be gathered.
    - C(namespace) - returns list of all namespaces.
    type: list
    elements: str
    choices: ['namespace']
    required: true

notes:
- The I(check_mode) is not supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Gather namespace information
  dellemc.objectscale.info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    gather_subset:
      - namespace
  register: objectscale_info

- name: Display all namespaces
  debug:
    var: objectscale_info.Namespaces
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: false

Namespaces:
    description: List of namespaces on the ObjectScale system.
    returned: When namespace is in gather_subset
    type: list
    elements: dict
    contains:
        id:
            description: Unique namespace identifier.
            type: str
        name:
            description: Name of the namespace.
            type: str
        default_data_services_vpool:
            description: Default replication group for the namespace.
            type: str
        is_compliance_enabled:
            description: Whether compliance (WORM) mode is enabled.
            type: bool
        is_encryption_enabled:
            description: Whether server-side encryption is enabled.
            type: bool
    sample:
        [
            {
                "id": "testnamespace",
                "name": "testnamespace",
                "default_data_services_vpool": "urn:storageos:ReplicationGroupInfo:xxxx:global",
                "is_compliance_enabled": false,
                "is_encryption_enabled": false
            }
        ]
'''

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespaces_response import (
        NamespaceServiceGetNamespacesResponse,
    )

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespaces_response import (
        NamespaceServiceGetNamespacesResponse,
    )
except (ImportError, Exception):
    NamespaceApi = None  # type: ignore[assignment,misc]
    NamespaceServiceGetNamespacesResponse = None  # type: ignore[assignment,misc]


class ObjectScaleInfo(object):
    """Class for gathering information from ObjectScale"""

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(dict(
            gather_subset=dict(
                type='list',
                elements='str',
                required=True,
                choices=['namespace']
            )
        ))

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=False
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.namespace_api: NamespaceApi = NamespaceApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

        self.module.log('Connected to ObjectScale at %s' % self.module.params['objectscale_host'])

    def get_namespaces(self) -> Optional[List[Dict[str, Any]]]:
        """Get all namespaces from ObjectScale."""
        try:
            response: NamespaceServiceGetNamespacesResponse = (
                self.namespace_api.namespace_service_get_namespaces()
            )
            return [
                ns.to_dict() for ns in (response.namespace or [])
            ]
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Getting namespace list failed with error: %s" % error_msg
            self.module.exit_json(failed=True, msg=msg)

    def perform_module_operation(self) -> None:
        """Gather requested information and return results."""
        result: Dict[str, Any] = dict(changed=False)

        gather_subset = self.module.params['gather_subset']

        if 'namespace' in gather_subset:
            result['Namespaces'] = self.get_namespaces()

        self.module.exit_json(**result)


def main() -> None:
    """Create ObjectScaleInfo object and gather information."""
    obj = ObjectScaleInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
