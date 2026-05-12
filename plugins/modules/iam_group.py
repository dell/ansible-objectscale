#!/usr/bin/python
# Copyright: (c) 2025, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM groups on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_group

version_added: '1.0.0'

short_description: Manage IAM groups on Dell ObjectScale

description:
- Manages IAM groups on the Dell ObjectScale storage system.
  This includes creating, modifying, deleting and retrieving details of an IAM group.
- Supports managing group membership (users), attached managed policies, and inline policies.
- All operations are scoped to a specific ObjectScale namespace.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: Supports check mode. No changes will be made when check mode is enabled.
  diff_mode:
    support: full
    description: Supports diff mode. Shows before and after state of the IAM group.

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

  validate_certs:
    description:
    - Boolean value to enable or disable SSL certificate verification.
    - Set to C(false) when certificates are not trusted.
    type: bool
    default: true
    required: false

  timeout:
    description:
    - Timeout in seconds for HTTP requests to the ObjectScale management endpoint.
    type: int
    default: 30
    required: false

  group_name:
    description:
    - The name of the IAM group.
    type: str
    required: true

  namespace:
    description:
    - The ObjectScale namespace in which the group resides.
    - Maps to the C(X-Emc-Namespace) header in IAM API requests.
    type: str
    required: true

  path:
    description:
    - The IAM path prefix for the group.
    - Only used during group creation.
    type: str
    default: '/'

  users:
    description:
    - List of IAM user names to manage in the group.
    - Behavior is controlled by I(user_state).
    type: list
    elements: str

  user_state:
    description:
    - Determines how the I(users) list is applied.
    - C(present-in-group) ensures the specified users are members of the group.
    - C(absent-in-group) ensures the specified users are removed from the group.
    type: str
    default: 'present-in-group'
    choices: ['present-in-group', 'absent-in-group']

  policies:
    description:
    - List of managed policy ARNs to manage on the group.
    - Behavior is controlled by I(policy_state).
    type: list
    elements: str

  policy_state:
    description:
    - Determines how the I(policies) list is applied.
    - C(present-in-group) ensures the specified policies are attached to the group.
    - C(absent-in-group) ensures the specified policies are detached from the group.
    type: str
    default: 'present-in-group'
    choices: ['present-in-group', 'absent-in-group']

  inline_policies:
    description:
    - List of inline policies to manage on the group.
    - Each item is a dictionary with C(name) and C(document) keys.
    type: list
    elements: dict

  inline_policy_state:
    description:
    - Determines how the I(inline_policies) list is applied.
    - C(present-in-group) ensures the specified inline policies exist on the group.
    - C(absent-in-group) ensures the specified inline policies are removed from the group.
    type: str
    default: 'present-in-group'
    choices: ['present-in-group', 'absent-in-group']

  state:
    description:
    - The desired state of the IAM group.
    - C(present) ensures the group exists with the specified configuration.
    - C(absent) ensures the group does not exist. All users, managed policies,
      and inline policies are removed before the group is deleted.
    choices: ['present', 'absent']
    type: str
    required: true

notes:
- The I(check_mode) is supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Create an IAM group
  dellemc.objectscale.iam_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    group_name: "developers"
    namespace: "my-namespace"
    state: "present"

- name: Add users to an IAM group
  dellemc.objectscale.iam_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    group_name: "developers"
    namespace: "my-namespace"
    users:
      - "alice"
      - "bob"
    user_state: "present-in-group"
    state: "present"

- name: Attach managed policies to an IAM group
  dellemc.objectscale.iam_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    group_name: "developers"
    namespace: "my-namespace"
    policies:
      - "urn:ecs:iam:::policy/ReadOnlyAccess"
    policy_state: "present-in-group"
    state: "present"

- name: Add an inline policy to an IAM group
  dellemc.objectscale.iam_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    group_name: "developers"
    namespace: "my-namespace"
    inline_policies:
      - name: "AllowS3List"
        document: '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:ListBucket","Resource":"*"}]}'
    inline_policy_state: "present-in-group"
    state: "present"

- name: Remove users from an IAM group
  dellemc.objectscale.iam_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    group_name: "developers"
    namespace: "my-namespace"
    users:
      - "bob"
    user_state: "absent-in-group"
    state: "present"

- name: Check mode - preview group creation
  dellemc.objectscale.iam_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    group_name: "preview-group"
    namespace: "my-namespace"
    state: "present"
  check_mode: true

- name: Delete an IAM group
  dellemc.objectscale.iam_group:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    group_name: "developers"
    namespace: "my-namespace"
    state: "absent"
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: false

iam_group_details:
    description: IAM group details.
    returned: When state is C(present) and the group exists
    type: dict
    contains:
        group_name:
            description: The name of the IAM group.
            type: str
        group_id:
            description: The unique identifier for the IAM group.
            type: str
        arn:
            description: The Amazon Resource Name (ARN) of the group.
            type: str
        path:
            description: The IAM path prefix for the group.
            type: str
        create_date:
            description: The date and time when the group was created.
            type: str
        users:
            description: List of user names that are members of the group.
            type: list
            elements: str
        attached_policies:
            description: List of managed policies attached to the group.
            type: list
            elements: dict
        inline_policies:
            description: List of inline policy names on the group.
            type: list
            elements: str
    sample:
        {
            "group_name": "developers",
            "group_id": "AGPA1234567890EXAMPLE",
            "arn": "urn:ecs:iam::my-namespace:group/developers",
            "path": "/",
            "create_date": "2025-01-15T12:00:00Z",
            "users": ["alice", "bob"],
            "attached_policies": [
                {"policy_arn": "urn:ecs:iam:::policy/ReadOnlyAccess", "policy_name": "ReadOnlyAccess"}
            ],
            "inline_policies": ["AllowS3List"]
        }

diff:
    description: Diff of the IAM group before and after changes.
    returned: When diff mode is enabled
    type: dict
'''

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi as IamApiType

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi
except Exception:
    IamApi = None  # type: ignore[assignment,misc]


class IamGroup(object):
    """Class with operations on ObjectScale IAM Groups"""

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_group_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True
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
    # Read operations
    # ------------------------------------------------------------------

    def get_group_details(self, group_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get full group details including users and policies.

        Returns a normalized dict or None if the group does not exist.
        IamApi.get_group returns: {GroupName, GroupId, Arn, Path, CreateDate, Users: [{UserName, ...}]}
        IamApi.list_attached_group_policies returns: [{PolicyName, PolicyArn}]
        IamApi.list_group_policies returns: [str]
        """
        try:
            group_response = self.iam_api.get_group(group_name, namespace)
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404',):
                return None
            error_msg = utils.determine_error(e)
            msg = "Getting group %s details failed with error: %s" % (group_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

        if group_response is None:
            return None

        # Extract user names from Users list
        raw_users = group_response.get('Users', [])
        user_names = [u.get('UserName', '') for u in raw_users if isinstance(u, dict)]

        # Get attached managed policies
        attached_policies = []  # type: List[Dict[str, Any]]
        try:
            attached_policies = self.iam_api.list_attached_group_policies(group_name, namespace)
        except Exception as e:
            self.module.warn("Could not list attached policies for group %s: %s" % (group_name, str(e)))

        # Get inline policy names
        inline_policies = []  # type: List[str]
        try:
            inline_policies = self.iam_api.list_group_policies(group_name, namespace)
        except Exception as e:
            self.module.warn("Could not list inline policies for group %s: %s" % (group_name, str(e)))

        return {
            'group_name': group_response.get('GroupName', group_name),
            'group_id': group_response.get('GroupId', ''),
            'arn': group_response.get('Arn', ''),
            'path': group_response.get('Path', '/'),
            'create_date': group_response.get('CreateDate', ''),
            'users': user_names,
            'attached_policies': attached_policies,
            'inline_policies': inline_policies,
        }

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_group(self, group_name: str, namespace: str) -> Optional[bool]:
        """Create a new IAM group."""
        path = self.module.params.get('path', '/')
        try:
            if not self.module.check_mode:
                self.iam_api.create_group(group_name, namespace, path=path)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating group %s failed with error: %s" % (group_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

    def _cleanup_group_users(self, group_name: str, namespace: str, current_state: Dict[str, Any]) -> None:
        """Remove all users from group before deletion."""
        for user_name in current_state.get('users', []):
            try:
                if not self.module.check_mode:
                    self.iam_api.remove_user_from_group(group_name, user_name, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Removing user %s from group %s failed with error: %s" % (user_name, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def _cleanup_group_policies(self, group_name: str, namespace: str, current_state: Dict[str, Any]) -> None:
        """Detach all managed policies from group before deletion."""
        for policy in current_state.get('attached_policies', []):
            policy_arn = policy.get('PolicyArn', '') if isinstance(policy, dict) else str(policy)
            try:
                if not self.module.check_mode:
                    self.iam_api.detach_group_policy(group_name, policy_arn, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Detaching policy %s from group %s failed with error: %s" % (policy_arn, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def _cleanup_group_inline_policies(self, group_name: str, namespace: str, current_state: Dict[str, Any]) -> None:
        """Delete all inline policies from group before deletion."""
        for policy_name in current_state.get('inline_policies', []):
            try:
                if not self.module.check_mode:
                    self.iam_api.delete_group_policy(group_name, policy_name, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Deleting inline policy %s from group %s failed with error: %s" % (policy_name, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def delete_group(self, group_name: str, namespace: str, current_state: Dict[str, Any]) -> Optional[bool]:
        """Delete group after cleaning up all dependencies."""
        self._cleanup_group_users(group_name, namespace, current_state)
        self._cleanup_group_policies(group_name, namespace, current_state)
        self._cleanup_group_inline_policies(group_name, namespace, current_state)
        try:
            if not self.module.check_mode:
                self.iam_api.delete_group(group_name, namespace)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Deleting group %s failed with error: %s" % (group_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

    def add_users(self, group_name: str, namespace: str, users: List[str]) -> None:
        """Add users to group."""
        for user_name in users:
            try:
                if not self.module.check_mode:
                    self.iam_api.add_user_to_group(group_name, user_name, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Adding user %s to group %s failed with error: %s" % (user_name, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def remove_users(self, group_name: str, namespace: str, users: List[str]) -> None:
        """Remove users from group."""
        for user_name in users:
            try:
                if not self.module.check_mode:
                    self.iam_api.remove_user_from_group(group_name, user_name, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Removing user %s from group %s failed with error: %s" % (user_name, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def attach_policies(self, group_name: str, namespace: str, policy_arns: List[str]) -> None:
        """Attach managed policies to group."""
        for policy_arn in policy_arns:
            try:
                if not self.module.check_mode:
                    self.iam_api.attach_group_policy(group_name, policy_arn, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Attaching policy %s to group %s failed with error: %s" % (policy_arn, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def detach_policies(self, group_name: str, namespace: str, policy_arns: List[str]) -> None:
        """Detach managed policies from group."""
        for policy_arn in policy_arns:
            try:
                if not self.module.check_mode:
                    self.iam_api.detach_group_policy(group_name, policy_arn, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Detaching policy %s from group %s failed with error: %s" % (policy_arn, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def put_inline_policies(self, group_name: str, namespace: str, policies: List[Dict[str, str]]) -> None:
        """Add or update inline policies on the group."""
        for policy in policies:
            policy_name = policy.get('name', '')
            policy_document = policy.get('document', '')
            try:
                if not self.module.check_mode:
                    self.iam_api.put_group_policy(group_name, policy_name, policy_document, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Putting inline policy %s on group %s failed with error: %s" % (
                    policy_name, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    def delete_inline_policies(self, group_name: str, namespace: str, policy_names: List[str]) -> None:
        """Delete inline policies from the group."""
        for policy_name in policy_names:
            try:
                if not self.module.check_mode:
                    self.iam_api.delete_group_policy(group_name, policy_name, namespace)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Deleting inline policy %s from group %s failed with error: %s" % (
                    policy_name, group_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    # ------------------------------------------------------------------
    # Idempotency
    # ------------------------------------------------------------------

    def _compute_user_modifications(self, params, current_users, modifications):
        """Compute user add/remove modifications."""
        desired_users = params.get('users')
        user_state = params.get('user_state', 'present-in-group')
        if desired_users is None:
            return
        desired_set = set(desired_users)
        if user_state == 'present-in-group':
            to_add = list(desired_set - current_users)
            if to_add:
                modifications['users_to_add'] = to_add
        elif user_state == 'absent-in-group':
            to_remove = list(desired_set & current_users)
            if to_remove:
                modifications['users_to_remove'] = to_remove

    def _compute_policy_modifications(self, params, current_policy_arns, modifications):
        """Compute managed policy attach/detach modifications."""
        desired_policies = params.get('policies')
        policy_state = params.get('policy_state', 'present-in-group')
        if desired_policies is None:
            return
        desired_policy_set = set(desired_policies)
        if policy_state == 'present-in-group':
            to_attach = list(desired_policy_set - current_policy_arns)
            if to_attach:
                modifications['policies_to_attach'] = to_attach
        elif policy_state == 'absent-in-group':
            to_detach = list(desired_policy_set & current_policy_arns)
            if to_detach:
                modifications['policies_to_detach'] = to_detach

    def _compute_inline_modifications(self, params, current_inline_names, modifications):
        """Compute inline policy put/delete modifications."""
        desired_inline = params.get('inline_policies')
        inline_state = params.get('inline_policy_state', 'present-in-group')
        if desired_inline is None:
            return
        if inline_state == 'present-in-group':
            to_put = [p for p in desired_inline if isinstance(p, dict) and p.get('name')]
            if to_put:
                modifications['inline_to_put'] = to_put
        elif inline_state == 'absent-in-group':
            desired_names = set(
                p.get('name', '') for p in desired_inline if isinstance(p, dict) and p.get('name')
            )
            to_delete = list(desired_names & current_inline_names)
            if to_delete:
                modifications['inline_to_delete'] = to_delete

    def is_group_modified(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what modifications are needed by comparing desired vs current state."""
        params = self.module.params
        modifications = {
            'users_to_add': [],
            'users_to_remove': [],
            'policies_to_attach': [],
            'policies_to_detach': [],
            'inline_to_put': [],
            'inline_to_delete': [],
            'is_modified': False,
        }  # type: Dict[str, Any]

        current_users = set(current_state.get('users', []))
        current_policy_arns = set(
            p.get('PolicyArn', '') if isinstance(p, dict) else str(p)
            for p in current_state.get('attached_policies', [])
        )
        current_inline_names = set(current_state.get('inline_policies', []))

        self._compute_user_modifications(params, current_users, modifications)
        self._compute_policy_modifications(params, current_policy_arns, modifications)
        self._compute_inline_modifications(params, current_inline_names, modifications)

        modifications['is_modified'] = bool(
            modifications['users_to_add'] or modifications['users_to_remove']
            or modifications['policies_to_attach'] or modifications['policies_to_detach']
            or modifications['inline_to_put'] or modifications['inline_to_delete']
        )
        return modifications

    # ------------------------------------------------------------------
    # Diff helpers
    # ------------------------------------------------------------------

    def _build_state_snapshot(self, group_details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a serializable state snapshot for diff output."""
        if not group_details:
            return {}
        return {
            'group_name': group_details.get('group_name', ''),
            'users': sorted(group_details.get('users', [])),
            'attached_policies': sorted(
                (p.get('PolicyArn', '') if isinstance(p, dict) else str(p))
                for p in group_details.get('attached_policies', [])
            ),
            'inline_policies': sorted(group_details.get('inline_policies', [])),
        }

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def _handle_create_group(self, group_name, namespace):
        """Create group and apply initial sub-resources."""
        self.create_group(group_name, namespace)
        params = self.module.params

        desired_users = params.get('users')
        if desired_users and params.get('user_state') == 'present-in-group':
            self.add_users(group_name, namespace, desired_users)

        desired_policies = params.get('policies')
        if desired_policies and params.get('policy_state') == 'present-in-group':
            self.attach_policies(group_name, namespace, desired_policies)

        desired_inline = params.get('inline_policies')
        if desired_inline and params.get('inline_policy_state') == 'present-in-group':
            self.put_inline_policies(group_name, namespace, desired_inline)

    def _apply_modifications(self, group_name, namespace, modifications):
        """Apply computed modifications to the group."""
        if modifications['users_to_add']:
            self.add_users(group_name, namespace, modifications['users_to_add'])
        if modifications['users_to_remove']:
            self.remove_users(group_name, namespace, modifications['users_to_remove'])
        if modifications['policies_to_attach']:
            self.attach_policies(group_name, namespace, modifications['policies_to_attach'])
        if modifications['policies_to_detach']:
            self.detach_policies(group_name, namespace, modifications['policies_to_detach'])
        if modifications['inline_to_put']:
            self.put_inline_policies(group_name, namespace, modifications['inline_to_put'])
        if modifications['inline_to_delete']:
            self.delete_inline_policies(group_name, namespace, modifications['inline_to_delete'])

    def _handle_group_absent(self, group_name, namespace, group_details, before_state, result):
        """Handle state=absent for an IAM group."""
        if group_details:
            self.delete_group(group_name, namespace, group_details)
            result['changed'] = True
        if self.module._diff:
            result['diff'] = dict(before=before_state, after={})

    def _handle_group_present(self, group_name, namespace, group_details, before_state, result):
        """Handle state=present for an IAM group."""
        if not group_details:
            self._handle_create_group(group_name, namespace)
            result['changed'] = True
            if not self.module.check_mode:
                group_details = self.get_group_details(group_name, namespace)
        else:
            modifications = self.is_group_modified(group_details)
            if modifications['is_modified']:
                self._apply_modifications(group_name, namespace, modifications)
                result['changed'] = True
                if not self.module.check_mode:
                    group_details = self.get_group_details(group_name, namespace)

        if self.module._diff:
            after_state = self._build_state_snapshot(group_details)
            result['diff'] = dict(before=before_state, after=after_state)

        result['iam_group_details'] = group_details

    def perform_module_operation(self) -> None:
        """Perform different actions based on parameters chosen in playbook."""
        result = dict(changed=False, iam_group_details=None)  # type: Dict[str, Any]

        group_name = self.module.params['group_name']
        namespace = self.module.params['namespace']
        state = self.module.params['state']

        group_details = self.get_group_details(group_name, namespace)
        before_state = self._build_state_snapshot(group_details)

        if state == 'absent':
            self._handle_group_absent(group_name, namespace, group_details, before_state, result)
        else:
            self._handle_group_present(group_name, namespace, group_details, before_state, result)

        self.module.exit_json(**result)

    @staticmethod
    def get_iam_group_parameters() -> Dict[str, Dict[str, Any]]:
        """Module-specific parameters for IAM group management."""
        return dict(
            group_name=dict(type='str', required=True),
            namespace=dict(type='str', required=True),
            path=dict(type='str', default='/'),
            users=dict(type='list', elements='str', default=None),
            user_state=dict(
                type='str', default='present-in-group',
                choices=['present-in-group', 'absent-in-group'],
            ),
            policies=dict(type='list', elements='str', default=None),
            policy_state=dict(
                type='str', default='present-in-group',
                choices=['present-in-group', 'absent-in-group'],
            ),
            inline_policies=dict(type='list', elements='dict', default=None),
            inline_policy_state=dict(
                type='str', default='present-in-group',
                choices=['present-in-group', 'absent-in-group'],
            ),
            state=dict(required=True, type='str', choices=['present', 'absent']),
        )


def main() -> None:
    """Create ObjectScale IAM Group object and perform actions on it."""
    obj = IamGroup()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
