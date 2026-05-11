#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering IAM policy attachment information from Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_policy_attachment_info

version_added: '1.0.0'

short_description: Gather IAM policy attachment information from Dell ObjectScale

description:
- Gather information about managed IAM policies attached to a user, group, or role
  on Dell ObjectScale.
- Returns the list of attached policy ARNs and names for the specified entity.

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
    - The IAM user name whose attached policies to list.
    - Exactly one of I(user_name), I(group_name), or I(role_name) must be specified.
    type: str
    required: false

  group_name:
    description:
    - The IAM group name whose attached policies to list.
    - Exactly one of I(user_name), I(group_name), or I(role_name) must be specified.
    type: str
    required: false

  role_name:
    description:
    - The IAM role name whose attached policies to list.
    - Exactly one of I(user_name), I(group_name), or I(role_name) must be specified.
    type: str
    required: false

notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: List attached policies for an IAM user
  dellemc.objectscale.iam_policy_attachment_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "testuser"
  register: user_policies

- name: List attached policies for an IAM group
  dellemc.objectscale.iam_policy_attachment_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    group_name: "developers"
  register: group_policies

- name: List attached policies for an IAM role
  dellemc.objectscale.iam_policy_attachment_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    role_name: "admin-role"
  register: role_policies
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed. Always false for info modules.
    returned: always
    type: bool
    sample: false

iam_attached_policies:
    description: List of attached policy dictionaries for the specified entity.
    returned: always
    type: list
    elements: dict
    contains:
        PolicyName:
            description: The friendly name of the attached policy.
            type: str
        PolicyArn:
            description: The Amazon Resource Name (ARN) of the attached policy.
            type: str
    sample:
        [
            {
                "PolicyName": "ECSS3ReadOnlyAccess",
                "PolicyArn": "urn:ecs:iam:::policy/ECSS3ReadOnlyAccess"
            },
            {
                "PolicyName": "IAMReadOnlyAccess",
                "PolicyArn": "urn:ecs:iam:::policy/IAMReadOnlyAccess"
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
    sample: "testuser"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi
except Exception:
    IamApi = None  # type: ignore[assignment,misc]


class IamPolicyAttachmentInfo(object):
    """Class for gathering IAM policy attachment information from ObjectScale."""

    def __init__(self):
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_policy_attachment_info_parameters())

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
    def get_iam_policy_attachment_info_parameters():
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

    def get_attached_policies(self, entity_type, entity_name, namespace):
        """Get list of attached policies for the given entity.

        Returns list of dicts with PolicyName/PolicyArn keys.
        """
        try:
            if entity_type == 'user':
                return self.iam_api.list_attached_user_policies(entity_name, namespace)
            elif entity_type == 'group':
                return self.iam_api.list_attached_group_policies(entity_name, namespace)
            elif entity_type == 'role':
                return self.iam_api.list_attached_role_policies(entity_name, namespace)
            else:
                self.module.fail_json(
                    msg="Unknown entity type: %s" % entity_type
                )
                return []
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(
                msg="Listing attached policies for %s '%s' in namespace '%s' "
                    "failed with error: %s" % (entity_type, entity_name, namespace, error_msg)
            )
            return []

    def perform_module_operation(self):
        """Perform the main module operation.

        Determines entity type, lists attached policies, and returns results.
        Always returns changed=False (read-only info module).
        """
        entity_type, entity_name = self.determine_entity()
        namespace = self.module.params['namespace']

        attached_policies = self.get_attached_policies(
            entity_type, entity_name, namespace
        )

        self.module.exit_json(
            changed=False,
            iam_attached_policies=attached_policies or [],
            entity_type=entity_type,
            entity_name=entity_name,
        )


def main():
    """Create IamPolicyAttachmentInfo object and perform module operation."""
    obj = IamPolicyAttachmentInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
