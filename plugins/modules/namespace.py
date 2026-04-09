#!/usr/bin/python
# Copyright: (c) 2025, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing namespaces on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: namespace

version_added: '1.0.0'

short_description: Manages namespace configuration on Dell ObjectScale

description:
- Manages the namespace configuration on the Dell ObjectScale storage system.
  This includes creating, modifying, deleting and retrieving details of a namespace.

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

  namespace_name:
    description:
    - The name of the namespace.
    type: str
    required: true

  default_data_services_vpool:
    description:
    - The default data services replication group (vpool) for the namespace.
    - Required when creating a namespace.
    type: str

  namespace_admins:
    description:
    - List of user IDs to set as namespace administrators.
    type: list
    elements: str

  is_compliance_enabled:
    description:
    - Whether compliance (WORM) is enabled for the namespace.
    type: bool

  is_encryption_enabled:
    description:
    - Whether server-side encryption is enabled for the namespace.
    type: bool

  is_stale_allowed:
    description:
    - Whether reading from stale/secondary zone data is allowed.
    type: bool

  allowed_protocols:
    description:
    - List of protocols allowed for this namespace (e.g. C(s3), C(atmos), C(swift)).
    type: list
    elements: str

  default_replication_factor:
    description:
    - Default replication factor for objects in this namespace.
    type: int

  quota_enabled:
    description:
    - Whether namespace quota is enabled.
    type: bool

  blocked_quota_size:
    description:
    - Quota size (in bytes) at which new object creation is blocked.
    type: int

  notification_quota_size:
    description:
    - Quota size (in bytes) at which a notification is sent.
    type: int

  soft_quota_size:
    description:
    - Soft quota size (in bytes).
    type: int

  hard_quota_size:
    description:
    - Hard quota size (in bytes).
    type: int

  state:
    description:
    - The state of the namespace after the task is performed.
    - C(present) - indicates that the namespace should exist on the system.
    - C(absent) - indicates that the namespace should not exist on the system.
    choices: ['present', 'absent']
    type: str
    required: true

notes:
- The I(check_mode) is not supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Create a namespace
  dellemc.objectscale.namespace:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "testnamespace"
    default_data_services_vpool: "urn:storageos:ReplicationGroupInfo:xxxx:global"
    namespace_admins:
      - "admin@example.com"
    is_compliance_enabled: false
    is_encryption_enabled: false
    state: "present"

- name: Enable quota on a namespace
  dellemc.objectscale.namespace:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "testnamespace"
    quota_enabled: true
    hard_quota_size: 107374182400
    notification_quota_size: 85899345920
    state: "present"

- name: Get namespace details
  dellemc.objectscale.namespace:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "testnamespace"
    state: "present"

- name: Delete a namespace
  dellemc.objectscale.namespace:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "testnamespace"
    state: "absent"
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: false

namespace_details:
    description: Namespace details.
    returned: When a namespace exists
    type: dict
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
        namespace_admins:
            description: List of namespace administrator user IDs.
            type: list
        is_compliance_enabled:
            description: Whether compliance (WORM) mode is enabled.
            type: bool
        is_encryption_enabled:
            description: Whether server-side encryption is enabled.
            type: bool
        is_stale_allowed:
            description: Whether stale data reads are allowed.
            type: bool
        allowed_protocols:
            description: Protocols allowed for this namespace.
            type: list
        default_replication_factor:
            description: Default replication factor.
            type: int
    sample:
        {
            "id": "testnamespace",
            "name": "testnamespace",
            "default_data_services_vpool": "urn:storageos:ReplicationGroupInfo:xxxx:global",
            "namespace_admins": ["admin@example.com"],
            "is_compliance_enabled": false,
            "is_encryption_enabled": false,
            "is_stale_allowed": false,
            "allowed_protocols": ["s3"],
            "default_replication_factor": 1
        }
'''

from typing import Any, Dict, TYPE_CHECKING
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_create_namespace_request import (
        NamespaceServiceCreateNamespaceRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_response import (
        NamespaceServiceGetNamespaceResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_quota_response import (
        NamespaceServiceGetNamespaceQuotaResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_request import (
        NamespaceServiceUpdateNamespaceRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_quota_request import (
        NamespaceServiceUpdateNamespaceQuotaRequest,
    )

# Import objectscale client - fail fast if not available
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_create_namespace_request import (
    NamespaceServiceCreateNamespaceRequest,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_response import (
    NamespaceServiceGetNamespaceResponse,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_quota_response import (
    NamespaceServiceGetNamespaceQuotaResponse,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_request import (
    NamespaceServiceUpdateNamespaceRequest,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_quota_request import (
    NamespaceServiceUpdateNamespaceQuotaRequest,
)


class Namespace(object):
    """Class with operations on ObjectScale namespace"""

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_namespace_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=False
        )

        # Validate dependencies and setup connection
        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.namespace_api = NamespaceApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

        self.module.log('Connected to ObjectScale at %s' % self.module.params['objectscale_host'])

    def get_namespace_details(self, namespace_name: str) -> Dict[str, Any]:
        """Get the details of a namespace. Returns empty dict if namespace not found."""
        try:
            response: NamespaceServiceGetNamespaceResponse = (
                self.namespace_api.namespace_service_get_namespace(id=namespace_name)
            )
            return response.to_dict()
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return {}  # Return empty dict for not found
            error_msg = utils.determine_error(e)
            msg = "Getting namespace %s details failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def create_namespace(self, namespace_name: str, params: Dict[str, Any]) -> bool:
        """Create a namespace."""
        if not params.get('default_data_services_vpool'):
            self.module.exit_json(
                failed=True,
                msg="default_data_services_vpool is required when creating a namespace."
            )

        try:
            request = NamespaceServiceCreateNamespaceRequest(
                namespace=namespace_name,
                default_data_services_vpool=params['default_data_services_vpool'],
                namespace_admins=(
                    ','.join(params['namespace_admins'])
                    if params.get('namespace_admins') else None
                ),
                compliance_enabled=params.get('is_compliance_enabled'),
                is_encryption_enabled=params.get('is_encryption_enabled'),
                is_stale_allowed=params.get('is_stale_allowed'),
            )
            self.namespace_api.namespace_service_create_namespace(request)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating namespace %s failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def modify_namespace(self, namespace_name: str, params_to_modify: Dict[str, Any]) -> bool:
        """Modify a namespace."""
        try:
            request = NamespaceServiceUpdateNamespaceRequest(
                user_mapping=params_to_modify.pop('user_mapping', []),
                **params_to_modify,
            )
            self.namespace_api.namespace_service_update_namespace(
                namespace=namespace_name,
                namespace_service_update_namespace_request=request,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Modifying namespace %s failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def delete_namespace(self, namespace_name: str) -> bool:
        """Delete (deactivate) a namespace."""
        try:
            self.namespace_api.namespace_service_deactivate_namespace(
                namespace=namespace_name,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Deleting namespace %s failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def get_quota_details(self, namespace_name: str) -> Dict[str, Any]:
        """Get quota details for a namespace. Returns empty dict if quota not available."""
        try:
            response: NamespaceServiceGetNamespaceQuotaResponse = (
                self.namespace_api.namespace_service_get_namespace_quota(
                    namespace=namespace_name,
                )
            )
            return response.to_dict()
        except Exception as e:
            self.module.warn("Could not get quota for namespace %s: %s" % (namespace_name, str(e)))
            return {}

    def modify_quota(self, namespace_name: str, params: Dict[str, Any]) -> bool:
        """Update quota settings for a namespace."""
        quota_fields: Dict[str, Any] = {}
        field_map = {
            'blocked_quota_size': 'block_size',
            'notification_quota_size': 'notification_size',
            'hard_quota_size': 'block_size_in_count',
            'soft_quota_size': 'notification_size_in_count',
        }
        for param_key, model_key in field_map.items():
            if params.get(param_key) is not None:
                quota_fields[model_key] = params[param_key]

        if not quota_fields:
            return False

        try:
            request = NamespaceServiceUpdateNamespaceQuotaRequest(**quota_fields)
            self.namespace_api.namespace_service_update_namespace_quota(
                namespace=namespace_name,
                namespace_service_update_namespace_quota_request=request,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Updating quota for namespace %s failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def is_namespace_modified(self, namespace_details: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if the namespace needs to be modified."""
        modify_params = {}

        field_map = {
            'is_compliance_enabled': 'is_compliance_enabled',
            'is_encryption_enabled': 'is_encryption_enabled',
            'is_stale_allowed': 'is_stale_allowed',
            'default_replication_factor': 'default_replication_factor',
        }
        for param_key, detail_key in field_map.items():
            if params.get(param_key) is not None:
                if params[param_key] != namespace_details.get(detail_key):
                    modify_params[param_key] = params[param_key]

        if params.get('namespace_admins') is not None:
            # API returns namespace_admins as a comma-separated string
            admins_obj = namespace_details.get('namespace_admins', '')
            if isinstance(admins_obj, str):
                current_admins = [a.strip() for a in admins_obj.split(',') if a.strip()]
            elif isinstance(admins_obj, list):
                current_admins = admins_obj
            else:
                current_admins = []
            if set(params['namespace_admins']) != set(current_admins):
                # Update model expects a comma-separated string
                modify_params['namespace_admins'] = ','.join(params['namespace_admins'])

        if params.get('allowed_protocols') is not None:
            current_protocols = []
            proto_obj = namespace_details.get('allowed_protocols', {})
            if isinstance(proto_obj, dict):
                current_protocols = proto_obj.get('protocol', [])
            elif isinstance(proto_obj, list):
                current_protocols = proto_obj
            if set(params['allowed_protocols']) != set(current_protocols or []):
                modify_params['allowed_protocols'] = {
                    'protocol': params['allowed_protocols']
                }

        return modify_params

    def is_quota_modified(self, quota_details: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """Determine if quota settings need to be modified."""
        # Empty dict means quota not available or not set
        if not quota_details:
            return False
        for field in ['quota_enabled', 'blocked_quota_size',
                      'notification_quota_size', 'soft_quota_size', 'hard_quota_size']:
            if params.get(field) is not None and params[field] != quota_details.get(field):
                return True
        return False

    def perform_module_operation(self) -> None:
        """Perform different actions based on parameters chosen in playbook."""
        result: Dict[str, Any] = dict(
            changed=False,
            namespace_details=None
        )

        namespace_name = self.module.params['namespace_name']
        state = self.module.params['state']
        params = self.module.params

        namespace_details = self.get_namespace_details(namespace_name)
        namespace_exists = bool(namespace_details)  # Empty dict means not found

        if state == 'absent':
            if namespace_exists:
                self.delete_namespace(namespace_name)
                result['changed'] = True
        elif state == 'present':
            if not namespace_exists:
                self.create_namespace(namespace_name, params)
                result['changed'] = True
                namespace_details = self.get_namespace_details(namespace_name)
            else:
                modify_params = self.is_namespace_modified(namespace_details, params)
                if modify_params:
                    self.modify_namespace(namespace_name, modify_params)
                    result['changed'] = True

            # Handle quota separately
            quota_details = self.get_quota_details(namespace_name)
            if self.is_quota_modified(quota_details, params):
                self.modify_quota(namespace_name, params)
                result['changed'] = True
            elif any(params.get(f) is not None for f in
                     ['quota_enabled', 'blocked_quota_size', 'notification_quota_size',
                      'soft_quota_size', 'hard_quota_size']) and not namespace_exists:
                self.modify_quota(namespace_name, params)
                result['changed'] = True

            if result['changed']:
                namespace_details = self.get_namespace_details(namespace_name)

        result['namespace_details'] = namespace_details
        self.module.exit_json(**result)

    @staticmethod
    def get_namespace_parameters() -> Dict[str, Dict[str, Any]]:
        return dict(
            namespace_name=dict(type='str', required=True),
            default_data_services_vpool=dict(type='str'),
            namespace_admins=dict(type='list', elements='str'),
            is_compliance_enabled=dict(type='bool'),
            is_encryption_enabled=dict(type='bool'),
            is_stale_allowed=dict(type='bool'),
            allowed_protocols=dict(type='list', elements='str'),
            default_replication_factor=dict(type='int'),
            quota_enabled=dict(type='bool'),
            blocked_quota_size=dict(type='int'),
            notification_quota_size=dict(type='int'),
            soft_quota_size=dict(type='int'),
            hard_quota_size=dict(type='int'),
            state=dict(required=True, type='str', choices=['present', 'absent']),
        )


def main() -> None:
    """Create ObjectScale Namespace object and perform actions on it."""
    obj = Namespace()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
