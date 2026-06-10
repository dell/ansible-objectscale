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

short_description: Manage storage pool configuration on Dell ObjectScale

description:
- Manages storage pool configuration on Dell ObjectScale.
- Supports modifying storage pool properties such as description, cold storage,
  and alert thresholds.
- Storage pools are identified by name and looked up automatically.

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
    no_log: true

  validate_certs:
    description:
    - Boolean value to enable or disable SSL certificate verification.
    type: bool
    default: true

  timeout:
    description:
    - Timeout in seconds for API requests.
    type: int
    default: 30

  storage_pool_name:
    description:
    - Name of the storage pool to manage.
    type: str
    required: true

  description:
    description:
    - Description of the storage pool.
    type: str

  is_cold_storage_enabled:
    description:
    - Whether cold storage encoding is enabled on the storage pool.
    type: bool

  is_protected:
    description:
    - Whether the storage pool is protected.
    type: bool

  warning_alert_at:
    description:
    - Threshold percent of remaining capacity at which a warning alert is raised.
    - Valid values are from -1 to 100. Value of -1 means do not alert.
    - Must be greater than C(error_alert_at).
    type: int

  error_alert_at:
    description:
    - Threshold percent of remaining capacity at which an error alert is raised.
    - Valid values are from -1 to 100. Value of -1 means do not alert.
    - Must be greater than C(critical_alert_at).
    type: int

  critical_alert_at:
    description:
    - Threshold percent of remaining capacity at which a critical alert is raised.
    - Valid values are from -1 to 100. Value of -1 means do not alert.
    type: int

  state:
    description:
    - Desired state of the storage pool.
    - C(present) ensures the storage pool is updated with the specified properties.
    type: str
    choices: ['present']
    default: present

notes:
- Only update operations are supported. Storage pools cannot be created or deleted
  through this module.
- Supports check mode.
'''

EXAMPLES = r'''
- name: Update storage pool description
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_default"
    description: "Updated by Ansible automation"
    state: present

- name: Update alert thresholds
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_default"
    warning_alert_at: 80
    error_alert_at: 60
    critical_alert_at: 20
    state: present

- name: Enable cold storage on a pool
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_cold"
    is_cold_storage_enabled: true
    state: present

- name: Check mode - preview update
  dellemc.objectscale.storage_pool:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_name: "sp_default"
    description: "Preview change"
    state: present
  check_mode: true
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool

storage_pool_details:
    description: Storage pool details after the operation.
    returned: When a storage pool exists
    type: dict
    contains:
        id:
            description: Unique storage pool identifier.
            type: str
        name:
            description: Name of the storage pool.
            type: str
        description:
            description: Description of the storage pool.
            type: str
        isColdStorageEnabled:
            description: Whether cold storage encoding is enabled.
            type: bool
        warningAlertAt:
            description: Warning alert threshold percent.
            type: int
        errorAlertAt:
            description: Error alert threshold percent.
            type: int
        criticalAlertAt:
            description: Critical alert threshold percent.
            type: int
    sample:
        {
            "id": "urn:storageos:VirtualArray:12345678-1234-1234-1234-123456789abc",
            "name": "sp_default",
            "description": "Updated by Ansible automation",
            "isColdStorageEnabled": false,
            "warningAlertAt": 70,
            "errorAlertAt": 85,
            "criticalAlertAt": 95
        }
'''

from typing import Any, Dict, Optional, TYPE_CHECKING  # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT  # noqa: E402

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.\
        objectscale_client import api_client as objectscale_api_client
except Exception:
    objectscale_api_client = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.\
        objectscale_client import _stubs as objectscale_client_stubs
except Exception:
    objectscale_client_stubs = None

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.\
        objectscale_client.api.object_varray_api import ObjectVarrayApi
    from ansible_collections.dellemc.objectscale.plugins.module_utils.\
        objectscale_client.models.\
        object_varray_service_update_virtual_array_request import (
            ObjectVarrayServiceUpdateVirtualArrayRequest,
        )

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.\
        objectscale_client.api.object_varray_api import ObjectVarrayApi  # noqa: F811
    from ansible_collections.dellemc.objectscale.plugins.module_utils.\
        objectscale_client.models.\
        object_varray_service_update_virtual_array_request import (  # noqa: F811
            ObjectVarrayServiceUpdateVirtualArrayRequest,
        )
except Exception:
    ObjectVarrayApi = None  # type: ignore[assignment,misc]
    ObjectVarrayServiceUpdateVirtualArrayRequest = None  # type: ignore[assignment,misc]


class StoragePool(object):
    """Class for managing ObjectScale storage pools."""

    # Fields checked for idempotency (module param -> API alias)
    MODIFY_FIELDS = {
        'description': 'description',
        'is_cold_storage_enabled': 'isColdStorageEnabled',
        'is_protected': 'isProtected',
        'warning_alert_at': 'warningAlertAt',
        'error_alert_at': 'errorAlertAt',
        'critical_alert_at': 'criticalAlertAt',
    }

    @staticmethod
    def _ensure_client_stub_compatibility() -> None:
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

    @staticmethod
    def _build_api_payload(model_cls: Any, payload: Dict[str, Any]) -> Any:
        """Build API payload compatible with real pydantic models and stub mode."""
        if model_cls is None:
            return {k: v for k, v in payload.items() if v is not None}

        base_cls = model_cls.__mro__[1] if len(model_cls.__mro__) > 1 else None
        if base_cls is not None and base_cls.__module__.endswith('objectscale_client._stubs'):
            return {k: v for k, v in payload.items() if v is not None}

        try:
            return model_cls.model_validate(payload)
        except Exception:
            return model_cls(**payload)

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(
            dict(
                storage_pool_name=dict(type='str', required=True),
                description=dict(type='str', required=False),
                is_cold_storage_enabled=dict(type='bool', required=False),
                is_protected=dict(type='bool', required=False),
                warning_alert_at=dict(type='int', required=False),
                error_alert_at=dict(type='int', required=False),
                critical_alert_at=dict(type='int', required=False),
                state=dict(type='str', default='present', choices=['present']),
            )
        )

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
                msg="ObjectScale storage pool API client is unavailable. "
                    "Rebuild/install objectscale_client.",
            )
            return

        try:
            self._ensure_client_stub_compatibility()
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.storage_pool_api = ObjectVarrayApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

    @staticmethod
    def _sanitize_sensitive_fields(value: Any) -> Any:
        """Remove sensitive fields from API response data."""
        sensitive_keys = {
            'password', 'passwd', 'secret', 'token', 'auth_token', 'access_key', 'secret_key',
        }

        if isinstance(value, dict):
            sanitized: Dict[str, Any] = {}
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
    def _to_dict(value: Any) -> Dict[str, Any]:
        """Convert API response object to dictionary."""
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, 'to_dict'):
            return value.to_dict()
        return {}

    def get_storage_pool_details(self, storage_pool_name: str) -> Optional[Dict[str, Any]]:
        """Get storage pool details by looking up the pool by name."""
        try:
            response = self.storage_pool_api.object_varray_service_get_virtual_arrays()
            pools = response.varray or []
            for pool in pools:
                pool_dict = self._to_dict(pool)
                if pool_dict.get('name') == storage_pool_name:
                    return self._sanitize_sensitive_fields(pool_dict)
            return None
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Getting storage pool '%s' failed with error: %s" % (storage_pool_name, error_msg),
            )
            return None

    def _get_storage_pool_by_id(self, storage_pool_id: str) -> Dict[str, Any]:
        """Get storage pool details by ID."""
        try:
            response = self.storage_pool_api.object_varray_service_get_virtual_array(id=storage_pool_id)
            pool = self._to_dict(response)
            return self._sanitize_sensitive_fields(pool)
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) == '404':
                self.module.exit_json(
                    failed=True,
                    msg="Storage pool with id '%s' was not found (HTTP 404)." % storage_pool_id,
                )
                return {}
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Getting storage pool %s failed with error: %s" % (storage_pool_id, error_msg),
            )
            return {}

    def is_modify_required(self, current: Dict[str, Any]) -> bool:
        """Compare desired state to current state. Return True if update needed."""
        for param_key, api_key in self.MODIFY_FIELDS.items():
            desired = self.module.params.get(param_key)
            if desired is not None and current.get(api_key) != desired:
                return True
        return False

    def _validate_alert_thresholds(self) -> None:
        """Validate alert threshold parameters."""
        warning = self.module.params.get('warning_alert_at')
        error = self.module.params.get('error_alert_at')
        critical = self.module.params.get('critical_alert_at')

        for name, value in [('warning_alert_at', warning), ('error_alert_at', error),
                            ('critical_alert_at', critical)]:
            if value is not None and (value < -1 or value > 100):
                self.module.exit_json(
                    failed=True,
                    msg="%s must be between -1 and 100, got %d." % (name, value),
                )

        if warning is not None and error is not None and warning <= error:
            self.module.exit_json(
                failed=True,
                msg="warning_alert_at (%d) must be greater than error_alert_at (%d)."
                    % (warning, error),
            )

        if error is not None and critical is not None and error <= critical:
            self.module.exit_json(
                failed=True,
                msg="error_alert_at (%d) must be greater than critical_alert_at (%d)."
                    % (error, critical),
            )

    def modify_storage_pool(self, pool_id: str, current: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a storage pool with the desired parameters."""
        if ObjectVarrayServiceUpdateVirtualArrayRequest is None:
            self.module.exit_json(
                failed=True,
                msg="Storage pool update request model is unavailable. "
                    "Rebuild/install objectscale_client.",
            )
            return None

        # Build update payload from current values + desired changes
        payload: Dict[str, Any] = {
            'name': current.get('name', self.module.params['storage_pool_name']),
            'isProtected': current.get('isProtected', False),
        }

        # Apply desired changes, falling back to current values
        for param_key, api_key in self.MODIFY_FIELDS.items():
            desired = self.module.params.get(param_key)
            if desired is not None:
                payload[api_key] = desired
            elif current.get(api_key) is not None:
                payload[api_key] = current[api_key]

        try:
            request = self._build_api_payload(ObjectVarrayServiceUpdateVirtualArrayRequest, payload)
            response = self.storage_pool_api.object_varray_service_update_virtual_array(
                id=pool_id,
                object_varray_service_update_virtual_array_request=request,
            )
            return self._sanitize_sensitive_fields(self._to_dict(response))
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) == '404':
                self.module.exit_json(
                    failed=True,
                    msg="Storage pool '%s' was not found (HTTP 404)." % pool_id,
                )
                return None
            if str(status) == '403':
                self.module.exit_json(
                    failed=True,
                    msg="Insufficient permissions — requires SYSTEM_ADMIN role.",
                )
                return None
            if str(status) == '401':
                self.module.exit_json(
                    failed=True,
                    msg="Failed to connect to ObjectScale: HTTP 401",
                )
                return None
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Updating storage pool '%s' failed with error: %s" % (pool_id, error_msg),
            )
            return None

    def perform_module_operation(self) -> None:
        """Main entry point for module execution."""
        storage_pool_name = self.module.params['storage_pool_name']
        state = self.module.params.get('state', 'present')

        # Validate alert thresholds
        self._validate_alert_thresholds()

        # Get current storage pool details
        current = self.get_storage_pool_details(storage_pool_name)

        if state == 'present':
            if current is None:
                self.module.exit_json(
                    failed=True,
                    msg="Storage pool '%s' was not found. "
                        "This module only supports updating existing storage pools."
                        % storage_pool_name,
                )
                return

            pool_id = current.get('id')
            if not pool_id:
                self.module.exit_json(
                    failed=True,
                    msg="Storage pool '%s' has no valid identifier." % storage_pool_name,
                )
                return

            if self.is_modify_required(current):
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        storage_pool_details=current,
                        msg="Storage pool '%s' would be updated (check mode)." % storage_pool_name,
                    )
                    return

                updated = self.modify_storage_pool(pool_id, current)
                if updated is None:
                    # modify_storage_pool already called exit_json on error
                    return
                self.module.exit_json(
                    changed=True,
                    storage_pool_details=updated,
                )
            else:
                self.module.exit_json(
                    changed=False,
                    storage_pool_details=current,
                )


def main() -> None:
    obj = StoragePool()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
