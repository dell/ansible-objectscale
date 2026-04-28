#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering IAM inline policy information from Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_inline_policy_info

version_added: '1.0.0'

short_description: Gather IAM inline policy information from Dell ObjectScale

description:
- Gather information about inline IAM policies on a user, group, or role
  in Dell ObjectScale.
- Returns the list of inline policy names and their documents for the specified entity.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

extends_documentation_fragment:
- dellemc.objectscale.objectscale

options:
  namespace:
    description:
    - The ObjectScale namespace in which the IAM entity resides.
    type: str
    required: true

  user_name:
    description:
    - The IAM user name whose inline policies to list.
    - Exactly one of I(user_name), I(group_name), or I(role_name) must be specified.
    type: str
    required: false

  group_name:
    description:
    - The IAM group name whose inline policies to list.
    - Exactly one of I(user_name), I(group_name), or I(role_name) must be specified.
    type: str
    required: false

  role_name:
    description:
    - The IAM role name whose inline policies to list.
    - Exactly one of I(user_name), I(group_name), or I(role_name) must be specified.
    type: str
    required: false

notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Get inline policies for an IAM user
  dellemc.objectscale.iam_inline_policy_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "userTest1"
  register: user_inline_policies

- name: Get inline policies for an IAM group
  dellemc.objectscale.iam_inline_policy_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    group_name: "developers"
  register: group_inline_policies

- name: Get inline policies for an IAM role
  dellemc.objectscale.iam_inline_policy_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    role_name: "admin-role"
  register: role_inline_policies
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed. Always false for info modules.
    returned: always
    type: bool
    sample: false

inline_policies:
    description: List of inline policies for the specified entity.
    returned: always
    type: list
    elements: dict
    contains:
        name:
            description: The name of the inline policy.
            type: str
        document:
            description: The JSON policy document.
            type: str
    sample:
        [
            {
                "name": "readOnlyPolicy",
                "document": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"iam:Get*\",\"iam:List*\"],\"Resource\":\"*\"}]}"
            }
        ]

entity_type:
    description: The type of IAM entity queried (user, group, or role).
    returned: always
    type: str
    sample: "user"

entity_name:
    description: The name of the IAM entity queried.
    returned: always
    type: str
    sample: "userTest1"

namespace:
    description: The ObjectScale namespace queried.
    returned: always
    type: str
    sample: "ns1"
'''

from urllib.parse import unquote
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi
except (ImportError, Exception):
    IamApi = None  # type: ignore[assignment,misc]


class IamInlinePolicyInfo(object):
    """Class for gathering IAM inline policy information from ObjectScale."""

    def __init__(self):
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_inline_policy_info_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            mutually_exclusive=[
                ['user_name', 'group_name', 'role_name'],
            ],
            required_one_of=[
                ['user_name', 'group_name', 'role_name'],
            ],
            supports_check_mode=True
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.fail_json(
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )
            return

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.iam_api = IamApi(self.api_client)
        except Exception as e:
            self.module.fail_json(
                msg="Failed to connect to ObjectScale: %s" % str(e)
            )
            return

    @staticmethod
    def get_iam_inline_policy_info_parameters():
        """Return dict of module-specific parameters."""
        return dict(
            namespace=dict(type='str', required=True),
            user_name=dict(type='str', required=False, default=None),
            group_name=dict(type='str', required=False, default=None),
            role_name=dict(type='str', required=False, default=None),
        )

    def determine_entity(self):
        """Determine the entity type and name from module params.

        Returns a tuple of (entity_type, entity_name).
        """
        params = self.module.params
        if params.get('user_name'):
            return 'user', params['user_name']
        elif params.get('group_name'):
            return 'group', params['group_name']
        elif params.get('role_name'):
            return 'role', params['role_name']
        self.module.fail_json(
            msg="One of user_name, group_name, or role_name is required."
        )
        return '', ''

    def get_inline_policies(self, entity_type, entity_name, namespace):
        """Get all inline policies for the given entity.

        Lists policy names then fetches each document. Returns list of
        dicts with 'name' and 'document' keys.
        """
        try:
            if entity_type == 'user':
                policy_names = self.iam_api.list_user_policies(entity_name, namespace)
            elif entity_type == 'group':
                policy_names = self.iam_api.list_group_policies(entity_name, namespace)
            elif entity_type == 'role':
                policy_names = self.iam_api.list_role_policies(entity_name, namespace)
            else:
                self.module.fail_json(msg="Unknown entity type: %s" % entity_type)
                return []
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(
                msg="Listing inline policies for %s '%s' in namespace '%s' "
                    "failed with error: %s" % (entity_type, entity_name, namespace, error_msg)
            )
            return []

        policies = []
        for pname in (policy_names or []):
            try:
                if entity_type == 'user':
                    result = self.iam_api.get_user_policy(entity_name, pname, namespace)
                elif entity_type == 'group':
                    result = self.iam_api.get_group_policy(entity_name, pname, namespace)
                elif entity_type == 'role':
                    result = self.iam_api.get_role_policy(entity_name, pname, namespace)
                else:
                    result = None

                if result is not None:
                    doc = result.get('PolicyDocument', '') or ''
                    if '%7B' in doc or '%22' in doc:
                        doc = unquote(doc)
                    policies.append({'name': pname, 'document': doc})
            except Exception as e:
                error_msg = utils.determine_error(e)
                self.module.fail_json(
                    msg="Getting inline policy '%s' for %s '%s' failed with error: %s" % (
                        pname, entity_type, entity_name, error_msg)
                )
                return []

        return policies

    def perform_module_operation(self):
        """Perform the main module operation.

        Determines entity type, lists inline policies with their documents,
        and returns results. Always returns changed=False (read-only info module).
        """
        entity_type, entity_name = self.determine_entity()
        namespace = self.module.params['namespace']

        inline_policies = self.get_inline_policies(entity_type, entity_name, namespace)

        self.module.exit_json(
            changed=False,
            inline_policies=inline_policies or [],
            entity_type=entity_type,
            entity_name=entity_name,
            namespace=namespace,
        )


def main():
    """Create IamInlinePolicyInfo object and perform module operation."""
    obj = IamInlinePolicyInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
