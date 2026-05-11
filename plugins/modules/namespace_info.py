#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering namespace information from Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: namespace_info

version_added: '1.0.0'

short_description: Gather namespace information from Dell ObjectScale

description:
- Gather information about ObjectScale namespaces.
- Supports listing all namespaces.
- Supports fetching a single namespace by name.
- Supports filtering namespace list with wildcard prefix matching.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

extends_documentation_fragment:
- dellemc.objectscale.objectscale

options:
  namespace_name:
    description:
    - Name of the namespace to retrieve.
    - If specified, returns at most one matching namespace.
    type: str
    required: false

  match:
    description:
    - Wildcard prefix filter for namespace names (for example C(team-*)).
    - Cannot be used with I(namespace_name).
    type: str
    required: false


notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: List all namespaces
  dellemc.objectscale.namespace_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
  register: namespace_info_result

- name: Get namespace details by name
  dellemc.objectscale.namespace_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "testnamespace"
  register: namespace_info_result

- name: List namespaces by prefix
  dellemc.objectscale.namespace_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    match: "team-*"
  register: namespace_info_result
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed. Always false for info modules.
    returned: always
    type: bool
    sample: false

namespaces:
    description: List of namespaces from the ObjectScale system.
    returned: always
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
'''

from typing import Any, Dict, List, Optional
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
    HAS_OBJECTSCALE_CLIENT,
    paginate_with_next_marker
)

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import api_client as objectscale_api_client
except Exception:
    objectscale_api_client = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import _stubs as objectscale_client_stubs
except Exception:
    objectscale_client_stubs = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.namespace_api import NamespaceApi
except Exception:
    NamespaceApi = None  # type: ignore[assignment,misc]


class NamespaceInfo(object):
    """Class for gathering namespace information from ObjectScale."""

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
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(dict(
            namespace_name=dict(type='str', required=False),
            match=dict(type='str', required=False),
        ))

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            mutually_exclusive=[('namespace_name', 'match')],
            supports_check_mode=True,
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.fail_json(
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )
            return

        if NamespaceApi is None:
            self.module.fail_json(
                msg="ObjectScale namespace API client is unavailable. Rebuild/install objectscale_client."
            )
            return

        try:
            self._ensure_secretstr_compatibility()
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.namespace_api = NamespaceApi(self.api_client)
        except Exception as e:
            self.module.fail_json(msg="Failed to connect to ObjectScale: %s" % str(e))
            return

    def get_namespace_details(self, namespace_name: str) -> Optional[Dict[str, Any]]:
        """Get namespace details by namespace name."""
        try:
            response = self.namespace_api.namespace_service_get_namespace(id=namespace_name)
            return response.to_dict() if hasattr(response, 'to_dict') else response
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            self.module.fail_json(
                msg="Getting namespace %s details failed with error: %s" % (namespace_name, error_msg)
            )
            return None

    def list_namespaces(self) -> List[Dict[str, Any]]:
        """List namespaces with auto-pagination and optional name matching."""
        base_kwargs: Dict[str, Any] = {}
        if self.module.params.get('match'):
            base_kwargs['name'] = str(self.module.params.get('match'))

        try:
            all_namespaces = paginate_with_next_marker(
                api_call=self.namespace_api.namespace_service_get_namespaces,
                base_kwargs=base_kwargs,
                items_key='namespace'
            )
            return [
                ns.to_dict() if hasattr(ns, 'to_dict') else ns
                for ns in (all_namespaces or [])
            ]
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(msg="Getting namespace list failed with error: %s" % error_msg)
            return []

    def perform_module_operation(self) -> None:
        """Gather namespace information and return results."""
        namespace_name = self.module.params.get('namespace_name')

        if namespace_name:
            namespace_details = self.get_namespace_details(namespace_name)
            namespaces = [namespace_details] if namespace_details else []
        else:
            namespaces = self.list_namespaces()

        self.module.exit_json(changed=False, namespaces=namespaces)


def main() -> None:
    """Create NamespaceInfo object and perform module operation."""
    obj = NamespaceInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
