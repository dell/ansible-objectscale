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
  This includes creating, modifying and deleting a namespace.

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

  default_object_project:
    description:
    - Default object project identifier used when creating buckets in this namespace.
    type: str

  allowed_vpools_list:
    description:
    - Desired list of replication groups allowed for this namespace.
    type: list
    elements: str

  disallowed_vpools_list:
    description:
    - Desired list of replication groups disallowed for this namespace.
    type: list
    elements: str

  namespace_admins:
    description:
    - List of user IDs to set as namespace administrators.
    type: list
    elements: str

  external_group_admins:
    description:
    - List of Active Directory groups to set as external namespace administrators.
    type: list
    elements: str

  user_mapping:
    description:
    - List of namespace user mapping entries.
    type: list
    elements: dict

  retention_classes:
    description:
    - Desired list of retention classes for the namespace.
    - Each entry should contain C(name) and C(period) in seconds.
    type: list
    elements: dict

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
    - Deprecated and currently unsupported by ObjectScale namespace API.
    type: int

  default_bucket_block_size:
    description:
    - Default bucket quota size for buckets created in this namespace.
    type: int

  is_object_lock_with_ado_allowed:
    description:
    - Whether Object Lock with ADO is allowed by default for new buckets in this namespace.
    type: bool

  default_audit_delete_expiration:
    description:
    - Default bucket audit delete expiration for the namespace.
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

  root_user_password:
    description:
    - Password for namespace virtual root user when creating a namespace.
    type: str

  current_root_user_password:
    description:
    - Current password for namespace virtual root user.
    type: str

  new_root_user_password:
    description:
    - New password for namespace virtual root user.
    type: str

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
- Use I(dellemc.objectscale.info) with C(gather_subset=namespace) for listing namespaces
  and getting namespace details by name.
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

- name: Configure namespace user mapping and retention class
  dellemc.objectscale.namespace:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "testnamespace"
    user_mapping:
      - domain: "example.com"
        groups:
          - "ops"
        attributes:
          - key: "department"
            value:
              - "engineering"
    retention_classes:
      - name: "compliance-7d"
        period: 604800
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

import json

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
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_create_namespace_request import (
        NamespaceServiceCreateNamespaceRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_create_retention_class_request import (
        NamespaceServiceCreateRetentionClassRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_response import (
        NamespaceServiceGetNamespaceResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_quota_response import (
        NamespaceServiceGetNamespaceQuotaResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_retention_classes_response import (
        NamespaceServiceGetRetentionClassesResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_request import (
        NamespaceServiceUpdateNamespaceRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_quota_request import (
        NamespaceServiceUpdateNamespaceQuotaRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_retention_class_request import (
        NamespaceServiceUpdateRetentionClassRequest,
    )

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_create_namespace_request import (
        NamespaceServiceCreateNamespaceRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_create_retention_class_request import (
        NamespaceServiceCreateRetentionClassRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_response import (
        NamespaceServiceGetNamespaceResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_namespace_quota_response import (
        NamespaceServiceGetNamespaceQuotaResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_get_retention_classes_response import (
        NamespaceServiceGetRetentionClassesResponse,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_request import (
        NamespaceServiceUpdateNamespaceRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_namespace_quota_request import (
        NamespaceServiceUpdateNamespaceQuotaRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.namespace_service_update_retention_class_request import (
        NamespaceServiceUpdateRetentionClassRequest,
    )
except (ImportError, Exception):
    NamespaceApi = None  # type: ignore[assignment,misc]
    NamespaceServiceCreateNamespaceRequest = None  # type: ignore[assignment,misc]
    NamespaceServiceCreateRetentionClassRequest = None  # type: ignore[assignment,misc]
    NamespaceServiceGetNamespaceResponse = None  # type: ignore[assignment,misc]
    NamespaceServiceGetNamespaceQuotaResponse = None  # type: ignore[assignment,misc]
    NamespaceServiceGetRetentionClassesResponse = None  # type: ignore[assignment,misc]
    NamespaceServiceUpdateNamespaceRequest = None  # type: ignore[assignment,misc]
    NamespaceServiceUpdateNamespaceQuotaRequest = None  # type: ignore[assignment,misc]
    NamespaceServiceUpdateRetentionClassRequest = None  # type: ignore[assignment,misc]


class Namespace(object):
    """Class with operations on ObjectScale namespace"""

    @staticmethod
    def _ensure_client_stub_compatibility() -> None:
        """Patch generated stubs for runtime compatibility when pydantic is absent.

        In environments without pydantic, generated stubs may map SecretStr to str.
        In that case, ApiClient treats normal strings as SecretStr and calls
        get_secret_value() on them, which fails. This runtime guard keeps behavior
        compatible without modifying generated module_utils code.
        """
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
        """Build API payload compatible with real pydantic models and stub mode.

        When generated client falls back to _stubs.BaseModel, model instances do
        not preserve fields and produce empty payloads. In that mode, pass plain
        dictionaries to the generated API client.
        """
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
        self.module_params.update(self.get_namespace_parameters())

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
            self._ensure_client_stub_compatibility()
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.namespace_api = namespace_api_cls(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

        self.module.log('Connected to ObjectScale at %s' % self.module.params['objectscale_host'])

    def get_namespace_details(self, namespace_name: str) -> Optional[Dict[str, Any]]:
        """Get the details of a namespace."""
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
            msg = "Getting namespace %s details failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    @staticmethod
    def _normalize_string_list(value: Any) -> List[str]:
        """Normalize comma-delimited strings or list-like values into list[str]."""
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item and item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    @staticmethod
    def _normalize_user_mapping(value: Any) -> List[str]:
        """Normalize user-mapping list to stable JSON strings for comparison."""
        if not isinstance(value, list):
            return []

        normalized: List[str] = []
        for entry in value:
            if hasattr(entry, 'to_dict'):
                normalized.append(json.dumps(entry.to_dict(), sort_keys=True))
            elif isinstance(entry, dict):
                normalized.append(json.dumps(entry, sort_keys=True))
        return sorted(normalized)

    def _normalize_retention_classes(self, value: Any) -> Dict[str, int]:
        """Normalize desired retention classes into {name: period} map."""
        normalized: Dict[str, int] = {}
        if value is None:
            return normalized

        if not isinstance(value, list):
            self.module.exit_json(
                failed=True,
                msg="retention_classes must be a list of dictionaries with name and period.",
            )
            return normalized

        for entry in value:
            if not isinstance(entry, dict):
                self.module.exit_json(
                    failed=True,
                    msg="Each retention_classes entry must be a dictionary with name and period.",
                )
                return normalized

            name = entry.get('name')
            period = entry.get('period')
            if not name or period is None:
                self.module.exit_json(
                    failed=True,
                    msg="Each retention_classes entry must include both name and period.",
                )
                return normalized

            try:
                normalized[str(name)] = int(period)
            except (TypeError, ValueError):
                self.module.exit_json(
                    failed=True,
                    msg="Retention class period must be an integer number of seconds.",
                )
                return normalized

        return normalized

    def create_namespace(self, namespace_name: str, params: Dict[str, Any]) -> Optional[bool]:
        """Create a namespace."""
        if not params.get('default_data_services_vpool'):
            self.module.exit_json(
                failed=True,
                msg="default_data_services_vpool is required when creating a namespace."
            )

        if NamespaceServiceCreateNamespaceRequest is None:
            self.module.exit_json(
                failed=True,
                msg="Namespace create request model is unavailable. Rebuild/install objectscale_client.",
            )

        namespace_admins = self._normalize_string_list(params.get('namespace_admins'))
        external_group_admins = self._normalize_string_list(params.get('external_group_admins'))
        payload = dict(
            namespace=namespace_name,
            default_object_project=params.get('default_object_project'),
            default_data_services_vpool=params['default_data_services_vpool'],
            allowed_vpools_list=params.get('allowed_vpools_list'),
            disallowed_vpools_list=params.get('disallowed_vpools_list'),
            namespace_admins=(
                ','.join(namespace_admins) if namespace_admins else None
            ),
            user_mapping=params.get('user_mapping'),
            compliance_enabled=params.get('is_compliance_enabled'),
            is_encryption_enabled=params.get('is_encryption_enabled'),
            default_bucket_block_size=params.get('default_bucket_block_size'),
            external_group_admins=(
                ','.join(external_group_admins) if external_group_admins else None
            ),
            is_stale_allowed=params.get('is_stale_allowed'),
            is_object_lock_with_ado_allowed=params.get('is_object_lock_with_ado_allowed'),
            default_audit_delete_expiration=params.get('default_audit_delete_expiration'),
            root_user_password=params.get('root_user_password'),
        )

        try:
            request = self._build_api_payload(NamespaceServiceCreateNamespaceRequest, payload)
            self.namespace_api.namespace_service_create_namespace(request)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating namespace %s failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def modify_namespace(
        self,
        namespace_name: str,
        params_to_modify: Dict[str, Any],
        namespace_details: Optional[Dict[str, Any]] = None,
    ) -> Optional[bool]:
        """Modify a namespace."""
        update_params = params_to_modify.copy()

        if 'user_mapping' not in update_params:
            if namespace_details is None:
                namespace_details = self.get_namespace_details(namespace_name) or {}
            current_mapping = (namespace_details or {}).get('user_mapping') or []
            update_params['user_mapping'] = current_mapping

        if update_params.get('namespace_admins') is not None:
            admins = self._normalize_string_list(update_params.get('namespace_admins'))
            update_params['namespace_admins'] = ','.join(admins) if admins else None

        if update_params.get('external_group_admins') is not None:
            groups = self._normalize_string_list(update_params.get('external_group_admins'))
            update_params['external_group_admins'] = ','.join(groups) if groups else None

        if NamespaceServiceUpdateNamespaceRequest is None:
            self.module.exit_json(
                failed=True,
                msg="Namespace update request model is unavailable. Rebuild/install objectscale_client.",
            )

        try:
            request = self._build_api_payload(NamespaceServiceUpdateNamespaceRequest, update_params)
            self.namespace_api.namespace_service_update_namespace(
                namespace=namespace_name,
                namespace_service_update_namespace_request=request,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Modifying namespace %s failed with error: %s" % (namespace_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def delete_namespace(self, namespace_name: str) -> Optional[bool]:
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

    def get_quota_details(self, namespace_name: str) -> Optional[Dict[str, Any]]:
        """Get quota details for a namespace."""
        try:
            response = (
                self.namespace_api.namespace_service_get_namespace_quota(
                    namespace=namespace_name,
                )
            )
            return response.to_dict() if hasattr(response, 'to_dict') else response
        except Exception as e:
            self.module.warn("Could not get quota for namespace %s: %s" % (namespace_name, str(e)))
            return None

    def get_retention_classes(self, namespace_name: str) -> Dict[str, int]:
        """Get retention classes configured on namespace as {name: period} map."""
        try:
            response = self.namespace_api.namespace_service_get_retention_classes(
                namespace=namespace_name,
            )
            retention_classes: Dict[str, int] = {}
            for retention in (response.retention_class or []):
                if isinstance(retention, dict):
                    name = retention.get('name')
                    period = retention.get('period')
                else:
                    name = getattr(retention, 'name', None)
                    period = getattr(retention, 'period', None)
                if name and period is not None:
                    retention_classes[str(name)] = int(period)
            return retention_classes
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return {}
            error_msg = utils.determine_error(e)
            msg = "Getting retention classes for namespace %s failed with error: %s" % (
                namespace_name,
                error_msg,
            )
            self.module.exit_json(failed=True, msg=msg)

    def sync_retention_classes(self, namespace_name: str, retention_classes: Any) -> bool:
        """Create/update retention classes to match desired state."""
        desired = self._normalize_retention_classes(retention_classes)
        existing = self.get_retention_classes(namespace_name)
        changed = False

        if NamespaceServiceCreateRetentionClassRequest is None or NamespaceServiceUpdateRetentionClassRequest is None:
            self.module.exit_json(
                failed=True,
                msg="Retention class request models are unavailable. Rebuild/install objectscale_client.",
            )
        for class_name, period in desired.items():
            current_period = existing.get(class_name)
            try:
                if current_period is None:
                    request = self._build_api_payload(
                        NamespaceServiceCreateRetentionClassRequest,
                        dict(name=class_name, period=period),
                    )
                    self.namespace_api.namespace_service_create_retention_class(
                        namespace=namespace_name,
                        namespace_service_create_retention_class_request=request,
                    )
                    changed = True
                elif int(current_period) != int(period):
                    request = self._build_api_payload(
                        NamespaceServiceUpdateRetentionClassRequest,
                        dict(period=period),
                    )
                    self.namespace_api.namespace_service_update_retention_class(
                        namespace=namespace_name,
                        var_class=class_name,
                        namespace_service_update_retention_class_request=request,
                    )
                    changed = True
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Updating retention class %s for namespace %s failed with error: %s" % (
                    class_name,
                    namespace_name,
                    error_msg,
                )
                self.module.exit_json(failed=True, msg=msg)

        return changed

    def modify_quota(self, namespace_name: str, params: Dict[str, Any]) -> Optional[bool]:
        """Update quota settings for a namespace."""
        if params.get('quota_enabled') is False:
            try:
                self.namespace_api.namespace_service_remove_namespace_quota(
                    namespace=namespace_name,
                )
                return True
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Removing quota for namespace %s failed with error: %s" % (
                    namespace_name,
                    error_msg,
                )
                self.module.exit_json(failed=True, msg=msg)

        if NamespaceServiceUpdateNamespaceQuotaRequest is None:
            self.module.exit_json(
                failed=True,
                msg="Namespace quota request model is unavailable. Rebuild/install objectscale_client.",
            )

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
            request = self._build_api_payload(NamespaceServiceUpdateNamespaceQuotaRequest, quota_fields)
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
            'default_data_services_vpool': 'default_data_services_vpool',
            'is_encryption_enabled': 'is_encryption_enabled',
            'is_stale_allowed': 'is_stale_allowed',
            'default_bucket_block_size': 'default_bucket_block_size',
            'is_object_lock_with_ado_allowed': 'is_object_lock_with_ado_allowed',
            'default_audit_delete_expiration': 'default_audit_delete_expiration',
        }
        for param_key, detail_key in field_map.items():
            if params.get(param_key) is not None:
                if detail_key in namespace_details and params[param_key] != namespace_details.get(detail_key):
                    modify_params[param_key] = params[param_key]

        if params.get('current_root_user_password') or params.get('new_root_user_password'):
            if not (params.get('current_root_user_password') and params.get('new_root_user_password')):
                self.module.exit_json(
                    failed=True,
                    msg="Both current_root_user_password and new_root_user_password are required to update root user password.",
                )
            modify_params['current_root_user_password'] = params.get('current_root_user_password')
            modify_params['new_root_user_password'] = params.get('new_root_user_password')

        if params.get('namespace_admins') is not None:
            # API returns namespace_admins as a comma-separated string
            admins_obj = namespace_details.get('namespace_admins', '')
            if isinstance(admins_obj, str):
                current_admins = [a.strip() for a in admins_obj.split(',') if a.strip()]
            elif isinstance(admins_obj, list):
                current_admins = admins_obj
            else:
                current_admins = []
            if set(self._normalize_string_list(params.get('namespace_admins'))) != set(current_admins):
                modify_params['namespace_admins'] = params.get('namespace_admins')

        if params.get('external_group_admins') is not None:
            groups_obj = namespace_details.get('external_group_admins', '')
            current_groups = self._normalize_string_list(groups_obj)
            desired_groups = self._normalize_string_list(params.get('external_group_admins'))
            if set(desired_groups) != set(current_groups):
                modify_params['external_group_admins'] = params.get('external_group_admins')

        if params.get('allowed_vpools_list') is not None:
            desired_allowed = set(self._normalize_string_list(params.get('allowed_vpools_list')))
            current_allowed = set(self._normalize_string_list(namespace_details.get('allowed_vpools_list')))
            added = sorted(desired_allowed - current_allowed)
            removed = sorted(current_allowed - desired_allowed)
            if added:
                modify_params['vpools_added_to_allowed_vpools_list'] = added
            if removed:
                modify_params['vpools_removed_from_allowed_vpools_list'] = removed

        if params.get('disallowed_vpools_list') is not None:
            desired_disallowed = set(self._normalize_string_list(params.get('disallowed_vpools_list')))
            current_disallowed = set(self._normalize_string_list(namespace_details.get('disallowed_vpools_list')))
            added = sorted(desired_disallowed - current_disallowed)
            removed = sorted(current_disallowed - desired_disallowed)
            if added:
                modify_params['vpools_added_to_disallowed_vpools_list'] = added
            if removed:
                modify_params['vpools_removed_from_disallowed_vpools_list'] = removed

        if params.get('user_mapping') is not None:
            desired_user_mapping = self._normalize_user_mapping(params.get('user_mapping'))
            current_user_mapping = self._normalize_user_mapping(namespace_details.get('user_mapping'))
            if desired_user_mapping != current_user_mapping:
                modify_params['user_mapping'] = params.get('user_mapping')

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

    def is_quota_modified(self, quota_details: Optional[Dict[str, Any]], params: Dict[str, Any]) -> bool:
        """Determine if quota settings need to be modified."""
        if quota_details is None:
            return any(
                params.get(field) is not None
                for field in ['blocked_quota_size', 'notification_quota_size', 'soft_quota_size', 'hard_quota_size']
            ) or params.get('quota_enabled') is False

        if params.get('quota_enabled') is not None:
            current_enabled = quota_details.get('quota_enabled')
            if current_enabled is not None and params.get('quota_enabled') != current_enabled:
                return True

        if params.get('quota_enabled') is False:
            return True

        field_map = {
            'blocked_quota_size': 'block_size',
            'notification_quota_size': 'notification_size',
            'hard_quota_size': 'block_size_in_count',
            'soft_quota_size': 'notification_size_in_count',
        }
        for param_key, detail_key in field_map.items():
            current_value = quota_details.get(detail_key)
            if current_value is None:
                current_value = quota_details.get(param_key)
            if params.get(param_key) is not None and params[param_key] != current_value:
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

        if state == 'absent':
            if namespace_details:
                self.delete_namespace(namespace_name)
                result['changed'] = True
        elif state == 'present':
            if not namespace_details:
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
                      'soft_quota_size', 'hard_quota_size']) and quota_details is None:
                self.modify_quota(namespace_name, params)
                result['changed'] = True

            if params.get('retention_classes') is not None:
                if self.sync_retention_classes(namespace_name, params.get('retention_classes')):
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
            default_object_project=dict(type='str'),
            allowed_vpools_list=dict(type='list', elements='str'),
            disallowed_vpools_list=dict(type='list', elements='str'),
            namespace_admins=dict(type='list', elements='str'),
            external_group_admins=dict(type='list', elements='str'),
            user_mapping=dict(type='list', elements='dict'),
            retention_classes=dict(type='list', elements='dict'),
            is_compliance_enabled=dict(type='bool'),
            is_encryption_enabled=dict(type='bool'),
            is_stale_allowed=dict(type='bool'),
            allowed_protocols=dict(type='list', elements='str'),
            default_replication_factor=dict(type='int'),
            default_bucket_block_size=dict(type='int'),
            is_object_lock_with_ado_allowed=dict(type='bool'),
            default_audit_delete_expiration=dict(type='int'),
            quota_enabled=dict(type='bool'),
            blocked_quota_size=dict(type='int'),
            notification_quota_size=dict(type='int'),
            soft_quota_size=dict(type='int'),
            hard_quota_size=dict(type='int'),
            root_user_password=dict(type='str', no_log=True),
            current_root_user_password=dict(type='str', no_log=True),
            new_root_user_password=dict(type='str', no_log=True),
            state=dict(required=True, type='str', choices=['present', 'absent']),
        )


def main() -> None:
    """Create ObjectScale Namespace object and perform actions on it."""
    obj = Namespace()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
