#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible info module for VDC-level Management Users on Dell ObjectScale."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: management_user_info

version_added: '1.0.0'

short_description: Gathers information about Management Users on Dell ObjectScale

description:
- Retrieves details for a single Management User or lists all Management Users
  on Dell ObjectScale via the C(/vdc/users) REST API.
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
    - User identifier. When provided, returns details of the single user.
    - When omitted, returns a list of all Management Users.
    type: str
'''

EXAMPLES = r'''
- name: List all Management Users
  dellemc.objectscale.management_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
  register: all_mgmt_users

- name: Get a single Management User
  dellemc.objectscale.management_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_id: operator1
  register: mgmt_user
'''

RETURN = r'''
changed:
    description: Always false for info modules.
    returned: always
    type: bool
    sample: false
management_user:
    description: Details of a single Management User.
    returned: when I(user_id) is provided
    type: dict
management_users:
    description: List of Management User dicts.
    returned: when I(user_id) is omitted
    type: list
    elements: dict
'''

from typing import Any, Dict, List, Optional

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.mgmt_user_info_api import (
        MgmtUserInfoApi,
    )
except (ImportError, Exception):
    MgmtUserInfoApi = None  # type: ignore[assignment,misc]


class ManagementUserInfo(object):
    """Read-only operations on ObjectScale Management Users."""

    def __init__(self) -> None:
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(dict(
            user_id=dict(type='str', required=False, default=None),
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

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.mgmt_api.mgmt_user_info_service_get_local_user_info(userid=user_id)
            return resp.to_dict() if hasattr(resp, 'to_dict') else resp
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Management User %s not found or unreadable: %s" % (user_id, error_msg),
            )
            return None

    def list_users(self) -> List[Dict[str, Any]]:
        try:
            resp = self.mgmt_api.mgmt_user_info_service_get_local_user_infos()
            data = resp.to_dict() if hasattr(resp, 'to_dict') else resp
            users = (data or {}).get('mgmt_user_info') or []
            return list(users)
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(
                failed=True,
                msg="Listing Management Users failed with error: %s" % error_msg,
            )
            return []

    def perform_module_operation(self) -> None:
        user_id = self.module.params.get('user_id')
        if user_id:
            user = self.get_user(user_id)
            self.module.exit_json(changed=False, management_user=user)
        else:
            users = self.list_users()
            self.module.exit_json(changed=False, management_users=users)


def main() -> None:
    obj = ManagementUserInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
