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
- Supports listing attached IAM policies for a user, group, or role.

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
    - C(iam_group) - returns list of all IAM groups in the specified namespace.
    type: list
    elements: str
    choices: ['namespace', 'iam_group', 'iam_attached_policies']
    required: true

  namespace:
    description:
    - The ObjectScale namespace to query for IAM resources.
    - Required when C(iam_group) or C(iam_attached_policies) is in I(gather_subset).
    type: str
    required: false

  user_name:
    description:
    - The IAM user name whose attached policies to list.
    - Used when C(iam_attached_policies) is in I(gather_subset).
    - Mutually exclusive with I(group_name) and I(role_name).
    type: str
    required: false

  group_name:
    description:
    - The IAM group name whose attached policies to list.
    - Used when C(iam_attached_policies) is in I(gather_subset).
    - Mutually exclusive with I(user_name) and I(role_name).
    type: str
    required: false

  role_name:
    description:
    - The IAM role name whose attached policies to list.
    - Used when C(iam_attached_policies) is in I(gather_subset).
    - Mutually exclusive with I(user_name) and I(group_name).
    type: str
    required: false

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

- name: List attached policies for an IAM user
  dellemc.objectscale.info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    gather_subset:
      - iam_attached_policies
    namespace: "ns1"
    user_name: "testuser"
  register: user_policies

- name: List attached policies for an IAM group
  dellemc.objectscale.info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    gather_subset:
      - iam_attached_policies
    namespace: "ns1"
    group_name: "developers"
  register: group_policies
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

IamGroups:
    description: List of IAM groups in the specified namespace.
    returned: When iam_group is in gather_subset
    type: list
    elements: dict
    contains:
        GroupName:
            description: The name of the IAM group.
            type: str
        GroupId:
            description: The unique identifier for the IAM group.
            type: str
        Arn:
            description: The Amazon Resource Name (ARN) of the group.
            type: str
        Path:
            description: The IAM path prefix for the group.
            type: str
        CreateDate:
            description: The date and time when the group was created.
            type: str
    sample:
        [
            {
                "GroupName": "developers",
                "GroupId": "AGPA1234567890EXAMPLE",
                "Arn": "urn:ecs:iam::ns1:group/developers",
                "Path": "/",
                "CreateDate": "2025-01-15T12:00:00Z"
            }
        ]

IamAttachedPolicies:
    description: List of managed policies attached to the specified IAM entity.
    returned: When iam_attached_policies is in gather_subset
    type: list
    elements: dict
    contains:
        PolicyName:
            description: The name of the attached policy.
            type: str
        PolicyArn:
            description: The ARN of the attached policy.
            type: str
    sample:
        [
            {
                "PolicyName": "ECSS3ReadOnlyAccess",
                "PolicyArn": "urn:ecs:iam:::policy/ECSS3ReadOnlyAccess"
            }
        ]
'''

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import api_client as objectscale_api_client
except (ImportError, Exception):
    objectscale_api_client = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import _stubs as objectscale_client_stubs
except (ImportError, Exception):
    objectscale_client_stubs = None

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_response import (
        NamespaceServiceGetNamespaceResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespaces_response import (
        NamespaceServiceGetNamespacesResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi as IamApiType

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

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi
except (ImportError, Exception):
    IamApi = None  # type: ignore[assignment,misc]


class ObjectScaleInfo(object):
    """Class for gathering information from ObjectScale"""

    @staticmethod
    def _ensure_secretstr_compatibility() -> None:
        """Patch generated stubs for runtime compatibility when pydantic is absent."""
        if objectscale_api_client is not None:
            secret_str_cls = getattr(objectscale_api_client, 'SecretStr', None)
            if secret_str_cls is str:
                class _CompatSecretStr(str):
                    def get_secret_value(self) -> str:
                        return str(self)

                objectscale_api_client.SecretStr = _CompatSecretStr

        if objectscale_client_stubs is not None:
            base_model_cls = getattr(objectscale_client_stubs, 'BaseModel', None)
            if base_model_cls is not None and not hasattr(base_model_cls, 'model_dump'):
                def _model_dump(self, *args, **kwargs):  # type: ignore[no-redef]
                    data = getattr(self, '__dict__', None)
                    if isinstance(data, dict):
                        return dict(data)
                    return {}

                base_model_cls.model_dump = _model_dump

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(dict(
            gather_subset=dict(
                type='list',
                elements='str',
                required=True,
                choices=['namespace', 'iam_group', 'iam_attached_policies']
            ),
            namespace=dict(type='str', required=False),
            user_name=dict(type='str', required=False),
            group_name=dict(type='str', required=False),
            role_name=dict(type='str', required=False),
            query_parameters=dict(type='dict', required=False),
        ))

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=False,
            mutually_exclusive=[['user_name', 'group_name', 'role_name']],
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )
            return

        if NamespaceApi is None:
            self.module.exit_json(
                failed=True,
                msg="ObjectScale namespace API client is unavailable. Rebuild/install objectscale_client.",
            )

        namespace_api_cls = NamespaceApi

        try:
            self._ensure_secretstr_compatibility()
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.namespace_api: NamespaceApi = NamespaceApi(self.api_client)
            if IamApi is not None:
                self.iam_api: IamApiType = IamApi(self.api_client)
            else:
                self.iam_api = None  # type: ignore[assignment]
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
            response = (
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

    def get_iam_groups(self, namespace: str) -> Optional[List[Dict[str, Any]]]:
        """Get all IAM groups in a namespace."""
        if self.iam_api is None:
            self.module.exit_json(failed=True, msg="IamApi is not available.")
            return None
        try:
            return self.iam_api.list_groups(namespace)
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Getting IAM group list failed with error: %s" % error_msg
            self.module.exit_json(failed=True, msg=msg)

    def get_iam_attached_policies(self, namespace: str) -> Optional[List[Dict[str, Any]]]:
        """Get attached IAM policies for a user, group, or role."""
        if self.iam_api is None:
            self.module.exit_json(failed=True, msg="IamApi is not available.")
            return None

        user_name = self.module.params.get('user_name')
        group_name = self.module.params.get('group_name')
        role_name = self.module.params.get('role_name')

        if not any([user_name, group_name, role_name]):
            self.module.exit_json(
                failed=True,
                msg="One of 'user_name', 'group_name', or 'role_name' is required "
                    "when gathering iam_attached_policies info."
            )
            return None

        try:
            if user_name:
                return self.iam_api.list_attached_user_policies(user_name, namespace)
            elif group_name:
                return self.iam_api.list_attached_group_policies(group_name, namespace)
            elif role_name:
                return self.iam_api.list_attached_role_policies(role_name, namespace)
        except Exception as e:
            error_msg = utils.determine_error(e)
            entity = user_name or group_name or role_name
            msg = "Getting attached policies failed with error: %s" % error_msg
            self.module.exit_json(failed=True, msg=msg)
        return None

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

        if 'iam_group' in gather_subset:
            namespace = self.module.params.get('namespace')
            if not namespace:
                self.module.exit_json(
                    failed=True,
                    msg="The 'namespace' parameter is required when gathering iam_group info."
                )
                return
            result['IamGroups'] = self.get_iam_groups(namespace)

        if 'iam_attached_policies' in gather_subset:
            namespace = self.module.params.get('namespace')
            if not namespace:
                self.module.exit_json(
                    failed=True,
                    msg="The 'namespace' parameter is required when gathering iam_attached_policies info."
                )
                return
            result['IamAttachedPolicies'] = self.get_iam_attached_policies(namespace)

        self.module.exit_json(**result)


def main() -> None:
    """Create ObjectScaleInfo object and gather information."""
    obj = ObjectScaleInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
