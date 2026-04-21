#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible info module for non-IAM Object Users on Dell ObjectScale."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: object_user_info

version_added: '1.1.0'

short_description: Gathers information about non-IAM Object Users on Dell ObjectScale

description:
- Retrieves details for a single Object User or lists Object Users for a
  namespace or the whole VDC via the C(/object/users) REST API. Optionally
  enriches each user with S3 secret key metadata (ids / timestamps only,
  plaintext values are never returned).

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

options:
  objectscale_host:
    description: IP address or FQDN of the ObjectScale management endpoint.
    type: str
    required: true
  objectscale_port:
    description: Port number for the ObjectScale management endpoint.
    type: int
    default: 4443
  objectscale_username:
    description: Username for authenticating with ObjectScale.
    type: str
    required: true
  objectscale_password:
    description: Password for authenticating with ObjectScale.
    type: str
    required: true
  validate_certs:
    description: Whether to verify SSL certificates.
    type: bool
    default: true
  timeout:
    description: HTTP request timeout in seconds.
    type: int
    default: 30
  user:
    description:
    - Identifier of the Object User. When provided, returns a single user.
    type: str
  namespace:
    description:
    - Namespace filter. When C(user) is provided, this qualifies the lookup.
      When C(user) is not provided, returns the list of users for this
      namespace.
    type: str
  include_secret_keys:
    description:
    - When C(true), enrich each user with S3 secret key metadata. Only key
      ids and timestamps are returned; plaintext secret values are never
      included.
    type: bool
    default: false
'''

EXAMPLES = r'''
- name: Get a single Object User
  dellemc.objectscale.object_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user: alice
    namespace: ns1
  register: user_info

- name: List users in a namespace with secret key metadata
  dellemc.objectscale.object_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: ns1
    include_secret_keys: true

- name: List all Object Users in the VDC
  dellemc.objectscale.object_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
'''

RETURN = r'''
changed:
    description: Always false for info modules.
    returned: always
    type: bool
    sample: false
object_user:
    description: A single Object User dict.
    returned: when I(user) is provided
    type: dict
object_users:
    description: List of Object User dicts.
    returned: when I(user) is not provided
    type: list
    elements: dict
'''

from typing import Any, Dict, List, Optional

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.user_management_api import (
        UserManagementApi,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.user_secret_key_api import (
        UserSecretKeyApi,
    )
except (ImportError, Exception):
    UserManagementApi = None  # type: ignore[assignment,misc]
    UserSecretKeyApi = None  # type: ignore[assignment,misc]


class ObjectUserInfo(object):
    """Read-only operations on non-IAM Object Users."""

    def __init__(self) -> None:
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(dict(
            user=dict(type='str', required=False, default=None),
            namespace=dict(type='str', required=False, default=None),
            include_secret_keys=dict(type='bool', default=False),
        ))
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
        if UserManagementApi is None or UserSecretKeyApi is None:
            self.module.exit_json(
                failed=True,
                msg="ObjectScale Object User / Secret Key API clients unavailable. Rebuild/install objectscale_client.",
            )
            return
        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.user_mgmt_api = UserManagementApi(self.api_client)
            self.secret_key_api = UserSecretKeyApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))
            return

    def get_user(self, user: str, namespace: Optional[str]) -> Optional[Dict[str, Any]]:
        try:
            if namespace:
                resp = self.user_mgmt_api.user_management_service_get_user_info(
                    uid=user, namespace=namespace,
                )
            else:
                resp = self.user_mgmt_api.user_management_service_get_user_info(uid=user)
            return resp.to_dict() if hasattr(resp, 'to_dict') else resp
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Object User %s not found or unreadable: %s" % (user, error_msg),
            )
            return None

    def list_users_in_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        try:
            resp = self.user_mgmt_api.user_management_service_get_users_for_namespace(
                namespace=namespace,
            )
            data = resp.to_dict() if hasattr(resp, 'to_dict') else (resp or {})
            return list((data or {}).get('blobuser') or [])
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Listing Object Users for namespace %s failed with error: %s" % (namespace, error_msg),
            )
            return []

    def list_all_users(self) -> List[Dict[str, Any]]:
        try:
            resp = self.user_mgmt_api.user_management_service_get_all_users()
            data = resp.to_dict() if hasattr(resp, 'to_dict') else (resp or {})
            return list((data or {}).get('blobuser') or [])
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Listing all Object Users failed with error: %s" % error_msg,
            )
            return []

    def get_secret_key_metadata(
        self, user: str, namespace: Optional[str]
    ) -> List[Dict[str, Any]]:
        try:
            if namespace:
                resp = self.secret_key_api.user_secret_key_service_get_keys_for_user1(
                    uid=user, namespace=namespace,
                )
            else:
                resp = self.secret_key_api.user_secret_key_service_get_keys_for_user(
                    uid=user,
                )
            data = resp.to_dict() if hasattr(resp, 'to_dict') else (resp or {})
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return []
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Listing secret keys for Object User %s failed with error: %s" % (user, error_msg),
            )
            return []

        metadata: List[Dict[str, Any]] = []
        for idx in (1, 2):
            exists = data.get('secret_key_%d_exist' % idx)
            key_id = data.get('secret_key_%d_id' % idx)
            if exists or key_id:
                metadata.append({
                    'secret_key_id': key_id,
                    'key_timestamp': data.get('key_timestamp_%d' % idx),
                    'key_expiry_timestamp': data.get('key_expiry_timestamp_%d' % idx),
                })
        return metadata

    def perform_module_operation(self) -> None:
        params = self.module.params
        user = params.get('user')
        namespace = params.get('namespace')
        include_keys = bool(params.get('include_secret_keys'))

        if user:
            details = self.get_user(user, namespace)
            if include_keys and details is not None:
                details['secret_key_metadata'] = self.get_secret_key_metadata(user, namespace)
            self.module.exit_json(changed=False, object_user=details)
            return

        if namespace:
            users = self.list_users_in_namespace(namespace)
        else:
            users = self.list_all_users()

        if include_keys:
            for entry in users:
                uid = entry.get('userid') or entry.get('name') or entry.get('user')
                if uid:
                    entry['secret_key_metadata'] = self.get_secret_key_metadata(uid, namespace)

        self.module.exit_json(changed=False, object_users=users)


def main() -> None:
    obj = ObjectUserInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
