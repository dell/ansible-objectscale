#!/usr/bin/python
# Copyright: (c) 2025, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM policy attachments on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_policy_attachment

version_added: '1.0.0'

short_description: Manage IAM policy attachments on Dell ObjectScale

description:
- Attaches or detaches managed IAM policies to/from a target principal
  (user, group, or role) in Dell ObjectScale.
- Supports diff-based idempotency.
- When I(state=absent), all currently attached policies are detached.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: Supports check mode. No changes will be made when check mode is enabled.
  diff_mode:
    support: full
    description: Supports diff mode. Shows before and after attached policy ARNs.

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
    no_log: true

  validate_certs:
    description:
    - Boolean value to enable or disable SSL certificate verification.
    type: bool
    default: true
    required: false

  timeout:
    description:
    - Timeout in seconds for HTTP requests to the ObjectScale management endpoint.
    type: int
    default: 30
    required: false

  namespace:
    description:
    - The ObjectScale namespace in which the IAM entity resides.
    type: str
    required: true

  user_name:
    description:
    - Name of the IAM user. Exactly one of I(user_name), I(group_name),
      or I(role_name) must be specified.
    type: str

  group_name:
    description:
    - Name of the IAM group. Exactly one of I(user_name), I(group_name),
      or I(role_name) must be specified.
    type: str

  role_name:
    description:
    - Name of the IAM role. Exactly one of I(user_name), I(group_name),
      or I(role_name) must be specified.
    type: str

  policy_arns:
    description:
    - List of managed policy ARNs to associate with the entity.
    - Required when I(state=present).
    type: list
    elements: str

  state:
    description:
    - Desired state of the policy attachment.
    - C(present) ensures the specified policies are attached (diff-based).
    - C(absent) detaches all currently attached policies.
    choices: ['present', 'absent']
    type: str
    default: present

notes:
- The I(check_mode) is supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Attach policies to an IAM user
  dellemc.objectscale.iam_policy_attachment:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "userTest1"
    policy_arns:
      - "urn:ecs:iam:::policy/ECSS3ReadOnlyAccess"
      - "urn:ecs:iam:::policy/IAMReadOnlyAccess"
    state: present

- name: Attach policies to a group
  dellemc.objectscale.iam_policy_attachment:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    group_name: "developers"
    policy_arns:
      - "urn:ecs:iam:::policy/ECSS3FullAccess"
    state: present

- name: Attach policy to a role
  dellemc.objectscale.iam_policy_attachment:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    role_name: "admin-role"
    policy_arns:
      - "urn:ecs:iam:::policy/IAMFullAccess"
    state: present

- name: Detach all policies from a user
  dellemc.objectscale.iam_policy_attachment:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "userTest1"
    state: absent

- name: Check mode - preview policy attachment
  dellemc.objectscale.iam_policy_attachment:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "userTest1"
    policy_arns:
      - "urn:ecs:iam:::policy/ECSS3ReadOnlyAccess"
    state: present
  check_mode: true
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: true

policy_attachment_details:
    description: Details of the policy attachment state after the operation.
    returned: always
    type: dict
    contains:
        namespace:
            description: The ObjectScale namespace.
            type: str
        entity_type:
            description: The type of IAM entity (user, group, or role).
            type: str
        entity_name:
            description: The name of the IAM entity.
            type: str
        attached_policy_arns:
            description: List of policy ARNs currently attached to the entity.
            type: list
            elements: str
    sample:
        {
            "namespace": "ns1",
            "entity_type": "user",
            "entity_name": "userTest1",
            "attached_policy_arns": [
                "urn:ecs:iam:::policy/ECSS3ReadOnlyAccess",
                "urn:ecs:iam:::policy/IAMReadOnlyAccess"
            ]
        }

id:
    description: Resource identifier in format namespace:entity_type:entity_name.
    returned: always
    type: str
    sample: "ns1:user:userTest1"

diff:
    description: Diff of the attached policies before and after changes.
    returned: When diff mode is enabled
    type: dict
'''

from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi as IamApiType

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi
except (ImportError, Exception):
    IamApi = None  # type: ignore[assignment,misc]


class IamPolicyAttachment(object):
    """Class with operations on ObjectScale IAM Policy Attachments"""

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_policy_attachment_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
            mutually_exclusive=[['user_name', 'group_name', 'role_name']],
            required_one_of=[['user_name', 'group_name', 'role_name']],
            required_if=[('state', 'present', ['policy_arns'])],
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )
            return

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.iam_api: IamApiType = IamApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

        self.module.log('Connected to ObjectScale at %s' % self.module.params['objectscale_host'])

    # ------------------------------------------------------------------
    # Entity determination
    # ------------------------------------------------------------------

    def determine_entity(self) -> Tuple[str, str]:
        """Determine the entity type and name from module params."""
        params = self.module.params
        if params.get('user_name'):
            return 'user', params['user_name']
        elif params.get('group_name'):
            return 'group', params['group_name']
        elif params.get('role_name'):
            return 'role', params['role_name']
        # Should never reach here due to required_one_of validation
        self.module.exit_json(failed=True, msg="One of user_name, group_name, or role_name is required.")
        return '', ''

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_attached_policies(self, entity_type: str, entity_name: str, namespace: str) -> List[Dict[str, Any]]:
        """Get list of attached policies for the given entity.

        Returns raw list of dicts with PolicyName/PolicyArn keys as returned
        by the IamApi list_attached_*_policies methods.
        """
        self.module.log('Listing attached policies for %s %s in namespace %s' % (
            entity_type, entity_name, namespace))
        try:
            if entity_type == 'user':
                return self.iam_api.list_attached_user_policies(entity_name, namespace)
            elif entity_type == 'group':
                return self.iam_api.list_attached_group_policies(entity_name, namespace)
            elif entity_type == 'role':
                return self.iam_api.list_attached_role_policies(entity_name, namespace)
            else:
                self.module.exit_json(failed=True, msg="Unknown entity type: %s" % entity_type)
                return []
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Listing attached policies for %s '%s' in namespace '%s' failed with error: %s" % (
                entity_type, entity_name, namespace, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return []

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def attach_policies(self, entity_type: str, entity_name: str, namespace: str,
                        policy_arns: Set[str]) -> None:
        """Attach policies to the entity."""
        for arn in sorted(policy_arns):
            self.module.log('Attaching policy %s to %s %s' % (arn, entity_type, entity_name))
            try:
                if not self.module.check_mode:
                    if entity_type == 'user':
                        self.iam_api.attach_user_policy(entity_name, arn, namespace)
                    elif entity_type == 'group':
                        self.iam_api.attach_group_policy(entity_name, arn, namespace)
                    elif entity_type == 'role':
                        self.iam_api.attach_role_policy(entity_name, arn, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Attaching policy '%s' to %s '%s' failed with error: %s" % (
                    arn, entity_type, entity_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def detach_policies(self, entity_type: str, entity_name: str, namespace: str,
                        policy_arns: Set[str]) -> None:
        """Detach policies from the entity."""
        for arn in sorted(policy_arns):
            self.module.log('Detaching policy %s from %s %s' % (arn, entity_type, entity_name))
            try:
                if not self.module.check_mode:
                    if entity_type == 'user':
                        self.iam_api.detach_user_policy(entity_name, arn, namespace)
                    elif entity_type == 'group':
                        self.iam_api.detach_group_policy(entity_name, arn, namespace)
                    elif entity_type == 'role':
                        self.iam_api.detach_role_policy(entity_name, arn, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Detaching policy '%s' from %s '%s' failed with error: %s" % (
                    arn, entity_type, entity_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    # ------------------------------------------------------------------
    # Diff computation
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_arns(attached_policies: List[Dict[str, Any]]) -> Set[str]:
        """Extract ARN strings from list of attached policy dicts."""
        return set(
            p.get('PolicyArn', '') if isinstance(p, dict) else str(p)
            for p in attached_policies
        )

    def compute_changes(self, desired_arns: Set[str], current_arns: Set[str],
                        state: str) -> Tuple[Set[str], Set[str], bool]:
        """Compute the attach/detach delta."""
        if state == 'absent':
            to_attach = set()  # type: Set[str]
            to_detach = current_arns.copy()
            return to_attach, to_detach, bool(to_detach)
        # state == 'present'
        to_attach = desired_arns - current_arns
        to_detach = current_arns - desired_arns
        is_changed = bool(to_attach or to_detach)
        return to_attach, to_detach, is_changed

    def _build_state_snapshot(self, attached_arns: List[str]) -> Dict[str, Any]:
        """Build a serializable state snapshot for diff output."""
        return {
            'attached_policy_arns': sorted(attached_arns),
        }

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def perform_module_operation(self) -> None:
        """Perform different actions based on parameters chosen in playbook."""
        entity_type, entity_name = self.determine_entity()
        namespace = self.module.params['namespace']
        state = self.module.params['state']
        desired_policy_arns = self.module.params.get('policy_arns') or []

        # Read current state
        current_policies = self.get_attached_policies(entity_type, entity_name, namespace)
        current_arns = self._extract_arns(current_policies)
        desired_arns = set(desired_policy_arns)

        before_arns = sorted(current_arns)

        # Compute delta
        to_attach, to_detach, is_changed = self.compute_changes(desired_arns, current_arns, state)

        result = dict(
            changed=is_changed,
            policy_attachment_details=None,
            id='%s:%s:%s' % (namespace, entity_type, entity_name),
        )  # type: Dict[str, Any]

        if is_changed:
            # Apply changes (skipped in check mode)
            if to_detach:
                self.detach_policies(entity_type, entity_name, namespace, to_detach)
            if to_attach:
                self.attach_policies(entity_type, entity_name, namespace, to_attach)

            # Re-read state after changes (unless check mode)
            if not self.module.check_mode:
                current_policies = self.get_attached_policies(entity_type, entity_name, namespace)
                current_arns = self._extract_arns(current_policies)

        after_arns = sorted(current_arns) if not self.module.check_mode else sorted(
            (current_arns - to_detach) | to_attach
        )

        result['policy_attachment_details'] = {
            'namespace': namespace,
            'entity_type': entity_type,
            'entity_name': entity_name,
            'attached_policy_arns': after_arns,
        }

        if self.module._diff:
            result['diff'] = dict(
                before=self._build_state_snapshot(before_arns),
                after=self._build_state_snapshot(after_arns),
            )

        self.module.log('Policy attachment operation complete: changed=%s' % result['changed'])
        self.module.exit_json(**result)

    @staticmethod
    def get_iam_policy_attachment_parameters() -> Dict[str, Dict[str, Any]]:
        """Module-specific parameters for IAM policy attachment management."""
        return dict(
            namespace=dict(type='str', required=True),
            user_name=dict(type='str', default=None),
            group_name=dict(type='str', default=None),
            role_name=dict(type='str', default=None),
            policy_arns=dict(type='list', elements='str', default=None),
            state=dict(type='str', default='present', choices=['present', 'absent']),
        )


def main() -> None:
    """Create ObjectScale IAM Policy Attachment object and perform actions on it."""
    obj = IamPolicyAttachment()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
