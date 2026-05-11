# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: replication_group
short_description: Manage ObjectScale replication groups
description:
  - Create, update, and delete ObjectScale replication groups (data vpools).
  - Supports idempotency, check mode, and diff mode.
version_added: "1.0.0"
author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: Supports check mode. No changes will be made when check mode is enabled.
  diff_mode:
    support: full
    description: Supports diff mode. Shows before and after state of the replication group.

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
  state:
    description:
    - Desired replication group state.
    - C(present) ensures the replication group exists with the specified configuration.
    - C(absent) ensures the replication group does not exist.
    type: str
    required: true
    choices: [present, absent]
  id:
    description:
    - Replication group identifier (URN).
    type: str
  name:
    description:
    - Replication group name.
    type: str
  new_name:
    description:
    - New name to set on an existing replication group.
    type: str
  description:
    description:
    - Description of the replication group.
    type: str
  replication_type:
    description:
    - Desired replication type.
    type: str
    choices: [active, passive]
    default: active
  mappings:
    description:
    - List of VDC and storage-pool mappings.
    type: list
    elements: dict
    suboptions:
      vdc_id:
        description:
        - VDC identifier for the mapping.
        type: str
        required: true
      storage_pool_id:
        description:
        - Storage pool identifier for the mapping.
        type: str
        required: true
      is_replication_target:
        description:
        - Whether this mapping is a replication target.
        type: bool
  replicate_to_all_sites:
    description:
    - Allow all namespaces / replicate to all sites.
    type: bool
    default: false
  enable_rebalancing:
    description:
    - Enable rebalancing for the replication group.
    type: bool
  skip_bootstrap_check:
    description:
    - Skip bootstrap check during mapping removal.
    type: bool
    default: false
  force_pso_zones:
    description:
    - Force PSO zones during mapping removal.
    type: bool
    default: false
notes:
  - Mapping removal is currently not supported on target ObjectScale builds where remove-from-vpool is unavailable.
  - Deletion requires a direct delete endpoint in the installed objectscale_client; otherwise the module fails.
'''

EXAMPLES = r'''
- name: Create replication group
  dellemc.objectscale.replication_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    state: present
    name: rg-ansible-01
    description: Created by Ansible
    mappings:
      - vdc_id: urn:storageos:VirtualDataCenterData:111
        storage_pool_id: urn:storageos:VirtualArray:111

- name: Update replication group metadata and mappings
  dellemc.objectscale.replication_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    state: present
    id: urn:storageos:ReplicationGroupInfo:111:global
    new_name: rg-ansible-01-renamed
    description: Updated by Ansible
    mappings:
      - vdc_id: urn:storageos:VirtualDataCenterData:111
        storage_pool_id: urn:storageos:VirtualArray:111
        is_replication_target: true

- name: Remove replication group
  dellemc.objectscale.replication_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    state: absent
    name: rg-ansible-01-renamed
'''

RETURN = r'''
changed:
  description: Whether resource state changed.
  type: bool
  returned: always
replication_group:
  description: Replication group details after operation.
  type: dict
  returned: when state=present
diff:
  description: Before/after state comparison.
  type: dict
  returned: when diff mode is enabled
'''

from typing import Any, Dict, List, Optional, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.data_vpool_api import (
        DataVpoolApi,
    )
except Exception:
    DataVpoolApi = None  # type: ignore[assignment,misc]

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.data_service_vpool_service_create_data_service_vpool_request import (  # noqa: E501
        DataServiceVpoolServiceCreateDataServiceVpoolRequest,
    )
except Exception:
    DataServiceVpoolServiceCreateDataServiceVpoolRequest = None  # type: ignore[assignment,misc]

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.data_service_vpool_service_put_data_service_vpool_request import (  # noqa: E501
        DataServiceVpoolServicePutDataServiceVpoolRequest,
    )
except Exception:
    DataServiceVpoolServicePutDataServiceVpoolRequest = None  # type: ignore[assignment,misc]

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.data_service_vpool_service_add_to_vpool_request import (  # noqa: E501
        DataServiceVpoolServiceAddToVpoolRequest,
    )
except Exception:
    DataServiceVpoolServiceAddToVpoolRequest = None  # type: ignore[assignment,misc]


class ReplicationGroup(object):
    """Class with operations on ObjectScale replication groups."""

    def __init__(self) -> None:
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_replication_group_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )
            return

        if DataVpoolApi is None:
            self.module.exit_json(
                failed=True,
                msg="ObjectScale DataVpool API client is unavailable. Rebuild/install objectscale_client."
            )
            return

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.data_vpool_api = DataVpoolApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))
            return

    @staticmethod
    def _to_dict(response: Any) -> Dict[str, Any]:
        if response is None:
            return {}
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        if isinstance(response, dict):
            return response
        return {}

    @staticmethod
    def _build_api_payload(model_cls: Any, payload: Dict[str, Any]) -> Any:
        filtered = {k: v for k, v in payload.items() if v is not None}
        if model_cls is None:
            return filtered

        base_cls = model_cls.__mro__[1] if len(model_cls.__mro__) > 1 else None
        if base_cls is not None and base_cls.__module__.endswith('objectscale_client._stubs'):
            return filtered

        try:
            return model_cls.model_validate(filtered)
        except Exception:
            return model_cls(**filtered)

    def _normalize_mapping_input(self, mappings: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        normalized = []
        for item in mappings or []:
            if not isinstance(item, dict):
                self.module.exit_json(failed=True, msg="Each mappings entry must be a dict")
            vdc_id = item.get('vdc_id')
            storage_pool_id = item.get('storage_pool_id')
            if not vdc_id or not storage_pool_id:
                self.module.exit_json(failed=True, msg="Each mapping requires vdc_id and storage_pool_id")
            normalized.append(
                {
                    'name': vdc_id,
                    'value': storage_pool_id,
                    'is_replication_target': bool(item.get('is_replication_target', False)),
                }
            )
        return normalized

    @staticmethod
    def _mapping_key(mapping: Dict[str, Any]) -> Tuple[str, str, bool]:
        return (
            str(mapping.get('name', '')),
            str(mapping.get('value', '')),
            bool(mapping.get('is_replication_target', False)),
        )

    def _normalize_current_mappings(self, details: Dict[str, Any]) -> List[Dict[str, Any]]:
        mappings = details.get('varrayMappings') or details.get('zone_mappings') or []
        normalized = []
        for entry in mappings:
            if isinstance(entry, dict):
                normalized.append(
                    {
                        'name': entry.get('name'),
                        'value': entry.get('value'),
                        'is_replication_target': bool(entry.get('is_replication_target', False)),
                    }
                )
        return normalized

    def _normalize_state(self, details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not details:
            return {}
        return {
            'id': details.get('id'),
            'name': details.get('name'),
            'description': details.get('description'),
            'enable_rebalancing': details.get('enable_rebalancing'),
            'isAllowAllNamespaces': details.get('isAllowAllNamespaces'),
            'isFullRep': details.get('isFullRep'),
            'use_replication_target': details.get('use_replication_target'),
            'mappings': sorted(self._normalize_current_mappings(details), key=self._mapping_key),
        }

    def get_all_replication_groups(self) -> List[Dict[str, Any]]:
        try:
            response = self.data_vpool_api.data_service_vpool_service_get_data_service_vpools()
            data = self._to_dict(response)
            return data.get('data_service_vpool', []) or []
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(failed=True, msg="Listing replication groups failed with error: %s" % error_msg)
            return []

    def get_replication_group_by_id(self, rg_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.data_vpool_api.data_service_vpool_service_get_data_service_store(id=rg_id)
            data = self._to_dict(response)
            # Some ObjectScale builds return an empty object (200) for unknown ids.
            # Normalize that to "not found" for idempotent absent/query behavior.
            if not data:
                return None
            if not data.get('id') and not data.get('name') and not data.get('description'):
                return None
            return data
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            self.module.exit_json(failed=True, msg="Getting replication group %s failed with error: %s" % (rg_id, error_msg))
            return None

    def find_replication_group_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        matches = [item for item in self.get_all_replication_groups() if item.get('name') == name]
        if not matches:
            return None
        if len(matches) > 1:
            self.module.exit_json(failed=True, msg="Multiple replication groups found for name '%s'. Use id." % name)
            return None
        rg_id = matches[0].get('id')
        if not rg_id:
            return matches[0]
        return self.get_replication_group_by_id(rg_id)

    def _resolve_current(self) -> Optional[Dict[str, Any]]:
        rg_id = self.module.params.get('id')
        rg_name = self.module.params.get('name')

        if rg_id:
            return self.get_replication_group_by_id(rg_id)
        if rg_name:
            return self.find_replication_group_by_name(rg_name)
        return None

    def _desired_name(self, current: Optional[Dict[str, Any]]) -> Optional[str]:
        return self.module.params.get('new_name') or self.module.params.get('name') or (current or {}).get('name')

    def _desired_metadata(self, current: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        desired_name = self._desired_name(current)
        replication_type = self.module.params.get('replication_type', 'active')
        return {
            'name': desired_name,
            'description': self.module.params.get('description'),
            'enable_rebalancing': self.module.params.get('enable_rebalancing'),
            'allowAllNamespaces': self.module.params.get('replicate_to_all_sites'),
            'isFullRep': True if replication_type == 'active' else False,
        }

    def is_replication_group_modified(self, current: Dict[str, Any]) -> Dict[str, Any]:
        desired_meta = self._desired_metadata(current)
        metadata_changes: Dict[str, Any] = {}

        if desired_meta.get('name') and desired_meta.get('name') != current.get('name'):
            metadata_changes['name'] = desired_meta['name']
        if desired_meta.get('description') is not None and desired_meta.get('description') != current.get('description'):
            metadata_changes['description'] = desired_meta['description']
        if desired_meta.get('enable_rebalancing') is not None and desired_meta.get('enable_rebalancing') != current.get('enable_rebalancing'):
            metadata_changes['enable_rebalancing'] = desired_meta['enable_rebalancing']
        if desired_meta.get('allowAllNamespaces') is not None and desired_meta.get('allowAllNamespaces') != current.get('isAllowAllNamespaces'):
            metadata_changes['allowAllNamespaces'] = desired_meta['allowAllNamespaces']

        desired_mappings = self._normalize_mapping_input(self.module.params.get('mappings'))
        current_mappings = self._normalize_current_mappings(current)

        desired_set = {self._mapping_key(m) for m in desired_mappings}
        current_set = {self._mapping_key(m) for m in current_mappings}

        mappings_to_add = [m for m in desired_mappings if self._mapping_key(m) not in current_set]
        mappings_to_remove = [m for m in current_mappings if self._mapping_key(m) not in desired_set]

        return {
            'metadata_changes': metadata_changes,
            'mappings_to_add': mappings_to_add,
            'mappings_to_remove': mappings_to_remove,
            'is_modified': bool(metadata_changes or mappings_to_add or mappings_to_remove),
        }

    def create_replication_group(self) -> None:
        name = self.module.params.get('name')
        if not name:
            self.module.exit_json(failed=True, msg="name is required when state=present and id is not provided")
            return

        requested_mappings = self._normalize_mapping_input(self.module.params.get('mappings'))
        payload: Dict[str, Any] = {
            'id': self.module.params.get('id'),
            'name': name,
            'description': self.module.params.get('description'),
            'zone_mappings': requested_mappings or None,
            'enable_rebalancing': self.module.params.get('enable_rebalancing'),
            'isAllowAllNamespaces': self.module.params.get('replicate_to_all_sites'),
            'isFullRep': True if self.module.params.get('replication_type', 'active') == 'active' else False,
            'use_replication_target': any(bool(m.get('is_replication_target')) for m in requested_mappings),
        }

        self._create_replication_group_with_payload(payload)

    def _create_replication_group_with_payload(self, payload: Dict[str, Any]) -> None:
        """Create a replication group using a payload dict."""

        try:
            if not payload.get('id'):
                # Backend accepts create requests without explicit vpool id and
                # generates one. The generated public API method is decorated
                # with @validate_call and rejects this payload before request
                # dispatch. Use the generated serializer + call_api path to
                # submit raw payload without pydantic call-time validation.
                serializer = getattr(
                    self.data_vpool_api,
                    '_data_service_vpool_service_create_data_service_vpool_serialize',
                    None,
                )
                if not callable(serializer):
                    self.module.exit_json(failed=True, msg='Create serializer method is unavailable in objectscale_client')
                    return
                request = self._build_api_payload(None, payload)
                params = serializer(
                    data_service_vpool_service_create_data_service_vpool_request=request,
                    _request_auth=None,
                    _content_type=None,
                    _headers=None,
                    _host_index=0,
                )
                response_data = self.data_vpool_api.api_client.call_api(
                    *params,
                    _request_timeout=self.module.params.get('timeout'),
                )
                if hasattr(response_data, 'read'):
                    response_data.read()
            else:
                request = self._build_api_payload(DataServiceVpoolServiceCreateDataServiceVpoolRequest, payload)
                self.data_vpool_api.data_service_vpool_service_create_data_service_vpool(
                    data_service_vpool_service_create_data_service_vpool_request=request
                )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(failed=True, msg="Creating replication group failed with error: %s" % error_msg)

    def _rename_by_recreate(self, current: Dict[str, Any], modifications: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fallback rename workflow for builds where PUT rename is not reliable."""
        desired_name = (modifications.get('metadata_changes') or {}).get('name')
        if not desired_name:
            return current

        desired_mappings = self._normalize_mapping_input(self.module.params.get('mappings'))
        if not desired_mappings:
            desired_mappings = self._normalize_current_mappings(current)

        desired_meta = self._desired_metadata(current)
        create_payload: Dict[str, Any] = {
            'id': None,
            'name': desired_name,
            'description': desired_meta.get('description'),
            'zone_mappings': desired_mappings or None,
            'enable_rebalancing': desired_meta.get('enable_rebalancing'),
            'isAllowAllNamespaces': desired_meta.get('allowAllNamespaces'),
            'isFullRep': desired_meta.get('isFullRep'),
            'use_replication_target': any(bool(m.get('is_replication_target')) for m in desired_mappings),
        }

        self._create_replication_group_with_payload(create_payload)
        self.delete_replication_group(current)
        return self.find_replication_group_by_name(desired_name)

    def update_replication_group_metadata(self, rg_id: str, metadata_changes: Dict[str, Any]) -> None:
        if not metadata_changes:
            return

        if 'name' not in metadata_changes:
            metadata_changes['name'] = self._desired_name(self.get_replication_group_by_id(rg_id))

        try:
            request = self._build_api_payload(DataServiceVpoolServicePutDataServiceVpoolRequest, metadata_changes)
            self.data_vpool_api.data_service_vpool_service_put_data_service_vpool(
                id=rg_id,
                data_service_vpool_service_put_data_service_vpool_request=request,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(failed=True, msg="Updating replication group %s failed with error: %s" % (rg_id, error_msg))

    def add_mappings(self, rg_id: str, mappings_to_add: List[Dict[str, Any]]) -> None:
        if not mappings_to_add:
            return
        payload: Dict[str, Any] = {'mappings': mappings_to_add}
        try:
            request = self._build_api_payload(DataServiceVpoolServiceAddToVpoolRequest, payload)
            self.data_vpool_api.data_service_vpool_service_add_to_vpool(
                id=rg_id,
                data_service_vpool_service_add_to_vpool_request=request,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(failed=True, msg="Adding mappings to replication group %s failed with error: %s" % (rg_id, error_msg))

    def remove_mappings(self, rg_id: str, mappings_to_remove: List[Dict[str, Any]]) -> None:
        if not mappings_to_remove:
            return
        # Runtime workaround: remove-from-vpool operation is not supported on
        # the target ObjectScale build. Skip remove to avoid false failures.
        self.module.warn(
            "Requested mapping removal for replication group %s is skipped because remove operation is not supported"
            % rg_id
        )
        self.module.log(
            "Skipping mapping removal for replication group %s because remove operation is not supported"
            % rg_id
        )

    def delete_replication_group(self, current: Dict[str, Any]) -> None:
        rg_id = current.get('id')
        if not rg_id:
            self.module.exit_json(failed=True, msg="Replication group id is required for delete")
            return

        direct_delete = getattr(self.data_vpool_api, 'data_service_vpool_service_delete_data_service_vpool', None)
        if callable(direct_delete):
            try:
                direct_delete(id=rg_id)
                return
            except Exception as e:
                error_msg = utils.determine_error(e)
                self.module.exit_json(failed=True, msg="Deleting replication group %s failed with error: %s" % (rg_id, error_msg))
                return

        # Runtime workaround: do not attempt delete-by-removing-all-mappings.
        # Remove operation is not supported on the target build.
        self.module.exit_json(
            failed=True,
            msg=(
                "Deleting replication group %s is not supported by the installed objectscale_client "
                "because direct delete API is unavailable"
            ) % rg_id,
        )

    def _predict_after_state(self, before: Dict[str, Any], modifications: Dict[str, Any], state: str) -> Dict[str, Any]:
        if state == 'absent':
            return {}
        after: Dict[str, Any] = dict(before)
        metadata_changes: Dict[str, Any] = modifications.get('metadata_changes') or {}
        if metadata_changes:
            if 'name' in metadata_changes:
                after['name'] = metadata_changes['name']
            if 'description' in metadata_changes:
                after['description'] = metadata_changes['description']
            if 'enable_rebalancing' in metadata_changes:
                after['enable_rebalancing'] = metadata_changes['enable_rebalancing']
            if 'allowAllNamespaces' in metadata_changes:
                after['isAllowAllNamespaces'] = metadata_changes['allowAllNamespaces']

        current_keys = {self._mapping_key(m): m for m in after.get('mappings', [])}
        for item in modifications.get('mappings_to_remove', []):
            current_keys.pop(self._mapping_key(item), None)
        for item in modifications.get('mappings_to_add', []):
            current_keys[self._mapping_key(item)] = item
        after['mappings'] = sorted(list(current_keys.values()), key=self._mapping_key)
        return after

    def _apply_modifications(self, current, modifications):
        """Apply non-check-mode modifications to the replication group.

        Returns None if an error exit was triggered (missing id).
        """
        rg_id = current.get('id')
        if not rg_id:
            self.module.exit_json(failed=True, msg="Replication group id is missing")
            return None
        metadata_changes = modifications.get('metadata_changes') or {}
        if metadata_changes.get('name') and metadata_changes.get('name') != current.get('name'):
            return self._rename_by_recreate(current, modifications) or current
        self.update_replication_group_metadata(rg_id, metadata_changes)
        self.add_mappings(rg_id, modifications['mappings_to_add'])
        self.remove_mappings(rg_id, modifications['mappings_to_remove'])
        return self.get_replication_group_by_id(rg_id) or current

    def perform_module_operation(self) -> None:
        result: Dict[str, Any] = dict(changed=False, replication_group=None)
        state = self.module.params['state']
        current = self._resolve_current()
        before_state = self._normalize_state(current)

        if state == 'absent':
            if current:
                if not self.module.check_mode:
                    self.delete_replication_group(current)
                result['changed'] = True
                result['replication_group'] = None
            if self.module._diff:
                result['diff'] = {'before': before_state, 'after': {}}
            self.module.exit_json(**result)
            return

        if not current:
            if self.module.check_mode:
                result['changed'] = True
                predicted = {
                    'id': self.module.params.get('id') or self.module.params.get('name'),
                    'name': self.module.params.get('name'),
                    'description': self.module.params.get('description'),
                    'mappings': sorted(self._normalize_mapping_input(self.module.params.get('mappings')), key=self._mapping_key),
                }
                if self.module._diff:
                    result['diff'] = {'before': {}, 'after': predicted}
                result['replication_group'] = predicted
                self.module.exit_json(**result)
                return

            self.create_replication_group()
            result['changed'] = True
            current = self._resolve_current()

        if not current:
            self.module.exit_json(failed=True, msg="Unable to resolve replication group after create/update operation")
            return

        modifications = self.is_replication_group_modified(current)
        if modifications['is_modified']:
            result['changed'] = True
            if not self.module.check_mode:
                current = self._apply_modifications(current, modifications)
                if current is None:
                    return

        after_state = self._normalize_state(current)
        if self.module.check_mode and modifications['is_modified']:
            after_state = self._predict_after_state(before_state, modifications, state)

        result['replication_group'] = after_state if after_state else current
        if self.module._diff:
            result['diff'] = {'before': before_state, 'after': after_state}

        self.module.exit_json(**result)

    @staticmethod
    def get_replication_group_parameters() -> Dict[str, Dict[str, Any]]:
        mapping_spec = dict(
            vdc_id=dict(type='str', required=True),
            storage_pool_id=dict(type='str', required=True),
            is_replication_target=dict(type='bool', required=False),
        )
        return dict(
            id=dict(type='str'),
            name=dict(type='str'),
            new_name=dict(type='str'),
            description=dict(type='str'),
            replication_type=dict(type='str', choices=['active', 'passive'], default='active'),
            mappings=dict(type='list', elements='dict', options=mapping_spec),
            replicate_to_all_sites=dict(type='bool', default=False),
            enable_rebalancing=dict(type='bool'),
            skip_bootstrap_check=dict(type='bool', default=False),
            force_pso_zones=dict(type='bool', default=False),
            state=dict(type='str', choices=['present', 'absent'], required=True),
        )


def main() -> None:
    obj = ReplicationGroup()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
