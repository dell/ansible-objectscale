#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM inline policies on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_inline_policy

version_added: '1.0.0'

short_description: Manage IAM inline policies on Dell ObjectScale

description:
- Manages IAM inline policies for Dell ObjectScale entities (user, group, or role).
- Supports creating, updating, and deleting multiple inline policies on a single entity.
- Uses diff-based idempotency — only changed policies are applied.
- When I(state=absent), all existing inline policies on the entity are deleted.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: Supports check mode. No changes will be made when check mode is enabled.
  diff_mode:
    support: full
    description: Supports diff mode. Shows before and after inline policy state.

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

  policies:
    description:
    - List of inline policies to associate with the entity.
    - Each item must be a dict with C(name) (str) and C(document) (JSON str) keys.
    - Required when I(state=present).
    type: list
    elements: dict

  state:
    description:
    - Desired state of the inline policies.
    - C(present) ensures the specified policies are applied (diff-based).
    - C(absent) deletes all inline policies from the entity.
    choices: ['present', 'absent']
    type: str
    default: present

notes:
- The I(check_mode) is supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Set inline policies on IAM user
  dellemc.objectscale.iam_inline_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "userTest1"
    policies:
      - name: "readOnlyPolicy"
        document: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": ["iam:Get*", "iam:List*"],
                "Resource": "*"
              }
            ]
          }
    state: present

- name: Set inline policies on IAM group
  dellemc.objectscale.iam_inline_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    group_name: "developers"
    policies:
      - name: "s3Access"
        document: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": "*"
              }
            ]
          }
    state: present

- name: Set inline policies on IAM role
  dellemc.objectscale.iam_inline_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    role_name: "admin-role"
    policies:
      - name: "fullAccess"
        document: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
              }
            ]
          }
    state: present

- name: Remove all inline policies from user
  dellemc.objectscale.iam_inline_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "userTest1"
    state: absent

- name: Check mode - preview inline policy changes
  dellemc.objectscale.iam_inline_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "ns1"
    user_name: "userTest1"
    policies:
      - name: "readOnlyPolicy"
        document: '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["iam:Get*"],"Resource":"*"}]}'
    state: present
  check_mode: true
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: true

inline_policy_details:
    description: Details of the inline policy state after the operation.
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
        policies:
            description: List of inline policies on the entity.
            type: list
            elements: dict
    sample:
        {
            "namespace": "ns1",
            "entity_type": "user",
            "entity_name": "userTest1",
            "policies": [
                {
                    "name": "readOnlyPolicy",
                    "document": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"iam:Get*\",\"iam:List*\"],\"Resource\":\"*\"}]}"
                }
            ]
        }

id:
    description: Resource identifier in format namespace:entity_type:entity_name.
    returned: always
    type: str
    sample: "ns1:user:userTest1"

diff:
    description: Diff of the inline policies before and after changes.
    returned: When diff mode is enabled
    type: dict
'''

import json
from urllib.parse import unquote
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


class IamInlinePolicy(object):
    """Class with operations on ObjectScale IAM Inline Policies"""

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_inline_policy_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
            mutually_exclusive=[['user_name', 'group_name', 'role_name']],
            required_one_of=[['user_name', 'group_name', 'role_name']],
            required_if=[('state', 'present', ['policies'])],
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
        self.module.exit_json(failed=True, msg="One of user_name, group_name, or role_name is required.")
        return '', ''

    # ------------------------------------------------------------------
    # JSON normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_document(doc_str: Optional[str]) -> str:
        """Normalize a JSON policy document for reliable comparison.

        Parses JSON, normalizes IAM-specific fields (ObjectScale converts
        single-string Action/Resource values to arrays), then re-serializes
        with sorted keys and compact separators.
        Returns the original string if parsing fails.
        """
        if doc_str is None:
            return ''
        try:
            parsed = json.loads(doc_str)
            # ObjectScale normalizes single-value Action/Resource strings
            # to arrays.  Mirror that so comparisons are stable.
            if isinstance(parsed, dict):
                for stmt in parsed.get('Statement', []):
                    if isinstance(stmt, dict):
                        for key in ('Action', 'NotAction', 'Resource', 'NotResource'):
                            if key in stmt and isinstance(stmt[key], str):
                                stmt[key] = [stmt[key]]
            return json.dumps(parsed, sort_keys=True, separators=(',', ':'))
        except (json.JSONDecodeError, TypeError, ValueError):
            return doc_str

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_current_policies(self, entity_type: str, entity_name: str,
                             namespace: str) -> List[Dict[str, str]]:
        """Read all inline policies for the entity (list names + get each doc)."""
        self.module.log('Reading inline policies for %s %s in namespace %s' % (
            entity_type, entity_name, namespace))
        try:
            if entity_type == 'user':
                policy_names = self.iam_api.list_user_policies(entity_name, namespace)
            elif entity_type == 'group':
                policy_names = self.iam_api.list_group_policies(entity_name, namespace)
            elif entity_type == 'role':
                policy_names = self.iam_api.list_role_policies(entity_name, namespace)
            else:
                self.module.exit_json(failed=True, msg="Unknown entity type: %s" % entity_type)
                return []
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Listing inline policies for %s '%s' in namespace '%s' failed with error: %s" % (
                entity_type, entity_name, namespace, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return []

        policies = []  # type: List[Dict[str, str]]
        for pname in policy_names:
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
                    # URL-decode if needed (ObjectScale may return URL-encoded JSON)
                    if '%7B' in doc or '%22' in doc:
                        doc = unquote(doc)
                    policies.append({'name': pname, 'document': doc})
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Getting inline policy '%s' for %s '%s' failed with error: %s" % (
                    pname, entity_type, entity_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)
                return []

        return policies

    # ------------------------------------------------------------------
    # Diff computation
    # ------------------------------------------------------------------

    def compute_changes(self, desired: List[Dict[str, str]],
                        current: List[Dict[str, str]],
                        state: str) -> Tuple[List[Dict[str, str]], List[str], bool]:
        """Compute the put/delete delta between desired and current policies.

        Returns (to_put, to_delete, changed):
          to_put: list of {name, document} dicts to create/update
          to_delete: list of policy names to delete
          changed: whether any changes are needed
        """
        if state == 'absent':
            current_names = [p['name'] for p in current]
            return [], current_names, bool(current_names)

        # Build lookup of current policies by name → normalized document
        current_map = {}  # type: Dict[str, str]
        for p in current:
            current_map[p['name']] = self._normalize_document(p.get('document', ''))

        desired_names = set()  # type: Set[str]
        to_put = []  # type: List[Dict[str, str]]

        for p in desired:
            name = p['name']
            desired_names.add(name)
            desired_doc = self._normalize_document(p.get('document', ''))
            current_doc = current_map.get(name)
            if current_doc is None or current_doc != desired_doc:
                to_put.append({'name': name, 'document': p.get('document', '')})

        to_delete = [n for n in current_map if n not in desired_names]
        changed = bool(to_put or to_delete)
        return to_put, to_delete, changed

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def apply_changes(self, entity_type: str, entity_name: str, namespace: str,
                      to_put: List[Dict[str, str]], to_delete: List[str]) -> None:
        """Apply policy changes (put new/updated, delete removed)."""
        for pname in sorted(to_delete):
            self.module.log('Deleting inline policy %s from %s %s' % (pname, entity_type, entity_name))
            try:
                if not self.module.check_mode:
                    if entity_type == 'user':
                        self.iam_api.delete_user_policy(entity_name, pname, namespace)
                    elif entity_type == 'group':
                        self.iam_api.delete_group_policy(entity_name, pname, namespace)
                    elif entity_type == 'role':
                        self.iam_api.delete_role_policy(entity_name, pname, namespace)
                    else:
                        self.module.exit_json(failed=True, msg="Unknown entity type: %s" % entity_type)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Deleting inline policy '%s' from %s '%s' failed with error: %s" % (
                    pname, entity_type, entity_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

        for policy in sorted(to_put, key=lambda p: p['name']):
            pname = policy['name']
            pdoc = policy.get('document', '')
            self.module.log('Putting inline policy %s on %s %s' % (pname, entity_type, entity_name))
            try:
                if not self.module.check_mode:
                    if entity_type == 'user':
                        self.iam_api.put_user_policy(entity_name, pname, pdoc, namespace)
                    elif entity_type == 'group':
                        self.iam_api.put_group_policy(entity_name, pname, pdoc, namespace)
                    elif entity_type == 'role':
                        self.iam_api.put_role_policy(entity_name, pname, pdoc, namespace)
                    else:
                        self.module.exit_json(failed=True, msg="Unknown entity type: %s" % entity_type)
            except Exception as e:
                error_msg = utils.determine_error(e)
                msg = "Putting inline policy '%s' on %s '%s' failed with error: %s" % (
                    pname, entity_type, entity_name, error_msg)
                self.module.exit_json(failed=True, msg=msg)

    # ------------------------------------------------------------------
    # State snapshot for diff
    # ------------------------------------------------------------------

    @staticmethod
    def _build_state_snapshot(policies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Build a serializable state snapshot for diff output."""
        return {
            'policies': sorted(
                [{'name': p['name'], 'document': p.get('document', '')} for p in policies],
                key=lambda p: p['name'],
            ),
        }

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def perform_module_operation(self) -> None:
        """Perform different actions based on parameters chosen in playbook."""
        entity_type, entity_name = self.determine_entity()
        namespace = self.module.params['namespace']
        state = self.module.params['state']
        desired_policies = self.module.params.get('policies') or []

        # Read current state
        current_policies = self.get_current_policies(entity_type, entity_name, namespace)
        before_policies = list(current_policies)

        # Compute delta
        to_put, to_delete, is_changed = self.compute_changes(desired_policies, current_policies, state)

        result = dict(
            changed=is_changed,
            inline_policy_details=None,
            id='%s:%s:%s' % (namespace, entity_type, entity_name),
        )  # type: Dict[str, Any]

        if is_changed:
            self.apply_changes(entity_type, entity_name, namespace, to_put, to_delete)

            # Re-read state after changes (unless check mode)
            if not self.module.check_mode:
                current_policies = self.get_current_policies(entity_type, entity_name, namespace)

        if self.module.check_mode and is_changed:
            # Simulate after state for check mode
            if state == 'absent':
                after_policies = []  # type: List[Dict[str, str]]
            else:
                # Start from current, remove deleted, add/update put
                remaining = {p['name']: p for p in current_policies if p['name'] not in to_delete}
                for p in to_put:
                    remaining[p['name']] = p
                after_policies = list(remaining.values())
        else:
            after_policies = list(current_policies)

        result['inline_policy_details'] = {
            'namespace': namespace,
            'entity_type': entity_type,
            'entity_name': entity_name,
            'policies': sorted(
                [{'name': p['name'], 'document': p.get('document', '')} for p in after_policies],
                key=lambda p: p['name'],
            ),
        }

        if self.module._diff:
            result['diff'] = dict(
                before=self._build_state_snapshot(before_policies),
                after=self._build_state_snapshot(after_policies),
            )

        self.module.log('Inline policy operation complete: changed=%s' % result['changed'])
        self.module.exit_json(**result)

    @staticmethod
    def get_iam_inline_policy_parameters() -> Dict[str, Dict[str, Any]]:
        """Module-specific parameters for IAM inline policy management."""
        return dict(
            namespace=dict(type='str', required=True),
            user_name=dict(type='str', default=None),
            group_name=dict(type='str', default=None),
            role_name=dict(type='str', default=None),
            policies=dict(type='list', elements='dict', default=None),
            state=dict(type='str', default='present', choices=['present', 'absent']),
        )


def main() -> None:
    """Create ObjectScale IAM Inline Policy object and perform actions on it."""
    obj = IamInlinePolicy()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
