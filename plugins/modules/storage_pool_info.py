#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible info module for querying ObjectScale storage pools."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: storage_pool_info

version_added: '1.0.0'

short_description: Gather storage pool information from Dell ObjectScale

description:
- Retrieves ObjectScale storage pool details.
- Supports listing all storage pools, listing by VDC, fetching by storage pool ID,
  and filtering by name.

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

  vdc_id:
    description:
    - VDC identifier to list storage pools for that VDC.
    type: str

  storage_pool_id:
    description:
    - Storage pool identifier to fetch a specific storage pool.
    type: str

  name:
    description:
    - Optional exact name filter applied client-side.
    type: str

notes:
- This is an info module. It always returns C(changed=false).
- Supports check mode.
'''

EXAMPLES = r'''
- name: List all storage pools
  dellemc.objectscale.storage_pool_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false

- name: List storage pools for a specific VDC
  dellemc.objectscale.storage_pool_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    vdc_id: "urn:storageos:VirtualDataCenterData:xxxx"

- name: Get storage pool by ID
  dellemc.objectscale.storage_pool_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    storage_pool_id: "urn:storageos:VirtualArray:xxxx"

- name: Filter storage pools by name
  dellemc.objectscale.storage_pool_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    name: "sp_ansible"
'''

RETURN = r'''
changed:
    description: Always false for info modules.
    returned: always
    type: bool

storage_pools:
    description: List of storage pools matching query criteria.
    returned: always
    type: list
    elements: dict
'''

from typing import Any, Dict, List, Optional

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import api_client as objectscale_api_client
except (ImportError, Exception):
    objectscale_api_client = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import _stubs as objectscale_client_stubs
except (ImportError, Exception):
    objectscale_client_stubs = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.object_varray_api import ObjectVarrayApi
except (ImportError, Exception):
    ObjectVarrayApi = None  # type: ignore[assignment,misc]


class StoragePoolInfo(object):
    """Class for gathering storage pool details from ObjectScale."""

    @staticmethod
    def _ensure_client_stub_compatibility() -> None:
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
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(
            dict(
                vdc_id=dict(type='str', required=False),
                storage_pool_id=dict(type='str', required=False),
                name=dict(type='str', required=False),
            )
        )

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
            mutually_exclusive=[('storage_pool_id', 'vdc_id')],
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
    def _sanitize_sensitive_fields(value: Any) -> Any:
        sensitive_keys = {
            'password', 'passwd', 'secret', 'token', 'auth_token', 'access_key', 'secret_key',
        }

        if isinstance(value, dict):
            sanitized: Dict[str, Any] = {}
            for key, val in value.items():
                if str(key).lower() in sensitive_keys:
                    sanitized[key] = '***'
                else:
                    sanitized[key] = StoragePoolInfo._sanitize_sensitive_fields(val)
            return sanitized

        if isinstance(value, list):
            return [StoragePoolInfo._sanitize_sensitive_fields(item) for item in value]

        return value

    @staticmethod
    def _to_dict(value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, 'to_dict'):
            return value.to_dict()
        return {}

    def _get_storage_pool_by_id(self, storage_pool_id: str) -> Dict[str, Any]:
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

    def _list_storage_pools(self, vdc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            kwargs: Dict[str, Any] = {}
            if vdc_id:
                kwargs['vdc_id'] = vdc_id
            response = self.storage_pool_api.object_varray_service_get_virtual_arrays(**kwargs)
            pools = [
                self._sanitize_sensitive_fields(self._to_dict(pool))
                for pool in (response.varray or [])
            ]
            return pools
        except Exception as e:
            status = getattr(e, 'status', None)
            if vdc_id and str(status) in ('404', '400'):
                self.module.exit_json(
                    failed=True,
                    msg="VDC '%s' does not exist or is invalid." % vdc_id,
                )
                return []
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Getting storage pool list failed with error: %s" % error_msg,
            )
            return []

    def get_storage_pools(self) -> List[Dict[str, Any]]:
        storage_pool_id = self.module.params.get('storage_pool_id')
        vdc_id = self.module.params.get('vdc_id')
        name = self.module.params.get('name')

        if storage_pool_id:
            pools = [self._get_storage_pool_by_id(storage_pool_id)]
        elif vdc_id:
            pools = self._list_storage_pools(vdc_id=vdc_id)
        else:
            pools = self._list_storage_pools()

        if name:
            pools = [pool for pool in pools if pool.get('name') == name]

        return pools

    def perform_module_operation(self) -> None:
        result = dict(
            changed=False,
            storage_pools=self.get_storage_pools(),
        )
        self.module.exit_json(**result)


def main() -> None:
    obj = StoragePoolInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
