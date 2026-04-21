#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing VDC-level Management Users on Dell ObjectScale."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: management_user

version_added: '1.1.0'

short_description: Manages VDC-level Management Users on Dell ObjectScale

description:
- Manages Management Users (administrators, operators, monitors, security admins)
  on the Dell ObjectScale storage system. This includes creating, modifying role
  assignments, changing password, and deleting Management Users via the
  C(/vdc/users) REST API. These users are VDC-scoped and are not associated with
  a namespace.

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
  user_id:
    description: Unique identifier of the Management User.
    type: str
    required: true
  password:
    description:
    - Password to set on the Management User. Required when creating.
    - When provided during modify, the password is (re)set; the module has no
      way to know the current password so providing this value always counts
      as a change.
    type: str
  is_system_admin:
    description: Assign/remove the System Admin role.
    type: bool
  is_system_monitor:
    description: Assign/remove the System Monitor role.
    type: bool
  is_security_admin:
    description: Assign/remove the Security Admin role.
    type: bool
  is_external_group:
    description:
    - Indicates the user is an external (domain) group. Only honored on create.
    type: bool
  state:
    description: Desired state of the Management User.
    type: str
    choices: [present, absent]
    default: present
'''

EXAMPLES = r'''
- name: Create a Management User with System Monitor role
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: operator1
    password: "{{ operator1_password }}"
    is_system_monitor: true
    state: present

- name: Promote Management User to System Admin
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: operator1
    is_system_admin: true
    state: present

- name: Delete a Management User
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: operator1
    state: absent
'''

RETURN = r'''
changed:
    description: Whether the resource was changed.
    returned: always
    type: bool
    sample: true
management_user_details:
    description: Management User details after the operation.
    returned: when the user exists
    type: dict
    contains:
        user_id:
            description: Management user identifier.
            type: str
        is_system_admin:
            description: True if the user holds the System Admin role.
            type: bool
        is_system_monitor:
            description: True if the user holds the System Monitor role.
            type: bool
        is_security_admin:
            description: True if the user holds the Security Admin role.
            type: bool
        is_external_group:
            description: True if this is an external/domain group entry.
            type: bool
        is_locked:
            description: True if the user is currently locked.
            type: bool
        last_time_password_changed:
            description: ISO-8601 timestamp of last password change.
            type: str
    sample:
        user_id: "operator1"
        is_system_admin: false
        is_system_monitor: true
        is_security_admin: false
        is_external_group: false
        is_locked: false
        last_time_password_changed: "2026-04-21T09:00:00Z"
diff:
    description: Diff between before and after state (when --diff is used).
    returned: when --diff is active and something changed
    type: dict
'''

from typing import Any, Dict, Optional

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.mgmt_user_info_api import (
        MgmtUserInfoApi,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.mgmt_user_info_service_create_local_user_info_request import (  # noqa: E501
        MgmtUserInfoServiceCreateLocalUserInfoRequest,
    )
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.mgmt_user_info_service_modify_local_user_info_request import (  # noqa: E501
        MgmtUserInfoServiceModifyLocalUserInfoRequest,
    )
except (ImportError, Exception):
    MgmtUserInfoApi = None  # type: ignore[assignment,misc]
    MgmtUserInfoServiceCreateLocalUserInfoRequest = None  # type: ignore[assignment,misc]
    MgmtUserInfoServiceModifyLocalUserInfoRequest = None  # type: ignore[assignment,misc]


ROLE_FIELDS = (
    ('is_system_admin', 'isSystemAdmin', 'is_system_admin'),
    ('is_system_monitor', 'isSystemMonitor', 'is_system_monitor'),
    ('is_security_admin', 'isSecurityAdmin', 'is_security_admin'),
)


class ManagementUser(object):
    """Class with operations on ObjectScale Management Users."""

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
        self.module_params.update(self.get_management_user_parameters())

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

        if MgmtUserInfoApi is None:
            self.module.exit_json(
                failed=True,
                msg="ObjectScale Management User API client is unavailable. Rebuild/install objectscale_client.",
            )
            return

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.mgmt_api = MgmtUserInfoApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))
            return

    @staticmethod
    def get_management_user_parameters() -> Dict[str, Dict[str, Any]]:
        return dict(
            user_id=dict(type='str', required=True),
            password=dict(type='str', required=False, no_log=True),
            is_system_admin=dict(type='bool', required=False),
            is_system_monitor=dict(type='bool', required=False),
            is_security_admin=dict(type='bool', required=False),
            is_external_group=dict(type='bool', required=False),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
        )

    def get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Return user dict, or None when the user does not exist."""
        try:
            resp = self.mgmt_api.mgmt_user_info_service_get_local_user_info(userid=user_id)
            return resp.to_dict() if hasattr(resp, 'to_dict') else resp
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Getting Management User %s details failed with error: %s" % (user_id, error_msg),
            )
            return None

    def create_user(self, user_id: str, params: Dict[str, Any]) -> Optional[bool]:
        password = params.get('password')
        if not password:
            self.module.exit_json(
                failed=True,
                msg="password is required when creating Management User '%s'." % user_id,
            )
            return None

        payload = dict(
            user_id=user_id,
            password=password,
            is_system_admin=params.get('is_system_admin'),
            is_system_monitor=params.get('is_system_monitor'),
            is_security_admin=params.get('is_security_admin'),
            is_external_group=params.get('is_external_group'),
        )

        try:
            request = self._build_api_payload(
                MgmtUserInfoServiceCreateLocalUserInfoRequest, payload
            )
            self.mgmt_api.mgmt_user_info_service_create_local_user_info(
                mgmt_user_info_service_create_local_user_info_request=request,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Creating Management User %s failed with error: %s" % (user_id, error_msg),
            )
            return None

    def modify_user(self, user_id: str, params_to_modify: Dict[str, Any]) -> bool:
        if not params_to_modify:
            return False
        try:
            request = self._build_api_payload(
                MgmtUserInfoServiceModifyLocalUserInfoRequest, params_to_modify
            )
            self.mgmt_api.mgmt_user_info_service_modify_local_user_info(
                userid=user_id,
                mgmt_user_info_service_modify_local_user_info_request=request,
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Modifying Management User %s failed with error: %s" % (user_id, error_msg),
            )
            return False

    def delete_user(self, user_id: str) -> bool:
        try:
            self.mgmt_api.mgmt_user_info_service_delete_local_user_info(userid=user_id)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Deleting Management User %s failed with error: %s" % (user_id, error_msg),
            )
            return False

    def is_user_modified(
        self, details: Dict[str, Any], params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return dict of fields to modify (only drifted fields)."""
        modify: Dict[str, Any] = {}
        for param_key, api_alias, payload_key in ROLE_FIELDS:
            desired = params.get(param_key)
            if desired is None:
                continue
            current = details.get(api_alias)
            if current is None:
                current = details.get(param_key)
            if bool(current) != bool(desired):
                modify[payload_key] = desired

        if params.get('password'):
            modify['password'] = params['password']
        return modify

    @staticmethod
    def _public_details(details: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Return a normalized, snake_case view of user details for module output."""
        if not details:
            return details
        alias_map = {
            'userId': 'user_id',
            'isSystemAdmin': 'is_system_admin',
            'isSystemMonitor': 'is_system_monitor',
            'isSecurityAdmin': 'is_security_admin',
        }
        out: Dict[str, Any] = {}
        for key, value in details.items():
            out[alias_map.get(key, key)] = value
        return out

    def perform_module_operation(self) -> None:
        result: Dict[str, Any] = dict(changed=False, management_user_details=None)
        params = self.module.params
        user_id = params['user_id']
        state = params['state']

        details = self.get_user_details(user_id)
        diff_before = self._public_details(details) or {}
        diff_after = dict(diff_before)

        if state == 'absent':
            if details:
                if not self.module.check_mode:
                    self.delete_user(user_id)
                result['changed'] = True
                diff_after = {}
                details = None
        else:  # present
            if not details:
                if not self.module.check_mode:
                    self.create_user(user_id, params)
                    details = self.get_user_details(user_id)
                result['changed'] = True
                diff_after = {
                    'user_id': user_id,
                    'is_system_admin': bool(params.get('is_system_admin')),
                    'is_system_monitor': bool(params.get('is_system_monitor')),
                    'is_security_admin': bool(params.get('is_security_admin')),
                    'password': '<REDACTED>' if params.get('password') else None,
                }
            else:
                modify_params = self.is_user_modified(details, params)
                if modify_params:
                    if not self.module.check_mode:
                        if self.modify_user(user_id, modify_params):
                            details = self.get_user_details(user_id)
                    result['changed'] = True
                    diff_after = dict(self._public_details(details) or {})
                    diff_after.update({
                        k: ('<REDACTED>' if k == 'password' else v)
                        for k, v in modify_params.items()
                    })

        result['management_user_details'] = self._public_details(details)

        if self.module._diff and result['changed']:
            before = dict(diff_before)
            if 'password' in before:
                before['password'] = '<REDACTED>'
            result['diff'] = {'before': before, 'after': diff_after}

        self.module.exit_json(**result)


def main() -> None:
    obj = ManagementUser()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
