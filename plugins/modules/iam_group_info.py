#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering IAM group information from Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_group_info

version_added: '1.0.0'

short_description: Gather IAM group information from Dell ObjectScale

description:
- Gather information about IAM groups in a specific ObjectScale namespace.
- Can retrieve a single group by name or list all groups.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

extends_documentation_fragment:
- dellemc.objectscale.objectscale

options:
  namespace:
    description:
    - The ObjectScale namespace to query for IAM groups.
    type: str
    required: true

  group_name:
    description:
    - The IAM group name to retrieve.
    - If omitted, all groups in the namespace are listed.
    type: str
    required: false

notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: List all IAM groups in namespace
  dellemc.objectscale.iam_group_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "testnamespace"
  register: group_info_result

- name: Get a specific IAM group
  dellemc.objectscale.iam_group_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "testnamespace"
    group_name: "developers"
  register: group_info_result
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed. Always false for info modules.
    returned: always
    type: bool
    sample: false

iam_groups:
    description: List of IAM groups in the namespace.
    returned: always
    type: list
    elements: dict
    contains:
        GroupName:
            description: The name of the IAM group.
            type: str
        GroupId:
            description: The unique identifier for the IAM group.
            type: str
        Arn:
            description: The Amazon Resource Name (ARN) of the group.
            type: str
        Path:
            description: The IAM path prefix for the group.
            type: str
        CreateDate:
            description: The date and time when the group was created.
            type: str
'''

from typing import Any, Dict, List
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi
except (ImportError, Exception):
    IamApi = None  # type: ignore[assignment,misc]


class IamGroupInfo(object):
    """Class for gathering IAM group information from ObjectScale."""

    def __init__(self) -> None:
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(dict(
            namespace=dict(type='str', required=True),
            group_name=dict(type='str', required=False),
        ))

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.fail_json(
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )
            return

        if IamApi is None:
            self.module.fail_json(msg="IamApi is not available.")
            return

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.iam_api = IamApi(self.api_client)
        except Exception as e:
            self.module.fail_json(msg="Failed to connect to ObjectScale: %s" % str(e))
            return

    def list_groups(self, namespace: str) -> List[Dict[str, Any]]:
        """List all IAM groups in a namespace."""
        try:
            return self.iam_api.list_groups(namespace)
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(msg="Getting IAM group list failed with error: %s" % error_msg)
            return []

    def get_group(self, group_name: str, namespace: str) -> List[Dict[str, Any]]:
        """Get a specific IAM group from a namespace."""
        try:
            group = self.iam_api.get_group(group_name, namespace)
            return [group] if group else []
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(
                msg="Getting IAM group %s failed with error: %s" % (group_name, error_msg)
            )
            return []

    def perform_module_operation(self) -> None:
        """Gather IAM group information and return results."""
        namespace = self.module.params['namespace']
        group_name = self.module.params.get('group_name')

        if group_name:
            iam_groups = self.get_group(group_name, namespace)
        else:
            iam_groups = self.list_groups(namespace)

        self.module.exit_json(changed=False, iam_groups=iam_groups)


def main() -> None:
    """Create IamGroupInfo object and perform module operation."""
    obj = IamGroupInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
