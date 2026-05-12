#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing ObjectScale storage pools."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: storage_pool

version_added: '1.0.0'

short_description: Manage storage pools on Dell ObjectScale

description:
  - Creates, modifies, and deletes storage pools on Dell ObjectScale.
  - Supports idempotent operations — reruns without changes are safe.
  - Supports check mode (dry-run) and diff mode (before/after comparison).

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: Supports check mode. No changes will be made when check mode is enabled.
  diff_mode:
    support: full
    description: Supports diff mode. Shows before and after state of the storage pool.

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
  timeout:
    description:
    - Timeout in seconds for HTTP requests to the ObjectScale management endpoint.
    type: int
    default: 30
  storage_pool_name:
    description:
    - Name of the storage pool.
    - Used as the primary identifier for idempotency checks.
    type: str
    required: true
  description:
    description:
    - Description of the storage pool.
    type: str
  is_cold_storage_enabled:
    description:
    - Enable or disable cold storage for this storage pool.
    type: bool
    default: false
  warning_alert_at:
    description:
    - Percentage of used capacity at which a warning alert is triggered.
    type: int
  error_alert_at:
    description:
    - Percentage of used capacity at which an error alert is triggered.
    type: int
  state:
    description:
    - C(present) ensures the storage pool exists with specified configuration.
    - C(absent) ensures the storage pool does not exist.
    type: str
    required: true
    choices: [present, absent]

notes:
  - Storage pools are identified by name for idempotency.
  - Supports check mode — use C(ansible-playbook --check) to preview changes.
  - Supports diff mode — use C(ansible-playbook --diff) to show before/after.
  - C(isProtected) is always set to false; protected varrays are not supported by ObjectScale.
'''

EXAMPLES = r'''
- name: Create a storage pool
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_production"
    description: "Production storage pool"
    is_cold_storage_enabled: false
    warning_alert_at: 70
    error_alert_at: 85
    state: present

- name: Modify a storage pool description
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_production"
    description: "Updated production pool"
    state: present

- name: Delete a storage pool
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_staging"
    state: absent

- name: Create pool (check mode — preview only)
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_new"
    description: "New pool"
    state: present
  check_mode: true
'''

RETURN = r'''
changed:
    description: Whether the storage pool was created, modified, or deleted.
    returned: always
    type: bool
    sample: true

storage_pool_details:
    description: Details of the storage pool after the operation. Empty dict if deleted.
    returned: when state=present and not check_mode
    type: dict
    sample:
        id: "urn:storageos:VirtualArray:12345678-1234-1234-1234-123456789abc"
        name: "sp_production"
        description: "Production storage pool"
        isProtected: false
        isColdStorageEnabled: false
        warningAlertAt: 70
        errorAlertAt: 85
        isRackProtected: false
        inactive: false

diff:
    description: Before/after comparison when diff mode is enabled.
    returned: when diff mode enabled and changes made
    type: dict
    sample:
        before:
            description: "Old description"
            warningAlertAt: 70
        after:
            description: "New description"
            warningAlertAt: 80
'''

from typing import Any, Dict, Optional  # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT  # noqa: E402

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import api_client as objectscale_api_client
except Exception:
    objectscale_api_client = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import _stubs as objectscale_client_stubs
except Exception:
    objectscale_client_stubs = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.object_varray_api import ObjectVarrayApi
except Exception:
    ObjectVarrayApi = None  # type: ignore[assignment,misc]


class StoragePool(object):
    """Class for managing ObjectScale storage pools."""

    @staticmethod
    def _ensure_client_stub_compatibility():
        # type: () -> None
        if objectscale_api_client is not None:
            secret_str_cls = getattr(objectscale_api_client, 'SecretStr', None)
            if secret_str_cls is str:
                class _CompatSecretStr(str):
                    def get_secret_value(self):
                        # type: () -> str
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

    def __init__(self):
        # type: () -> None
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_storage_pool_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil",
            )
            return

        if ObjectVarrayApi is None:
            self.module.exit_json(
                failed=True,
                msg="ObjectScale storage pool API client is unavailable. Rebuild/install objectscale_client.",
            )
            return

        try:
            self._ensure_client_stub_compatibility()
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.storage_pool_api = ObjectVarrayApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

    @staticmethod
    def _sanitize_sensitive_fields(value):
        # type: (Any) -> Any
        sensitive_keys = {
            'password', 'passwd', 'secret', 'token', 'auth_token', 'access_key', 'secret_key',
        }

        if isinstance(value, dict):
            sanitized = {}  # type: Dict[str, Any]
            for key, val in value.items():
                if str(key).lower() in sensitive_keys:
                    sanitized[key] = '***'
                else:
                    sanitized[key] = StoragePool._sanitize_sensitive_fields(val)
            return sanitized

        if isinstance(value, list):
            return [StoragePool._sanitize_sensitive_fields(item) for item in value]

        return value

    @staticmethod
    def _to_dict(value):
        # type: (Any) -> Dict[str, Any]
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, 'to_dict'):
            return value.to_dict()
        return {}

    def get_storage_pool_details(self, name):
        # type: (str) -> Optional[Dict[str, Any]]
        """Retrieve a storage pool by name. Returns None if not found."""
        try:
            response = self.storage_pool_api.object_varray_service_get_virtual_arrays()
            pools = response.varray or []
            for pool in pools:
                pool_dict = self._to_dict(pool)
                pool_dict = self._sanitize_sensitive_fields(pool_dict)
                if pool_dict.get('name') == name:
                    return pool_dict
            return None
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Getting storage pool details failed with error: %s" % error_msg,
            )
            return None

    def is_modify_required(self, params, current):
        # type: (Dict[str, Any], Dict[str, Any]) -> bool
        """Compare desired state to current state. Return True if update needed."""
        checks = [
            ('description', params.get('description')),
            ('isColdStorageEnabled', params.get('is_cold_storage_enabled')),
            ('warningAlertAt', params.get('warning_alert_at')),
            ('errorAlertAt', params.get('error_alert_at')),
        ]
        for api_key, desired in checks:
            if desired is not None and current.get(api_key) != desired:
                return True
        return False

    def _build_create_payload(self):
        # type: () -> Dict[str, Any]
        """Build the payload for creating a storage pool."""
        payload = {
            'name': self.module.params.get('storage_pool_name'),
            'description': self.module.params.get('description'),
            'is_protected': False,
            'is_cold_storage_enabled': self.module.params.get('is_cold_storage_enabled', False),
        }  # type: Dict[str, Any]

        warning_alert = self.module.params.get('warning_alert_at')
        if warning_alert is not None:
            payload['warning_alert_at'] = warning_alert

        error_alert = self.module.params.get('error_alert_at')
        if error_alert is not None:
            payload['error_alert_at'] = error_alert

        return payload

    def _build_modify_payload(self, current):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """Build the payload for modifying a storage pool."""
        payload = {}  # type: Dict[str, Any]

        description = self.module.params.get('description')
        if description is not None and description != current.get('description'):
            payload['description'] = description

        cold_storage = self.module.params.get('is_cold_storage_enabled')
        if cold_storage is not None and cold_storage != current.get('isColdStorageEnabled'):
            payload['is_cold_storage_enabled'] = cold_storage

        warning_alert = self.module.params.get('warning_alert_at')
        if warning_alert is not None and warning_alert != current.get('warningAlertAt'):
            payload['warning_alert_at'] = warning_alert

        error_alert = self.module.params.get('error_alert_at')
        if error_alert is not None and error_alert != current.get('errorAlertAt'):
            payload['error_alert_at'] = error_alert

        return payload

    def create_storage_pool(self):
        # type: () -> None
        """Create a new storage pool via the ObjectScale API."""
        payload = self._build_create_payload()
        try:
            # Convert snake_case to camelCase for API
            api_payload = {
                'name': payload.get('name'),
                'isProtected': payload.get('is_protected'),
                'isColdStorageEnabled': payload.get('is_cold_storage_enabled'),
                'description': payload.get('description'),
            }
            if 'warning_alert_at' in payload:
                api_payload['warningAlertAt'] = payload['warning_alert_at']
            if 'error_alert_at' in payload:
                api_payload['errorAlertAt'] = payload['error_alert_at']

            self.storage_pool_api.object_varray_service_create_virtual_array(
                object_varray_service_create_virtual_array_request=api_payload,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Creating storage pool '%s' failed with error: %s"
                    % (self.module.params.get('storage_pool_name'), error_msg),
            )

    def modify_storage_pool(self, pool_id):
        # type: (str) -> None
        """Modify an existing storage pool."""
        current = self.get_storage_pool_details(self.module.params.get('storage_pool_name'))
        if current is None:
            self.module.exit_json(
                failed=True,
                msg="Storage pool '%s' was not found for modification."
                    % self.module.params.get('storage_pool_name'),
            )
            return

        payload = self._build_modify_payload(current)
        if not payload:
            return

        # Include the pool name in the update payload (required by some API builds)
        payload['name'] = current.get('name')

        try:
            # Convert snake_case to camelCase for API
            api_payload = {}
            if 'name' in payload:
                api_payload['name'] = payload['name']
            if 'description' in payload:
                api_payload['description'] = payload['description']
            if 'is_cold_storage_enabled' in payload:
                api_payload['isColdStorageEnabled'] = payload['is_cold_storage_enabled']
            if 'warning_alert_at' in payload:
                api_payload['warningAlertAt'] = payload['warning_alert_at']
            if 'error_alert_at' in payload:
                api_payload['errorAlertAt'] = payload['error_alert_at']

            self.storage_pool_api.object_varray_service_update_virtual_array(
                id=pool_id,
                object_varray_service_update_virtual_array_request=api_payload,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Modifying storage pool '%s' failed with error: %s"
                    % (pool_id, error_msg),
            )

    def delete_storage_pool(self, pool_id):
        # type: (str) -> None
        """Delete a storage pool."""
        try:
            self.storage_pool_api.object_varray_service_delete_virtual_array(
                id=pool_id,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Deleting storage pool '%s' failed with error: %s"
                    % (pool_id, error_msg),
            )

    def _validate_params(self):
        # type: () -> bool
        """Validate module parameters. Returns False and calls fail_json on error."""
        warning_alert = self.module.params.get('warning_alert_at')
        error_alert = self.module.params.get('error_alert_at')

        if (warning_alert is not None and error_alert is not None
                and warning_alert >= error_alert):
            self.module.fail_json(
                msg="warning_alert_at (%d) must be less than error_alert_at (%d)."
                    % (warning_alert, error_alert)
            )
            return False
        return True

    def perform_module_operation(self):
        # type: () -> None
        """Main entry point for module execution."""
        if not self._validate_params():
            return

        try:
            self._execute_module_operation()
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Storage pool operation failed with error: %s" % error_msg,
            )

    def _execute_module_operation(self):
        # type: () -> None
        """Internal module execution logic."""
        result = dict(
            changed=False,
            storage_pool_details={},
        )  # type: Dict[str, Any]

        state = self.module.params['state']
        pool_name = self.module.params['storage_pool_name']

        current = self.get_storage_pool_details(pool_name)
        before_state = dict(current) if current else {}

        # --- state: absent ---
        if state == 'absent':
            if current:
                if not self.module.check_mode:
                    self.delete_storage_pool(current['id'])
                result['changed'] = True
            if self.module._diff:
                result['diff'] = {'before': before_state, 'after': {}}
            self.module.exit_json(**result)
            return

        # --- state: present ---
        if not current:
            # Pool does not exist -> create
            if self.module.check_mode:
                result['changed'] = True
                result['storage_pool_details'] = self._build_create_payload()
                if self.module._diff:
                    result['diff'] = {'before': {}, 'after': result['storage_pool_details']}
                self.module.exit_json(**result)
                return

            self.create_storage_pool()
            result['changed'] = True
            current = self.get_storage_pool_details(pool_name)
            if current:
                result['storage_pool_details'] = current
            if self.module._diff:
                result['diff'] = {'before': {}, 'after': current or {}}
            self.module.exit_json(**result)
            return

        # Pool exists -> check if modification is needed
        modify_needed = self.is_modify_required(self.module.params, current)

        if modify_needed:
            if not self.module.check_mode:
                self.modify_storage_pool(current['id'])
                current = self.get_storage_pool_details(pool_name)

            result['changed'] = True

        result['storage_pool_details'] = current or {}

        if self.module._diff:
            after_state = dict(current) if current else {}
            result['diff'] = {'before': before_state, 'after': after_state}

        self.module.exit_json(**result)

    @staticmethod
    def get_storage_pool_parameters():
        # type: () -> Dict[str, Dict[str, Any]]
        """Return the storage pool specific parameters for the module argument_spec."""
        return dict(
            storage_pool_name=dict(type='str', required=True),
            description=dict(type='str', required=False),
            is_cold_storage_enabled=dict(type='bool', required=False, default=False),
            warning_alert_at=dict(type='int', required=False),
            error_alert_at=dict(type='int', required=False),
            state=dict(type='str', choices=['present', 'absent'], required=True),
        )


def main():
    # type: () -> None
    obj = StoragePool()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
