#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM users on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_user

version_added: '1.0.0'

short_description: Manages IAM users on Dell ObjectScale

description:
- Manages IAM users on the Dell ObjectScale storage system.
  This includes creating, modifying, deleting and retrieving details of IAM users,
  managing their tags, policies, groups, permissions boundaries, and access keys.

extends_documentation_fragment:
  - dellemc.objectscale.objectscale

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

options:
  user_name:
    description:
    - The name of the IAM user.
    type: str
    required: true

  namespace_name:
    description:
    - The namespace for the IAM user.
    type: str
    required: true

  state:
    description:
    - The desired state of the IAM user.
    - C(present) - the user should exist.
    - C(absent) - the user should not exist.
    choices: ['present', 'absent']
    type: str
    default: present

  path:
    description:
    - The path for the IAM user.
    type: str
    default: /

  permissions_boundary:
    description:
    - The ARN of the managed policy to set as the permissions boundary.
    - Set to empty string to remove the boundary.
    type: str

  tags:
    description:
    - Dictionary of tags to apply to the user.
    type: dict

  purge_tags:
    description:
    - If true, remove tags not in the desired set.
    type: bool
    default: true

  managed_policies:
    description:
    - List of managed policy ARNs to attach to the user.
    type: list
    elements: str

  purge_managed_policies:
    description:
    - If true, detach policies not in the desired list.
    type: bool
    default: true

  inline_policies:
    description:
    - Dictionary of inline policy names to policy documents.
    type: dict

  purge_inline_policies:
    description:
    - If true, delete inline policies not in the desired set.
    type: bool
    default: true

  groups:
    description:
    - List of group names the user should belong to.
    type: list
    elements: str

  purge_groups:
    description:
    - If true, remove user from groups not in the desired list.
    type: bool
    default: true

  access_key_state:
    description:
    - State for access key operations.
    - C(present) creates a new access key.
    - C(absent) deletes an existing access key.
    choices: ['present', 'absent']
    type: str

  access_key_id:
    description:
    - The access key ID for delete or status update operations.
    type: str

  access_key_status:
    description:
    - Desired status for an access key.
    choices: ['Active', 'Inactive']
    type: str

  force_delete:
    description:
    - If true, remove all dependencies before deleting the user.
    type: bool
    default: false

notes:
- The I(check_mode) is supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Create an IAM user
  dellemc.objectscale.iam_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: "testuser"
    namespace_name: "testns"
    state: present

- name: Create IAM user with tags and policies
  dellemc.objectscale.iam_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: "testuser"
    namespace_name: "testns"
    tags:
      Env: prod
      Team: ops
    managed_policies:
      - "urn:ecs:iam::testns:policy/ReadOnly"
    groups:
      - admins
    state: present

- name: Delete an IAM user with force cleanup
  dellemc.objectscale.iam_user:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: "testuser"
    namespace_name: "testns"
    state: absent
    force_delete: true
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: false

user:
    description: IAM user details.
    returned: When user exists and state is present
    type: dict
    contains:
        UserName:
            description: The name of the IAM user.
            type: str
        Arn:
            description: The ARN of the IAM user.
            type: str
        UserId:
            description: The unique ID of the IAM user.
            type: str
        CreateDate:
            description: The date the user was created.
            type: str
        Path:
            description: The path for the IAM user.
            type: str

access_key:
    description: Created access key details.
    returned: When access_key_state is present
    type: dict
    contains:
        AccessKeyId:
            description: The access key ID.
            type: str
        SecretAccessKey:
            description: The secret access key.
            type: str
        Status:
            description: The status of the access key.
            type: str
'''

import json
from urllib.parse import quote as url_encode
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi
except Exception:
    IamApi = None  # type: ignore[assignment,misc]


class IamUser(object):
    """Class with operations on ObjectScale IAM users."""

    def __init__(self):
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_user_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
            required_if=[
                ('access_key_state', 'absent', ['access_key_id']),
            ],
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

        self.namespace = self.module.params.get('namespace_name')

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _extract_user_dict(self, response):
        """Extract user dict from API response object."""
        d = response.to_dict()
        # Handle different response types
        for result_key in ['GetUserResult', 'CreateUserResult']:
            if result_key in d:
                return d[result_key].get('User', d)
        return d

    @staticmethod
    def _dict_to_tag_members(tags_dict):
        """Convert a dict of tags to a list of {Key, Value} dicts."""
        return [{'Key': k, 'Value': v} for k, v in tags_dict.items()]

    def _iam_raw_post(self, action, params=None):
        """Make a raw IAM POST call with properly expanded member.N params.

        The generated client doesn't handle AWS-style member.N query
        parameters correctly (it JSON-stringifies dicts instead of
        expanding them into individual query params). This helper
        constructs the URL manually.
        """
        from urllib.parse import quote, urlencode
        base = self.iam_api.api_client.configuration.host
        query_parts = [('Action', action)]
        if params:
            for k, v in params.items():
                query_parts.append((k, str(v)))
        qs = urlencode(query_parts)
        url = f"{base}/iam?{qs}"
        headers = {}
        for key in ['AuthToken']:
            token = self.iam_api.api_client.configuration.api_key.get(key)
            if token:
                prefix = self.iam_api.api_client.configuration.api_key_prefix.get(key, '')
                headers['X-SDS-AUTH-TOKEN'] = f"{prefix}{token}" if prefix else token
        if self.namespace:
            headers['x-emc-namespace'] = self.namespace
        headers['Accept'] = 'application/json'
        resp = self.iam_api.api_client.rest_client.request(
            'POST', url, headers=headers,
        )
        if resp.status >= 400:
            import json
            body = json.loads(resp.data.decode('utf-8')) if resp.data else {}
            raise RuntimeError(str(body))
        return resp

    def _tag_user_raw(self, user_name, tags_dict):
        """Tag a user using raw API call with expanded Tags.member.N params."""
        params = {'UserName': user_name}
        for i, (k, v) in enumerate(tags_dict.items(), 1):
            params[f'Tags.member.{i}.Key'] = k
            params[f'Tags.member.{i}.Value'] = v
        self._iam_raw_post('TagUser', params)

    def _untag_user_raw(self, user_name, tag_keys):
        """Untag a user using raw API call with expanded TagKeys.member.N params."""
        params = {'UserName': user_name}
        for i, key in enumerate(tag_keys, 1):
            params[f'TagKeys.member.{i}'] = key
        self._iam_raw_post('UntagUser', params)

    def _paginate_list(self, list_func, result_attr, items_key, **kwargs):
        """Paginate through a list API call, collecting all items.

        Args:
            list_func: The API method to call (e.g., iam_service_list_user_tags).
            result_attr: The snake_case attribute on the response to get the
                result object (e.g., 'list_user_tags_result').
            items_key: The CamelCase key in the result's to_dict() that holds
                the items (e.g., 'Tags').
        """
        all_items = []
        marker = None
        while True:
            if marker:
                kwargs['marker'] = marker
            response = list_func(**kwargs)
            result_obj = getattr(response, result_attr, None)
            if result_obj is None:
                break
            result_dict = result_obj.to_dict()
            items = result_dict.get(items_key, []) or []
            all_items.extend(items)
            if result_dict.get('IsTruncated', False):
                marker = result_dict.get('Marker')
            else:
                break
        return all_items

    # ------------------------------------------------------------------
    # List helpers (used by manage_* and force_delete_cleanup)
    # ------------------------------------------------------------------

    def list_access_keys(self, user_name):
        """List all access keys for a user."""
        return self._paginate_list(
            self.iam_api.iam_service_list_access_keys,
            'list_access_keys_result',
            'AccessKeyMetadata',
            user_name=user_name,
            x_emc_namespace=self.namespace,
        )

    def list_attached_policies(self, user_name):
        """List all attached managed policies for a user."""
        return self._paginate_list(
            self.iam_api.iam_service_list_attached_user_policies,
            'list_attached_user_policies_result',
            'AttachedPolicies',
            user_name=user_name,
            x_emc_namespace=self.namespace,
        )

    def list_inline_policy_names(self, user_name):
        """List all inline policy names for a user."""
        return self._paginate_list(
            self.iam_api.iam_service_list_user_policies,
            'list_user_policies_result',
            'PolicyNames',
            user_name=user_name,
            x_emc_namespace=self.namespace,
        )

    def list_groups_for_user(self, user_name):
        """List all groups a user belongs to."""
        return self._paginate_list(
            self.iam_api.iam_service_list_groups_for_user,
            'list_groups_for_user_result',
            'Groups',
            user_name=user_name,
            x_emc_namespace=self.namespace,
        )

    def list_user_tags(self, user_name):
        """List all tags for a user."""
        return self._paginate_list(
            self.iam_api.iam_service_list_user_tags,
            'list_user_tags_result',
            'Tags',
            user_name=user_name,
            x_emc_namespace=self.namespace,
        )

    def get_inline_policy_document(self, user_name, policy_name):
        """Get the policy document for an inline policy."""
        try:
            resp = self.iam_api.iam_service_get_user_policy(
                user_name=user_name,
                policy_name=policy_name,
                x_emc_namespace=self.namespace,
            )
            result = resp.to_dict()
            doc = result.get('GetUserPolicyResult', {}).get('PolicyDocument', '')
            if isinstance(doc, str):
                from urllib.parse import unquote
                try:
                    doc = json.loads(unquote(doc))
                except ValueError:
                    pass
            return doc
        except Exception:
            return None

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def get_user(self, user_name):
        """Get user details. Returns dict or None if not found."""
        try:
            response = self.iam_api.iam_service_get_user(
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            return self._extract_user_dict(response)
        except Exception as e:
            status = getattr(e, 'status', None)
            if status in (404, 400):
                return None
            error_msg = utils.determine_error(e)
            msg = "Getting IAM user %s failed with error: %s" % (user_name, error_msg)
            self.module.fail_json(msg=msg)
            return None

    def create_user(self, user_name):
        """Create an IAM user. Returns the created user dict."""
        try:
            kwargs = dict(
                user_name=user_name,
                x_emc_namespace=self.namespace,
                path=self.module.params.get('path', '/'),
            )

            # Optional permissions boundary
            boundary = self.module.params.get('permissions_boundary')
            if boundary:
                kwargs['permissions_boundary'] = boundary

            response = self.iam_api.iam_service_create_user(**kwargs)
            return self._extract_user_dict(response)
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating IAM user %s failed with error: %s" % (user_name, error_msg)
            self.module.fail_json(msg=msg)
            return None

    def delete_user(self, user_name):
        """Delete an IAM user."""
        try:
            self.iam_api.iam_service_delete_user(
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Deleting IAM user %s failed with error: %s" % (user_name, error_msg)
            self.module.fail_json(msg=msg)

    def _cleanup_access_keys(self, user_name, errors):
        """Delete all access keys for a user during force-delete cleanup."""
        try:
            for key in self.list_access_keys(user_name):
                try:
                    self.iam_api.iam_service_delete_access_key(
                        access_key_id=key['AccessKeyId'],
                        user_name=user_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to delete access key %s: %s" % (key.get('AccessKeyId', ''), str(e)))
        except Exception as e:
            errors.append("Failed to list access keys: %s" % str(e))

    def _cleanup_policies(self, user_name, errors):
        """Detach managed and delete inline policies during force-delete cleanup."""
        try:
            for pol in self.list_attached_policies(user_name):
                try:
                    self.iam_api.iam_service_detach_user_policy(
                        policy_arn=pol['PolicyArn'],
                        user_name=user_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to detach policy %s: %s" % (pol.get('PolicyArn', ''), str(e)))
        except Exception as e:
            errors.append("Failed to list attached policies: %s" % str(e))

        try:
            for pol_name in self.list_inline_policy_names(user_name):
                try:
                    self.iam_api.iam_service_delete_user_policy(
                        policy_name=pol_name,
                        user_name=user_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to delete inline policy %s: %s" % (pol_name, str(e)))
        except Exception as e:
            errors.append("Failed to list inline policies: %s" % str(e))

    def _cleanup_groups_and_boundary(self, user_name, errors):
        """Remove from groups and delete boundary during force-delete cleanup."""
        try:
            for group in self.list_groups_for_user(user_name):
                try:
                    self.iam_api.iam_service_remove_user_from_group(
                        group_name=group['GroupName'],
                        user_name=user_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to remove from group %s: %s" % (group.get('GroupName', ''), str(e)))
        except Exception as e:
            errors.append("Failed to list groups: %s" % str(e))

        try:
            user = self.get_user(user_name)
            if user and user.get('PermissionsBoundary'):
                try:
                    self.iam_api.iam_service_delete_user_permissions_boundary(
                        user_name=user_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to delete permissions boundary: %s" % str(e))
        except Exception as e:
            errors.append("Failed to get user for boundary check: %s" % str(e))

    def force_delete_cleanup(self, user_name):
        """Remove all dependencies before deleting a user."""
        errors = []
        self._cleanup_access_keys(user_name, errors)
        self._cleanup_policies(user_name, errors)
        self._cleanup_groups_and_boundary(user_name, errors)
        if errors:
            self.module.warn("force_delete cleanup encountered errors: %s" % "; ".join(errors))

    # ------------------------------------------------------------------
    # Sub-resource management
    # ------------------------------------------------------------------

    def manage_tags(self, user_name, desired_tags, purge=True):
        """Manage tags on a user. Returns True if any changes were made."""
        current_tags = self.list_user_tags(user_name)
        current_dict = {t['Key']: t['Value'] for t in current_tags}

        changed = False

        # Find tags to add or update
        tags_to_add = {}
        for k, v in desired_tags.items():
            if k not in current_dict or current_dict[k] != v:
                tags_to_add[k] = v

        # Find tags to remove (only if purging)
        tags_to_remove = []
        if purge:
            for k in current_dict:
                if k not in desired_tags:
                    tags_to_remove.append(k)

        if tags_to_add:
            self._tag_user_raw(user_name, tags_to_add)
            changed = True

        if tags_to_remove:
            self._untag_user_raw(user_name, tags_to_remove)
            changed = True

        return changed

    def manage_managed_policies(self, user_name, desired_policies, purge=True):
        """Manage attached managed policies. Returns True if any changes were made."""
        current = self.list_attached_policies(user_name)
        current_arns = {p['PolicyArn'] for p in current}
        desired_set = set(desired_policies)

        changed = False

        # Attach missing policies
        for arn in desired_set - current_arns:
            self.iam_api.iam_service_attach_user_policy(
                policy_arn=arn,
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            changed = True

        # Detach extra policies if purging
        if purge:
            for arn in current_arns - desired_set:
                self.iam_api.iam_service_detach_user_policy(
                    policy_arn=arn,
                    user_name=user_name,
                    x_emc_namespace=self.namespace,
                )
                changed = True

        return changed

    def manage_inline_policies(self, user_name, desired_policies, purge=True):
        """Manage inline policies. Returns True if any changes were made."""
        current_names = self.list_inline_policy_names(user_name)
        current_set = set(current_names)
        desired_set = set(desired_policies.keys())

        changed = False

        # Put new or updated policies
        for name, doc in desired_policies.items():
            if name in current_set:
                # Check if document has changed
                current_doc = self.get_inline_policy_document(user_name, name)
                if current_doc == doc:
                    continue

            encoded_doc = url_encode(json.dumps(doc))
            self.iam_api.iam_service_put_user_policy(
                policy_name=name,
                policy_document=encoded_doc,
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            changed = True

        # Delete extra policies if purging
        if purge:
            for name in current_set - desired_set:
                self.iam_api.iam_service_delete_user_policy(
                    policy_name=name,
                    user_name=user_name,
                    x_emc_namespace=self.namespace,
                )
                changed = True

        return changed

    def manage_groups(self, user_name, desired_groups, purge=True):
        """Manage group membership. Returns True if any changes were made."""
        current = self.list_groups_for_user(user_name)
        current_names = {g['GroupName'] for g in current}
        desired_set = set(desired_groups)

        changed = False

        # Add to missing groups
        for group in desired_set - current_names:
            self.iam_api.iam_service_add_user_to_group(
                group_name=group,
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            changed = True

        # Remove from extra groups if purging
        if purge:
            for group in current_names - desired_set:
                self.iam_api.iam_service_remove_user_from_group(
                    group_name=group,
                    user_name=user_name,
                    x_emc_namespace=self.namespace,
                )
                changed = True

        return changed

    def manage_permissions_boundary(self, user_name, desired_boundary, user):
        """Manage permissions boundary. Returns True if any changes were made."""
        if desired_boundary is None:
            return False

        current_boundary = None
        if user and user.get('PermissionsBoundary'):
            current_boundary = user['PermissionsBoundary'].get('PermissionsBoundaryArn')

        if desired_boundary == '':
            # Remove boundary
            if current_boundary:
                self.iam_api.iam_service_delete_user_permissions_boundary(
                    user_name=user_name,
                    x_emc_namespace=self.namespace,
                )
                return True
            return False

        if desired_boundary != current_boundary:
            self.iam_api.iam_service_put_user_permissions_boundary(
                permissions_boundary=desired_boundary,
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            return True

        return False

    # ------------------------------------------------------------------
    # Access key operations
    # ------------------------------------------------------------------

    def create_access_key(self, user_name):
        """Create a new access key for a user. Returns key dict."""
        try:
            response = self.iam_api.iam_service_create_access_key(
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            result = response.to_dict()
            return result['CreateAccessKeyResult']['AccessKey']
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating access key for IAM user %s failed with error: %s" % (
                user_name, error_msg)
            self.module.fail_json(msg=msg)
            return None

    def delete_access_key(self, user_name, access_key_id):
        """Delete an access key. Returns True if changed."""
        keys = self.list_access_keys(user_name)
        found = any(k['AccessKeyId'] == access_key_id for k in keys)

        if not found:
            return False

        self.iam_api.iam_service_delete_access_key(
            access_key_id=access_key_id,
            user_name=user_name,
            x_emc_namespace=self.namespace,
        )
        return True

    def update_access_key_status(self, user_name, access_key_id, desired_status):
        """Update access key status. Returns True if changed."""
        keys = self.list_access_keys(user_name)
        current_key = None
        for k in keys:
            if k['AccessKeyId'] == access_key_id:
                current_key = k
                break

        if current_key is None:
            return False

        if current_key.get('Status') == desired_status:
            return False

        self.iam_api.iam_service_update_access_key(
            access_key_id=access_key_id,
            status=desired_status,
            user_name=user_name,
            x_emc_namespace=self.namespace,
        )
        return True

    # ------------------------------------------------------------------
    # State capture for diff mode
    # ------------------------------------------------------------------

    def capture_current_state(self, user_name, user):
        """Capture current state of user and sub-resources for diff mode."""
        if user is None:
            return {}

        return {
            'user': user,
            'tags': self.list_user_tags(user_name),
            'managed_policies': self.list_attached_policies(user_name),
            'inline_policies': self.list_inline_policy_names(user_name),
            'groups': self.list_groups_for_user(user_name),
            'access_keys': self.list_access_keys(user_name),
        }

    # ------------------------------------------------------------------
    # Main orchestrator
    # ------------------------------------------------------------------

    def _handle_absent(self, user_name, result):
        """Handle state=absent logic for a user."""
        user = self.get_user(user_name)
        if user:
            if self.module.check_mode:
                result['changed'] = True
            else:
                if self.module._diff:
                    before_state = self.capture_current_state(user_name, user)
                if self.module.params.get('force_delete'):
                    self.force_delete_cleanup(user_name)
                self.delete_user(user_name)
                result['changed'] = True
                if self.module._diff:
                    result['diff'] = {'before': before_state, 'after': {}}
        elif self.module._diff:
            result['diff'] = {'before': {}, 'after': {}}

    def _apply_present_subresources(self, user_name, user, result):
        """Apply sub-resource management for state=present."""
        params = self.module.params
        check_mode = self.module.check_mode

        if params.get('tags') is not None:
            if not check_mode:
                if self.manage_tags(user_name, params['tags'], params.get('purge_tags', True)):
                    result['changed'] = True
            else:
                current_tags = self.list_user_tags(user_name)
                current_dict = {t['Key']: t['Value'] for t in current_tags}
                if current_dict != params['tags']:
                    result['changed'] = True

        if params.get('managed_policies') is not None:
            if not check_mode:
                if self.manage_managed_policies(
                        user_name, params['managed_policies'],
                        params.get('purge_managed_policies', True)):
                    result['changed'] = True
            else:
                current = self.list_attached_policies(user_name)
                if {p['PolicyArn'] for p in current} != set(params['managed_policies']):
                    result['changed'] = True

        if params.get('inline_policies') is not None:
            if not check_mode:
                if self.manage_inline_policies(
                        user_name, params['inline_policies'],
                        params.get('purge_inline_policies', True)):
                    result['changed'] = True
            else:
                current_names = set(self.list_inline_policy_names(user_name))
                if current_names != set(params['inline_policies'].keys()):
                    result['changed'] = True

        if params.get('groups') is not None:
            if not check_mode:
                if self.manage_groups(
                        user_name, params['groups'],
                        params.get('purge_groups', True)):
                    result['changed'] = True
            else:
                current = self.list_groups_for_user(user_name)
                if {g['GroupName'] for g in current} != set(params['groups']):
                    result['changed'] = True

        if params.get('permissions_boundary') is not None:
            if not check_mode:
                if self.manage_permissions_boundary(
                        user_name, params['permissions_boundary'],
                        user):
                    result['changed'] = True
            else:
                desired_boundary = params['permissions_boundary']
                current_boundary = None
                if user and user.get('PermissionsBoundary'):
                    current_boundary = user['PermissionsBoundary'].get('PermissionsBoundaryArn')
                if desired_boundary == '':
                    if current_boundary:
                        result['changed'] = True
                elif desired_boundary != current_boundary:
                    result['changed'] = True

    def _apply_access_key_ops(self, user_name, result):
        """Handle access key create/delete/update operations."""
        params = self.module.params
        check_mode = self.module.check_mode
        access_key_state = params.get('access_key_state')
        access_key_id = params.get('access_key_id')
        access_key_status = params.get('access_key_status')

        if access_key_state == 'present':
            if not check_mode:
                result['access_key'] = self.create_access_key(user_name)
            result['changed'] = True
        elif access_key_state == 'absent' and access_key_id:
            if not check_mode:
                if self.delete_access_key(user_name, access_key_id):
                    result['changed'] = True
            else:
                keys = self.list_access_keys(user_name)
                if any(k['AccessKeyId'] == access_key_id for k in keys):
                    result['changed'] = True
        elif access_key_id and access_key_status:
            if not check_mode:
                if self.update_access_key_status(user_name, access_key_id, access_key_status):
                    result['changed'] = True
            else:
                keys = self.list_access_keys(user_name)
                current_key = next(
                    (k for k in keys if k['AccessKeyId'] == access_key_id), None)
                if current_key and current_key.get('Status') != access_key_status:
                    result['changed'] = True

    def perform_module_operation(self):
        """Perform different actions based on parameters chosen in playbook."""
        result = dict(changed=False)
        user_name = self.module.params['user_name']
        state = self.module.params['state']

        if state == 'absent':
            self._handle_absent(user_name, result)

        elif state == 'present':
            user = self.get_user(user_name)

            if user is None:
                if self.module.check_mode:
                    result['changed'] = True
                    self.module.exit_json(**result)
                    return
                self.create_user(user_name)
                result['changed'] = True
                user = self.get_user(user_name)

            if user is not None:
                if self.module._diff:
                    before_state = self.capture_current_state(user_name, user)

                self._apply_present_subresources(user_name, user, result)
                self._apply_access_key_ops(user_name, result)

                if self.module._diff:
                    after_state = self.capture_current_state(user_name, user)
                    if 'access_key' in result and result['access_key']:
                        ak = result['access_key'].copy()
                        if 'SecretAccessKey' in ak:
                            ak['SecretAccessKey'] = '***'
                        after_state['access_key'] = ak
                    result['diff'] = {
                        'before': before_state,
                        'after': after_state,
                    }

            result['user'] = user

        self.module.exit_json(**result)

    @staticmethod
    def get_iam_user_parameters():
        """Return the argument spec for IAM user module parameters."""
        return dict(
            user_name=dict(type='str', required=True),
            namespace_name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            path=dict(type='str', default='/'),
            permissions_boundary=dict(type='str'),
            tags=dict(type='dict'),
            purge_tags=dict(type='bool', default=True),
            managed_policies=dict(type='list', elements='str'),
            purge_managed_policies=dict(type='bool', default=True),
            inline_policies=dict(type='dict'),
            purge_inline_policies=dict(type='bool', default=True),
            groups=dict(type='list', elements='str'),
            purge_groups=dict(type='bool', default=True),
            access_key_state=dict(type='str', choices=['present', 'absent']),
            access_key_id=dict(type='str'),
            access_key_status=dict(type='str', choices=['Active', 'Inactive']),
            force_delete=dict(type='bool', default=False),
        )


def main():
    """Create ObjectScale IAM User object and perform actions on it."""
    obj = IamUser()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
