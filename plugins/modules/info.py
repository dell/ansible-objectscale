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
- Supports listing all namespaces and fetching namespace details by name.

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

  query_parameters:
    description:
    - Contains dictionary of query parameters for specific I(gather_subset).
    - Applicable to C(namespace).
    - Use C(query_parameters.namespace.name) to get a specific namespace.
    - Use C(query_parameters.namespace.match) to list namespaces by prefix
      with wildcard (for example C(team-*)).
    type: dict
    required: false

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

- name: Get namespace details by name
  dellemc.objectscale.info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    gather_subset:
      - namespace
    query_parameters:
      namespace:
        name: "testnamespace"
  register: objectscale_namespace

- name: List namespaces by name prefix
  dellemc.objectscale.info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    gather_subset:
      - namespace
    query_parameters:
      namespace:
        match: "team-*"
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
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_response import (
        NamespaceServiceGetNamespaceResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespaces_response import (
        NamespaceServiceGetNamespacesResponse,
    )

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_response import (
        NamespaceServiceGetNamespaceResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespaces_response import (
        NamespaceServiceGetNamespacesResponse,
    )
except (ImportError, Exception):
    NamespaceApi = None  # type: ignore[assignment,misc]
    NamespaceServiceGetNamespaceResponse = None  # type: ignore[assignment,misc]
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
            ),
            query_parameters=dict(type='dict', required=False),
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

        if NamespaceApi is None:
            self.module.exit_json(
                failed=True,
                msg="ObjectScale namespace API client is unavailable. Rebuild/install objectscale_client.",
            )

        namespace_api_cls = NamespaceApi

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.namespace_api = namespace_api_cls(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

        self.module.log('Connected to ObjectScale at %s' % self.module.params['objectscale_host'])

    def get_namespaces(self) -> Optional[List[Dict[str, Any]]]:
        """Get all namespaces from ObjectScale."""
        namespace_query = self._get_namespace_query_parameters()
        namespace_name = namespace_query.get('name')

        if namespace_name:
            namespace_details = self.get_namespace_details(namespace_name)
            return [namespace_details] if namespace_details else []

        list_kwargs: Dict[str, Any] = {}
        if namespace_query.get('limit') is not None:
            list_kwargs['limit'] = str(namespace_query.get('limit'))
        if namespace_query.get('marker') is not None:
            list_kwargs['marker'] = str(namespace_query.get('marker'))
        if namespace_query.get('match'):
            list_kwargs['name'] = str(namespace_query.get('match'))

        try:
            response: NamespaceServiceGetNamespacesResponse = (
                self.namespace_api.namespace_service_get_namespaces(**list_kwargs)
            )
            return [
                ns.to_dict() if hasattr(ns, 'to_dict') else ns
                for ns in (response.namespace or [])
            ]
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Getting namespace list failed with error: %s" % error_msg
            self.module.exit_json(failed=True, msg=msg)

    def get_namespace_details(self, namespace_name: str) -> Optional[Dict[str, Any]]:
        """Get namespace details by namespace name."""
        try:
            response = (
                self.namespace_api.namespace_service_get_namespace(id=namespace_name)
            )
            return response.to_dict() if hasattr(response, 'to_dict') else response
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            msg = "Getting namespace %s details failed with error: %s" % (
                namespace_name,
                error_msg,
            )
            self.module.exit_json(failed=True, msg=msg)

    def _get_namespace_query_parameters(self) -> Dict[str, Any]:
        """Extract and validate query parameters for namespace gather subset."""
        query_parameters = self.module.params.get('query_parameters')

        if query_parameters is None:
            return {}

        if not isinstance(query_parameters, dict):
            self.module.exit_json(
                failed=True,
                msg="query_parameters must be a dictionary.",
            )
            return {}

        namespace_query = query_parameters.get('namespace') or {}

        if namespace_query and not isinstance(namespace_query, dict):
            self.module.exit_json(
                failed=True,
                msg="query_parameters.namespace must be a dictionary.",
            )
            return {}

        supported_keys = {'name', 'match', 'limit', 'marker'}
        unsupported_keys = sorted(set(namespace_query.keys()) - supported_keys)
        if unsupported_keys:
            self.module.exit_json(
                failed=True,
                msg="Unsupported namespace query parameter(s): %s"
                    % ", ".join(unsupported_keys),
            )
            return {}

        if namespace_query.get('name') and namespace_query.get('match'):
            self.module.exit_json(
                failed=True,
                msg="query_parameters.namespace.name and query_parameters.namespace.match are mutually exclusive.",
            )
            return {}

        return namespace_query

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
