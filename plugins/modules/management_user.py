#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing VDC-level Management Users on Dell ObjectScale."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: management_user

version_added: '1.0.0'

short_description: Manages VDC-level Management Users on Dell ObjectScale

description:
- Manages Management Users (administrators, operators, monitors, security admins)
  on the Dell ObjectScale storage system. This includes creating, modifying role
  assignments, changing password, and deleting Management Users via the
  C(/vdc/users) REST API. These users are VDC-scoped and are not associated with
  a namespace.
- C(Create), C(Update), and C(Delete) operations require the I(SECURITY_ADMIN) role.
- C(Read) operations require any one of I(SECURITY_ADMIN), I(SYSTEM_ADMIN), or
  I(SYSTEM_MONITOR) roles.

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
    description:
    - Unique identifier of the Management User. Upper case letters are not allowed.
    - If user_id does not contain C(@), the user is treated as a Local User.
    - If user_id contains C(@), the user is treated as an AD/LDAP User or
      AD/LDAP Group depending on I(is_external_group).
    type: str
    required: true
  password:
    description:
    - Password to set on the Management User.
    - Required when creating a Local User. Must not be provided for AD/LDAP
      Users or AD/LDAP Groups.
    - When provided during modify of a Local User, the password is (re)set;
      the module has no way to know the current password so providing this
      value always counts as a change.
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
    - Must be set to C(true) when creating an AD/LDAP Group.
    - Must not be set to C(true) for Local Users or AD/LDAP Users.
    type: bool
  state:
    description: Desired state of the Management User.
    type: str
    choices: [present, absent]
    default: present
'''

EXAMPLES = r'''
- name: Create a Local User with System Monitor role
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: localuser1
    password: "{{ local_user_password }}"
    is_system_monitor: true
    state: present

- name: Update Local User to System Admin and Security Admin roles
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: localuser1
    is_system_admin: true
    is_security_admin: true
    state: present

- name: Create an AD/LDAP User with System Monitor role
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: user1@domain
    is_system_monitor: true
    state: present

- name: Create an AD/LDAP Group with System Admin role
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: group1@domain
    is_system_admin: true
    is_external_group: true
    state: present

- name: Delete a Management User
  dellemc.objectscale.management_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: localuser1
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
except Exception:
    MgmtUserInfoApi = None  # type: ignore[assignment,misc]
    MgmtUserInfoServiceCreateLocalUserInfoRequest = None  # type: ignore[assignment,misc]
    MgmtUserInfoServiceModifyLocalUserInfoRequest = None  # type: ignore[assignment,misc]


ROLE_FIELDS = (
    ('is_system_admin', 'isSystemAdmin', 'is_system_admin'),
    ('is_system_monitor', 'isSystemMonitor', 'is_system_monitor'),
    ('is_security_admin', 'isSecurityAdmin', 'is_security_admin'),
)

USER_TYPE_LOCAL = 'local'
USER_TYPE_AD_LDAP_USER = 'ad_ldap_user'
USER_TYPE_AD_LDAP_GROUP = 'ad_ldap_group'
REDACTED_VALUE = '<REDACTED>'


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

    @staticmethod
    def _determine_user_type(user_id: str, is_external_group: Optional[bool]) -> str:
        """Determine the management user type from supplied parameters.

        - No '@' in user_id -> Local User
        - '@' in user_id and is_external_group is True -> AD/LDAP Group
        - '@' in user_id otherwise -> AD/LDAP User
        """
        if '@' not in user_id:
            return USER_TYPE_LOCAL
        if is_external_group:
            return USER_TYPE_AD_LDAP_GROUP
        return USER_TYPE_AD_LDAP_USER

    def _validate_local_user_create(self, user_id, params):
        """Validate create params for a Local Management User."""
        if not params.get('password'):
            self.module.exit_json(
                failed=True,
                msg="password is required when creating a Local Management User ('%s')." % user_id,
            )
        if params.get('is_external_group'):
            self.module.exit_json(
                failed=True,
                msg="is_external_group must not be true for a Local User ('%s')." % user_id,
            )

    def _validate_ad_ldap_user_create(self, user_type, user_id, params):
        """Validate create params for an AD/LDAP User or Group."""
        if params.get('password'):
            self.module.exit_json(
                failed=True,
                msg="password should not be provided when creating an AD/LDAP User ('%s')." % user_id,
            )
        if user_type == USER_TYPE_AD_LDAP_USER and params.get('is_external_group'):
            self.module.exit_json(
                failed=True,
                msg="is_external_group must not be true for an AD/LDAP User ('%s')." % user_id,
            )
        if user_type == USER_TYPE_AD_LDAP_GROUP and not params.get('is_external_group'):
            self.module.exit_json(
                failed=True,
                msg="is_external_group must be true when creating an AD/LDAP Group ('%s')." % user_id,
            )

    def _validate_create_params(self, user_type, user_id, params):
        """Validate parameter combinations for user creation."""
        if user_type == USER_TYPE_LOCAL:
            self._validate_local_user_create(user_id, params)
        else:
            self._validate_ad_ldap_user_create(user_type, user_id, params)

    def _validate_modify_params(self, user_type, user_id, params):
        """Validate parameter combinations for user modification."""
        if user_type in (USER_TYPE_AD_LDAP_USER, USER_TYPE_AD_LDAP_GROUP) and params.get('password'):
            self.module.exit_json(
                failed=True,
                msg="password should not be provided when updating an AD/LDAP User or Group ('%s')." % user_id,
            )
        if user_type in (USER_TYPE_LOCAL, USER_TYPE_AD_LDAP_USER) and params.get('is_external_group') is True:
            self.module.exit_json(
                failed=True,
                msg="is_external_group cannot be modified for a Local User or AD/LDAP User ('%s')." % user_id,
            )

    def _validate_params(self, user_type: str, user_id: str, params: Dict[str, Any], user_exists: bool) -> None:
        """Validate parameter combinations based on user type and operation."""
        if user_id != user_id.lower():
            self.module.exit_json(
                failed=True,
                msg="Upper case letters are not allowed in user_id. Got: '%s'." % user_id,
            )

        if not user_exists:
            self._validate_create_params(user_type, user_id, params)
        else:
            self._validate_modify_params(user_type, user_id, params)

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
        payload: Dict[str, Any] = dict(
            user_id=user_id,
            is_system_admin=params.get('is_system_admin'),
            is_system_monitor=params.get('is_system_monitor'),
            is_security_admin=params.get('is_security_admin'),
        )

        if params.get('password'):
            payload['password'] = params['password']
        if params.get('is_external_group') is not None:
            payload['is_external_group'] = params['is_external_group']

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

    def _handle_present_create(self, user_id, params, result):
        """Handle creating a new management user."""
        if not self.module.check_mode:
            self.create_user(user_id, params)
            details = self.get_user_details(user_id)
        else:
            details = None
        result['changed'] = True
        diff_after = {
            'user_id': user_id,
            'is_system_admin': bool(params.get('is_system_admin')),
            'is_system_monitor': bool(params.get('is_system_monitor')),
            'is_security_admin': bool(params.get('is_security_admin')),
            'password': REDACTED_VALUE if params.get('password') else None,
        }
        return details, diff_after

    def _handle_present_modify(self, user_id, details, params, result):
        """Handle modifying an existing management user."""
        diff_after = dict(self._public_details(details) or {})
        modify_params = self.is_user_modified(details, params)
        if modify_params:
            if not self.module.check_mode:
                if self.modify_user(user_id, modify_params):
                    details = self.get_user_details(user_id)
            result['changed'] = True
            diff_after = dict(self._public_details(details) or {})
            diff_after.update({
                k: (REDACTED_VALUE if k == 'password' else v)
                for k, v in modify_params.items()
            })
        return details, diff_after

    def _mgmt_handle_absent(self, user_id, details, diff_before, result):
        """Handle state=absent for a management user. Returns (details, diff_after)."""
        if details:
            if not self.module.check_mode:
                self.delete_user(user_id)
            result['changed'] = True
            return None, {}
        return details, dict(diff_before)

    def _mgmt_handle_present(self, user_id, details, params, result):
        """Handle state=present for a management user. Returns (details, diff_after)."""
        user_exists = details is not None
        is_external_group = details.get('is_external_group') if user_exists else params.get('is_external_group')
        user_type = self._determine_user_type(user_id, is_external_group)
        self._validate_params(user_type, user_id, params, user_exists)
        if not details:
            return self._handle_present_create(user_id, params, result)
        return self._handle_present_modify(user_id, details, params, result)

    def _apply_diff(self, diff_before, diff_after, result):
        """Attach diff to result dict if diff mode is active and changed."""
        if not (self.module._diff and result['changed']):
            return
        before = dict(diff_before)
        if 'password' in before:
            before['password'] = REDACTED_VALUE
        result['diff'] = {'before': before, 'after': diff_after}

    def perform_module_operation(self) -> None:
        result: Dict[str, Any] = dict(changed=False, management_user_details=None)
        params = self.module.params
        user_id = params['user_id']
        state = params['state']

        details = self.get_user_details(user_id)
        diff_before = self._public_details(details) or {}

        if state == 'absent':
            details, diff_after = self._mgmt_handle_absent(user_id, details, diff_before, result)
        else:
            details, diff_after = self._mgmt_handle_present(user_id, details, params, result)

        result['management_user_details'] = self._public_details(details)
        self._apply_diff(diff_before, diff_after, result)
        self.module.exit_json(**result)


def main() -> None:
    obj = ManagementUser()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
