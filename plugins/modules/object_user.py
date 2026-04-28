#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing namespace-scoped (non-IAM) Object Users on Dell ObjectScale."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: object_user

version_added: '1.0.0'

short_description: Manages non-IAM Object Users on Dell ObjectScale

description:
- Manages namespace-scoped (non-IAM) Object Users on the Dell ObjectScale storage
  system using the C(/object/users) and C(/object/user-secret-keys) REST APIs.
- Supports create, delete, tag reconciliation, lock state management, and S3
  secret key lifecycle (create/delete) for the user.
- For IAM-based user management, use the M(dellemc.objectscale.iam_user) module
  instead.

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
    description: Identifier of the Object User.
    type: str
    required: true
  namespace:
    description: Namespace the Object User belongs to.
    type: str
    required: true
  tags:
    description:
    - Desired list of tags. Each entry must contain C(name) and C(value).
    type: list
    elements: dict
  purge_tags:
    description:
    - When C(true), tags not in the desired set are removed.
    type: bool
    default: true
  locked:
    description:
    - Desired lock state. When set, the module ensures the user is locked
      (C(true)) or unlocked (C(false)).
    type: bool
  secret_keys:
    description:
    - Desired S3 secret key declarations. Each entry is a dict with C(state)
      (C(present) or C(absent)) and optional C(secret_key_id),
      C(secret_key), and C(existing_key_expiry_time_mins).
    - For C(state=present) with no existing keys matching, a new key is
      generated and its plaintext returned once under
      C(created_secret_keys).
    - For C(state=absent), BOTH C(secret_key_id) AND C(secret_key) must be provided
      to delete a specific key. The API requires the actual secret key value for
      security verification. Since secret keys are only returned once at creation,
      you must save the key value if you plan to delete it later. Note that even
      deleting all keys requires the actual key values for namespace-scoped users.
    type: list
    elements: dict
  state:
    description: Desired state of the Object User.
    type: str
    choices: [present, absent]
    default: present
'''

EXAMPLES = r'''
- name: Create an Object User in a namespace
  dellemc.objectscale.object_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user: alice
    namespace: ns1
    tags:
      - { name: env, value: prod }
    state: present

- name: Create an S3 secret key for the user
  dellemc.objectscale.object_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user: alice
    namespace: ns1
    secret_keys:
      - state: present
    state: present
  register: s3_keys
  no_log: true

- name: Lock the Object User
  dellemc.objectscale.object_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user: alice
    namespace: ns1
    locked: true

- name: Delete a specific secret key (requires both ID and the actual key value)
  dellemc.objectscale.object_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user: alice
    namespace: ns1
    secret_keys:
      - secret_key_id: "{{ saved_key_id }}"
        secret_key: "{{ saved_key_value }}"
        state: absent
    state: present
  no_log: true

- name: Delete the Object User
  dellemc.objectscale.object_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user: alice
    namespace: ns1
    state: absent
'''

RETURN = r'''
changed:
    description: Whether the resource was changed.
    returned: always
    type: bool
object_user_details:
    description: Details of the Object User after the operation.
    returned: when the user exists
    type: dict
created_secret_keys:
    description:
    - S3 secret keys newly created during this run. Plaintext is returned
      once at creation time and should be captured securely (e.g., via
      Ansible Vault).
    returned: when a secret key was created
    type: list
    elements: dict
'''

from typing import Any, Dict, List, Optional, Tuple

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
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_management_service_add_user_request import (  # noqa: E501
        UserManagementServiceAddUserRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_management_service_remove_user_request import (  # noqa: E501
        UserManagementServiceRemoveUserRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_management_service_add_user_tag_request import (  # noqa: E501
        UserManagementServiceAddUserTagRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_management_service_remove_user_tags_request import (  # noqa: E501
        UserManagementServiceRemoveUserTagsRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_management_service_update_user_tag_request import (  # noqa: E501
        UserManagementServiceUpdateUserTagRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_management_service_set_user_lock_request import (  # noqa: E501
        UserManagementServiceSetUserLockRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_secret_key_service_create_new_key_for_user_request import (  # noqa: E501
        UserSecretKeyServiceCreateNewKeyForUserRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.user_secret_key_service_delete_key_for_user_request import (  # noqa: E501
        UserSecretKeyServiceDeleteKeyForUserRequest,
    )
except (ImportError, Exception):
    UserManagementApi = None  # type: ignore[assignment,misc]
    UserSecretKeyApi = None  # type: ignore[assignment,misc]
    UserManagementServiceAddUserRequest = None  # type: ignore[assignment,misc]
    UserManagementServiceRemoveUserRequest = None  # type: ignore[assignment,misc]
    UserManagementServiceAddUserTagRequest = None  # type: ignore[assignment,misc]
    UserManagementServiceRemoveUserTagsRequest = None  # type: ignore[assignment,misc]
    UserManagementServiceUpdateUserTagRequest = None  # type: ignore[assignment,misc]
    UserManagementServiceSetUserLockRequest = None  # type: ignore[assignment,misc]
    UserSecretKeyServiceCreateNewKeyForUserRequest = None  # type: ignore[assignment,misc]
    UserSecretKeyServiceDeleteKeyForUserRequest = None  # type: ignore[assignment,misc]


class ObjectUser(object):
    """Class with operations on non-IAM Object Users."""

    @staticmethod
    def _build_api_payload(model_cls: Any, payload: Dict[str, Any]) -> Any:
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
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_object_user_parameters())
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

    @staticmethod
    def get_object_user_parameters() -> Dict[str, Dict[str, Any]]:
        return dict(
            user=dict(type='str', required=True),
            namespace=dict(type='str', required=True),
            tags=dict(type='list', elements='dict', required=False),
            purge_tags=dict(type='bool', default=True),
            locked=dict(type='bool', required=False),
            secret_keys=dict(
                type='list', elements='dict', required=False, no_log=True,
            ),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
        )

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------
    def get_user_details(self, user: str, namespace: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.user_mgmt_api.user_management_service_get_user_info(
                uid=user, namespace=namespace,
            )
            return resp.to_dict() if hasattr(resp, 'to_dict') else resp
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Getting Object User %s (namespace=%s) failed with error: %s" % (user, namespace, error_msg),
            )
            return None

    def create_user(
        self, user: str, namespace: str, tags: Optional[List[Dict[str, Any]]]
    ) -> bool:
        try:
            payload = dict(user=user, namespace=namespace)
            if tags:
                payload['tags'] = tags
            request = self._build_api_payload(UserManagementServiceAddUserRequest, payload)
            self.user_mgmt_api.user_management_service_add_user(
                user_management_service_add_user_request=request,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Creating Object User %s failed with error: %s" % (user, error_msg),
            )
            return False

    def delete_user(self, user: str, namespace: str) -> bool:
        try:
            request = self._build_api_payload(
                UserManagementServiceRemoveUserRequest,
                dict(user=user, namespace=namespace),
            )
            self.user_mgmt_api.user_management_service_remove_user(
                user_management_service_remove_user_request=request,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Deleting Object User %s failed with error: %s" % (user, error_msg),
            )
            return False

    # ------------------------------------------------------------------
    # Tag reconciliation
    # ------------------------------------------------------------------
    @staticmethod
    def _tags_to_map(tags: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for t in (tags or []):
            if isinstance(t, dict) and 'name' in t:
                out[str(t['name'])] = t.get('value')
        return out

    def sync_tags(
        self,
        user: str,
        namespace: Optional[str],
        current_tags: Optional[List[Dict[str, Any]]],
        desired_tags: Optional[List[Dict[str, Any]]],
        purge_tags: bool = True,
        check_mode: bool = False,
    ) -> bool:
        if desired_tags is None:
            return False
        current_map = self._tags_to_map(current_tags)
        desired_map = self._tags_to_map(desired_tags)

        to_add: List[Dict[str, Any]] = []
        to_update: List[Dict[str, Any]] = []
        for name, value in desired_map.items():
            if name not in current_map:
                to_add.append({'name': name, 'value': value})
            elif current_map.get(name) != value:
                to_update.append({'name': name, 'value': value})

        to_remove: List[Dict[str, Any]] = []
        if purge_tags:
            for name in current_map:
                if name not in desired_map:
                    to_remove.append({'name': name})

        if not (to_add or to_update or to_remove):
            return False

        if check_mode:
            return True

        try:
            if to_add:
                req = self._build_api_payload(
                    UserManagementServiceAddUserTagRequest,
                    dict(tags=to_add),
                )
                self.user_mgmt_api.user_management_service_add_user_tag(
                    uid=user,
                    user_management_service_add_user_tag_request=req,
                    namespace=namespace,
                )
            if to_update:
                req = self._build_api_payload(
                    UserManagementServiceUpdateUserTagRequest,
                    dict(tags=to_update),
                )
                self.user_mgmt_api.user_management_service_update_user_tag(
                    uid=user,
                    user_management_service_update_user_tag_request=req,
                    namespace=namespace,
                )
            if to_remove:
                req = self._build_api_payload(
                    UserManagementServiceRemoveUserTagsRequest,
                    dict(tags=[{'name': t['name']} for t in to_remove]),
                )
                self.user_mgmt_api.user_management_service_remove_user_tags(
                    uid=user,
                    user_management_service_remove_user_tags_request=req,
                    namespace=namespace,
                )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Updating tags for Object User %s failed with error: %s" % (user, error_msg),
            )
            return False
        return True

    # ------------------------------------------------------------------
    # Lock management
    # ------------------------------------------------------------------
    def sync_lock(
        self,
        user: str,
        namespace: Optional[str],
        current_locked: Optional[bool],
        desired_locked: Optional[bool],
        check_mode: bool = False,
    ) -> bool:
        if desired_locked is None:
            return False
        if bool(current_locked) == bool(desired_locked):
            return False
        if check_mode:
            return True
        try:
            payload: Dict[str, Any] = dict(user=user, is_locked=bool(desired_locked))
            if namespace:
                payload['namespace'] = namespace
            req = self._build_api_payload(UserManagementServiceSetUserLockRequest, payload)
            self.user_mgmt_api.user_management_service_set_user_lock(
                user_management_service_set_user_lock_request=req,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Setting lock state for Object User %s failed with error: %s" % (user, error_msg),
            )
            return False

    # ------------------------------------------------------------------
    # Secret key management
    # ------------------------------------------------------------------
    def _list_existing_secret_keys(self, user: str, namespace: Optional[str]) -> List[Dict[str, Any]]:
        """Return list of existing secret key metadata as dicts."""
        try:
            if namespace:
                resp = self.secret_key_api.user_secret_key_service_get_keys_for_user1(
                    uid=user, namespace=namespace,
                )
            else:
                resp = self.secret_key_api.user_secret_key_service_get_keys_for_user(uid=user)
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

        keys: List[Dict[str, Any]] = []
        for idx in (1, 2):
            exists = data.get('secret_key_%d_exist' % idx)
            key_id = data.get('secret_key_%d_id' % idx)
            if exists or key_id:
                keys.append({
                    'secret_key_id': key_id,
                    'key_timestamp': data.get('key_timestamp_%d' % idx),
                    'key_expiry_timestamp': data.get('key_expiry_timestamp_%d' % idx),
                })
        return keys

    def sync_secret_keys(
        self,
        user: str,
        namespace: Optional[str],
        desired: Optional[List[Dict[str, Any]]],
        check_mode: bool = False,
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Reconcile secret keys against declarations.

        Returns (changed, created_keys). ``created_keys`` contains plaintext
        secrets that callers must capture securely.
        """
        created: List[Dict[str, Any]] = []
        if not desired:
            return False, created

        existing = self._list_existing_secret_keys(user, namespace)
        existing_ids = {k.get('secret_key_id') for k in existing if k.get('secret_key_id')}
        changed = False

        for entry in desired:
            entry_state = entry.get('state', 'present')
            entry_id = entry.get('secret_key_id')
            entry_secret = entry.get('secret_key')

            if entry_state == 'present':
                # If caller declares a specific id that already exists -> noop
                if entry_id and entry_id in existing_ids:
                    continue
                # If no id specified but keys already exist -> noop (cap 2 keys)
                if not entry_id and len(existing) >= 2:
                    continue
                # Otherwise create a new key
                if check_mode:
                    changed = True
                    continue
                payload = dict(
                    namespace=namespace,
                    secretkey=entry_secret,
                    existing_key_expiry_time_mins=entry.get('existing_key_expiry_time_mins'),
                )
                try:
                    req = self._build_api_payload(
                        UserSecretKeyServiceCreateNewKeyForUserRequest, payload,
                    )
                    resp = self.secret_key_api.user_secret_key_service_create_new_key_for_user(
                        uid=user,
                        user_secret_key_service_create_new_key_for_user_request=req,
                    )
                    resp_data = resp.to_dict() if hasattr(resp, 'to_dict') else (resp or {})
                    created.append({
                        'secret_key': resp_data.get('secret_key'),
                        'secret_key_id': resp_data.get('secret_key_id'),
                        'key_timestamp': resp_data.get('key_timestamp'),
                        'key_expiry_timestamp': resp_data.get('key_expiry_timestamp'),
                    })
                    changed = True
                except Exception as e:
                    error_msg = utils.determine_error(e)
                    self.module.exit_json(
                        failed=True,
                        msg="Creating secret key for Object User %s failed with error: %s" % (user, error_msg),
                    )

            elif entry_state == 'absent':
                if not (entry_id or entry_secret):
                    continue
                # Skip if target is already gone
                if entry_id and entry_id not in existing_ids:
                    continue
                # Validate that both secret_key_id and secret_key are provided for deletion
                if entry_id and not entry_secret:
                    self.module.exit_json(
                        failed=True,
                        msg="Deleting secret keys requires both 'secret_key_id' and 'secret_key'. "
                            "The API requires the actual secret key value for security verification. "
                            "Since secret keys are only returned once at creation time, you must save "
                            "the key value if you plan to delete it later."
                    )
                if check_mode:
                    changed = True
                    continue
                payload = dict(
                    secret_key=entry_secret,
                    secret_key_id=entry_id,
                    namespace=namespace,
                )
                try:
                    req = self._build_api_payload(
                        UserSecretKeyServiceDeleteKeyForUserRequest, payload,
                    )
                    self.secret_key_api.user_secret_key_service_delete_key_for_user(
                        uid=user,
                        user_secret_key_service_delete_key_for_user_request=req,
                    )
                    changed = True
                except Exception as e:
                    error_msg = utils.determine_error(e)
                    self.module.exit_json(
                        failed=True,
                        msg="Deleting secret key for Object User %s failed with error: %s" % (user, error_msg),
                    )
        return changed, created

    # ------------------------------------------------------------------
    # Main operation
    # ------------------------------------------------------------------
    def perform_module_operation(self) -> None:
        params = self.module.params
        user = params['user']
        namespace = params['namespace']
        state = params['state']

        result: Dict[str, Any] = dict(changed=False, object_user_details=None)
        created_keys: List[Dict[str, Any]] = []

        details = self.get_user_details(user, namespace)
        diff_before = dict(details) if details else {}
        diff_after = dict(diff_before)

        if state == 'absent':
            if details:
                if not self.module.check_mode:
                    self.delete_user(user, namespace)
                result['changed'] = True
                details = None
                diff_after = {}
        else:
            if not details:
                if not self.module.check_mode:
                    self.create_user(user, namespace, params.get('tags'))
                    details = self.get_user_details(user, namespace)
                result['changed'] = True
                diff_after = dict(details) if details else {}

                # Set lock state after creation if specified
                if params.get('locked') is not None:
                    if self.sync_lock(
                        user, namespace,
                        False,  # New users are unlocked by default
                        params['locked'],
                        check_mode=self.module.check_mode,
                    ):
                        result['changed'] = True
                        if not self.module.check_mode:
                            details = self.get_user_details(user, namespace)
                            diff_after = dict(details) if details else {}
            else:
                if params.get('tags') is not None:
                    if self.sync_tags(
                        user, namespace,
                        details.get('tag'), params['tags'], params.get('purge_tags', True),
                        check_mode=self.module.check_mode,
                    ):
                        result['changed'] = True
                        if not self.module.check_mode:
                            details = self.get_user_details(user, namespace)
                            diff_after = dict(details) if details else {}

                if params.get('locked') is not None:
                    if self.sync_lock(
                        user, namespace,
                        bool(details.get('locked')) if details else False,
                        params['locked'],
                        check_mode=self.module.check_mode,
                    ):
                        result['changed'] = True
                        if not self.module.check_mode:
                            details = self.get_user_details(user, namespace)
                            diff_after = dict(details) if details else {}

            if params.get('secret_keys'):
                key_changed, created_keys = self.sync_secret_keys(
                    user, namespace, params['secret_keys'], check_mode=self.module.check_mode,
                )
                if key_changed:
                    result['changed'] = True
                    if not self.module.check_mode:
                        details = self.get_user_details(user, namespace)
                        diff_after = dict(details) if details else {}

        result['object_user_details'] = details
        if created_keys:
            result['created_secret_keys'] = created_keys

        if self.module._diff and result['changed']:
            result['diff'] = {'before': diff_before, 'after': diff_after}

        self.module.exit_json(**result)


def main() -> None:
    obj = ObjectUser()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
