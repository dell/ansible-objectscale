#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM roles on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_role

version_added: '1.0.0'

short_description: Manages IAM roles on Dell ObjectScale

description:
- Manages IAM roles on the Dell ObjectScale storage system.
  This includes creating, modifying, deleting and retrieving details of IAM roles,
  managing their trust policies, tags, managed policies, inline policies,
  and permissions boundaries.

extends_documentation_fragment:
  - dellemc.objectscale.objectscale

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

options:
  role_name:
    description:
    - The name of the IAM role.
    type: str
    required: true

  namespace_name:
    description:
    - The namespace for the IAM role.
    type: str
    required: true

  state:
    description:
    - The desired state of the IAM role.
    - C(present) - the role should exist.
    - C(absent) - the role should not exist.
    choices: ['present', 'absent']
    type: str
    default: present

  assume_role_policy_document:
    description:
    - The trust relationship policy document (JSON) that grants an entity
      permission to assume the role.
    - Required when creating a new role.
    type: dict

  description:
    description:
    - A description of the IAM role.
    type: str

  max_session_duration:
    description:
    - The maximum session duration (in seconds) for the role.
    - Valid range is 3600 to 43200 (1 hour to 12 hours).
    type: int

  path:
    description:
    - The path for the IAM role.
    type: str
    default: /

  permissions_boundary:
    description:
    - The ARN of the managed policy to set as the permissions boundary.
    - Set to empty string to remove the boundary.
    type: str

  tags:
    description:
    - Dictionary of tags to apply to the role.
    type: dict

  purge_tags:
    description:
    - If true, remove tags not in the desired set.
    type: bool
    default: true

  managed_policies:
    description:
    - List of managed policy ARNs to attach to the role.
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

  force_delete:
    description:
    - If true, remove all dependencies before deleting the role.
    type: bool
    default: false

notes:
- The I(check_mode) is supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Create an IAM role
  dellemc.objectscale.iam_role:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    role_name: "app-data-access-role"
    namespace_name: "testns"
    assume_role_policy_document:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            AWS:
              - "urn:ecs:iam::testns:user/app-service"
          Action: "sts:AssumeRole"
    state: present

- name: Create IAM role with tags, policies and description
  dellemc.objectscale.iam_role:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    role_name: "finance-data-role"
    namespace_name: "testns"
    assume_role_policy_document:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            AWS:
              - "urn:ecs:iam::testns:user/finance-admin"
          Action: "sts:AssumeRole"
    description: "Finance team data access role"
    max_session_duration: 7200
    tags:
      Env: prod
      Team: finance
    managed_policies:
      - "urn:ecs:iam::testns:policy/ReadOnly"
    inline_policies:
      restrict-bucket:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action:
              - "s3:GetObject"
            Resource: "urn:ecs:s3:::finance-bucket/*"
    state: present

- name: Delete an IAM role with force cleanup
  dellemc.objectscale.iam_role:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    role_name: "app-data-access-role"
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

role:
    description: IAM role details.
    returned: When role exists and state is present
    type: dict
    contains:
        RoleName:
            description: The name of the IAM role.
            type: str
        Arn:
            description: The ARN of the IAM role.
            type: str
        RoleId:
            description: The unique ID of the IAM role.
            type: str
        CreateDate:
            description: The date the role was created.
            type: str
        Path:
            description: The path for the IAM role.
            type: str
        AssumeRolePolicyDocument:
            description: The trust policy document.
            type: str
        Description:
            description: The description of the role.
            type: str
        MaxSessionDuration:
            description: The maximum session duration in seconds.
            type: int
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi
except (ImportError, Exception):
    IamApi = None  # type: ignore[assignment,misc]


class IamRole(object):
    """Class with operations on ObjectScale IAM roles."""

    def __init__(self):
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_role_parameters())

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

    def _extract_role_dict(self, response):
        """Extract role dict from API response object.

        The generated Pydantic models for GetRoleResponse/CreateRoleResponse
        use a mismatched 'Result' alias and drop the nested Role object
        during deserialization. We fall back to raw JSON parsing when
        to_dict() doesn't contain the expected keys.
        """
        d = response.to_dict()
        for result_key in ['Result', 'GetRoleResult', 'CreateRoleResult']:
            if result_key in d:
                role = d[result_key].get('Role')
                if role:
                    return role

        # Fallback: parse raw response body if model deserialization lost data
        try:
            raw = json.loads(response.data.decode('utf-8')) if hasattr(response, 'data') and response.data else None
        except Exception:
            raw = None
        if raw:
            for key in ['GetRoleResult', 'CreateRoleResult', 'Result']:
                if key in raw and 'Role' in raw[key]:
                    return raw[key]['Role']
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
        from urllib.parse import urlencode
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
        resp.read()  # Ensure response data is available
        if resp.status >= 400:
            body = json.loads(resp.data.decode('utf-8')) if resp.data else {}
            err = Exception(str(body))
            err.status = resp.status
            raise err
        return resp

    def _tag_role_raw(self, role_name, tags_dict):
        """Tag a role using raw API call with expanded Tags.member.N params."""
        params = {'RoleName': role_name}
        for i, (k, v) in enumerate(tags_dict.items(), 1):
            params[f'Tags.member.{i}.Key'] = k
            params[f'Tags.member.{i}.Value'] = v
        self._iam_raw_post('TagRole', params)

    def _untag_role_raw(self, role_name, tag_keys):
        """Untag a role using raw API call with expanded TagKeys.member.N params."""
        params = {'RoleName': role_name}
        for i, key in enumerate(tag_keys, 1):
            params[f'TagKeys.member.{i}'] = key
        self._iam_raw_post('UntagRole', params)

    def _paginate_list(self, list_func, result_attr, items_key, **kwargs):
        """Paginate through a list API call, collecting all items.

        Args:
            list_func: The API method to call (e.g., iam_service_list_role_tags).
            result_attr: The snake_case attribute on the response to get the
                result object (e.g., 'list_role_tags_result').
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

    def list_attached_policies(self, role_name):
        """List all attached managed policies for a role."""
        return self._paginate_list(
            self.iam_api.iam_service_list_attached_role_policies,
            'list_attached_role_policies_result',
            'AttachedPolicies',
            role_name=role_name,
            x_emc_namespace=self.namespace,
        )

    def list_inline_policy_names(self, role_name):
        """List all inline policy names for a role."""
        return self._paginate_list(
            self.iam_api.iam_service_list_role_policies,
            'list_role_policies_result',
            'PolicyNames',
            role_name=role_name,
            x_emc_namespace=self.namespace,
        )

    def list_role_tags(self, role_name):
        """List all tags for a role."""
        return self._paginate_list(
            self.iam_api.iam_service_list_role_tags,
            'list_role_tags_result',
            'Tags',
            role_name=role_name,
            x_emc_namespace=self.namespace,
        )

    def get_inline_policy_document(self, role_name, policy_name):
        """Get the policy document for an inline policy."""
        try:
            resp = self.iam_api.iam_service_get_role_policy(
                role_name=role_name,
                policy_name=policy_name,
                x_emc_namespace=self.namespace,
            )
            result = resp.to_dict()
            doc = result.get('GetRolePolicyResult', {}).get('PolicyDocument', '')
            if isinstance(doc, str):
                from urllib.parse import unquote
                try:
                    doc = json.loads(unquote(doc))
                except (json.JSONDecodeError, ValueError):
                    pass
            return doc
        except Exception:
            return None

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def get_role(self, role_name):
        """Get role details. Returns dict or None if not found."""
        try:
            resp = self._iam_raw_post('GetRole', {'RoleName': role_name})
            raw = json.loads(resp.data.decode('utf-8'))
            return raw.get('GetRoleResult', {}).get('Role')
        except Exception as e:
            status = getattr(e, 'status', None)
            if status in (404, 400):
                return None
            # Check if error dict was raised from _iam_raw_post
            err_str = str(e)
            if 'NoSuchEntity' in err_str or 'not found' in err_str.lower():
                return None
            error_msg = utils.determine_error(e)
            msg = "Getting IAM role %s failed with error: %s" % (role_name, error_msg)
            self.module.fail_json(msg=msg)
            return None

    def create_role(self, role_name):
        """Create an IAM role. Returns the created role dict."""
        try:
            assume_doc = self.module.params.get('assume_role_policy_document')
            if assume_doc is None:
                self.module.fail_json(
                    msg="assume_role_policy_document is required when creating a role"
                )
                return None

            params = {
                'RoleName': role_name,
                'AssumeRolePolicyDocument': json.dumps(assume_doc),
            }
            path = self.module.params.get('path', '/')
            if path:
                params['Path'] = path

            boundary = self.module.params.get('permissions_boundary')
            if boundary:
                params['PermissionsBoundary'] = boundary

            description = self.module.params.get('description')
            if description:
                params['Description'] = description

            max_session = self.module.params.get('max_session_duration')
            if max_session:
                params['MaxSessionDuration'] = str(max_session)

            resp = self._iam_raw_post('CreateRole', params)
            raw = json.loads(resp.data.decode('utf-8'))
            return raw.get('CreateRoleResult', {}).get('Role')
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating IAM role %s failed with error: %s" % (role_name, error_msg)
            self.module.fail_json(msg=msg)
            return None

    def delete_role(self, role_name):
        """Delete an IAM role."""
        try:
            self.iam_api.iam_service_delete_role(
                role_name=role_name,
                x_emc_namespace=self.namespace,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Deleting IAM role %s failed with error: %s" % (role_name, error_msg)
            self.module.fail_json(msg=msg)

    def force_delete_cleanup(self, role_name):
        """Remove all dependencies before deleting a role."""
        errors = []

        # Detach all managed policies
        try:
            for pol in self.list_attached_policies(role_name):
                try:
                    self.iam_api.iam_service_detach_role_policy(
                        policy_arn=pol['PolicyArn'],
                        role_name=role_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to detach policy %s: %s" % (pol.get('PolicyArn', ''), str(e)))
        except Exception as e:
            errors.append("Failed to list attached policies: %s" % str(e))

        # Delete all inline policies
        try:
            for pol_name in self.list_inline_policy_names(role_name):
                try:
                    self.iam_api.iam_service_delete_role_policy(
                        policy_name=pol_name,
                        role_name=role_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to delete inline policy %s: %s" % (pol_name, str(e)))
        except Exception as e:
            errors.append("Failed to list inline policies: %s" % str(e))

        # Delete permissions boundary if set
        try:
            role = self.get_role(role_name)
            if role and role.get('PermissionsBoundary'):
                try:
                    self.iam_api.iam_service_delete_role_permissions_boundary(
                        role_name=role_name,
                        x_emc_namespace=self.namespace,
                    )
                except Exception as e:
                    errors.append("Failed to delete permissions boundary: %s" % str(e))
        except Exception as e:
            errors.append("Failed to get role for boundary check: %s" % str(e))

        if errors:
            self.module.warn("force_delete cleanup encountered errors: %s" % "; ".join(errors))

    # ------------------------------------------------------------------
    # Sub-resource management
    # ------------------------------------------------------------------

    def manage_tags(self, role_name, desired_tags, purge=True):
        """Manage tags on a role. Returns True if any changes were made."""
        current_tags = self.list_role_tags(role_name)
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
            self._tag_role_raw(role_name, tags_to_add)
            changed = True

        if tags_to_remove:
            self._untag_role_raw(role_name, tags_to_remove)
            changed = True

        return changed

    def manage_managed_policies(self, role_name, desired_policies, purge=True):
        """Manage attached managed policies. Returns True if any changes were made."""
        current = self.list_attached_policies(role_name)
        current_arns = {p['PolicyArn'] for p in current}
        desired_set = set(desired_policies)

        changed = False

        # Attach missing policies
        for arn in desired_set - current_arns:
            self.iam_api.iam_service_attach_role_policy(
                policy_arn=arn,
                role_name=role_name,
                x_emc_namespace=self.namespace,
            )
            changed = True

        # Detach extra policies if purging
        if purge:
            for arn in current_arns - desired_set:
                self.iam_api.iam_service_detach_role_policy(
                    policy_arn=arn,
                    role_name=role_name,
                    x_emc_namespace=self.namespace,
                )
                changed = True

        return changed

    def manage_inline_policies(self, role_name, desired_policies, purge=True):
        """Manage inline policies. Returns True if any changes were made."""
        current_names = self.list_inline_policy_names(role_name)
        current_set = set(current_names)
        desired_set = set(desired_policies.keys())

        changed = False

        # Put new or updated policies
        for name, doc in desired_policies.items():
            if name in current_set:
                # Check if document has changed
                current_doc = self.get_inline_policy_document(role_name, name)
                if current_doc == doc:
                    continue

            encoded_doc = json.dumps(doc)
            self.iam_api.iam_service_put_role_policy(
                policy_name=name,
                policy_document=encoded_doc,
                role_name=role_name,
                x_emc_namespace=self.namespace,
            )
            changed = True

        # Delete extra policies if purging
        if purge:
            for name in current_set - desired_set:
                self.iam_api.iam_service_delete_role_policy(
                    policy_name=name,
                    role_name=role_name,
                    x_emc_namespace=self.namespace,
                )
                changed = True

        return changed

    def manage_permissions_boundary(self, role_name, desired_boundary, role):
        """Manage permissions boundary. Returns True if any changes were made."""
        if desired_boundary is None:
            return False

        current_boundary = None
        if role and role.get('PermissionsBoundary'):
            current_boundary = role['PermissionsBoundary'].get('PermissionsBoundaryArn')

        if desired_boundary == '':
            # Remove boundary
            if current_boundary:
                self.iam_api.iam_service_delete_role_permissions_boundary(
                    role_name=role_name,
                    x_emc_namespace=self.namespace,
                )
                return True
            return False

        if desired_boundary != current_boundary:
            self.iam_api.iam_service_put_role_permissions_boundary(
                permissions_boundary=desired_boundary,
                role_name=role_name,
                x_emc_namespace=self.namespace,
            )
            return True

        return False

    def manage_assume_role_policy(self, role_name, desired_doc, role):
        """Manage the trust policy (assume role policy document).

        Returns True if any changes were made.
        """
        if desired_doc is None:
            return False

        # Compare with current trust policy
        current_doc = role.get('AssumeRolePolicyDocument') if role else None
        if isinstance(current_doc, str):
            from urllib.parse import unquote
            try:
                current_doc = json.loads(unquote(current_doc))
            except (json.JSONDecodeError, ValueError):
                pass

        if current_doc == desired_doc:
            return False

        encoded_doc = json.dumps(desired_doc)
        self.iam_api.iam_service_update_assume_role_policy(
            role_name=role_name,
            policy_document=encoded_doc,
            x_emc_namespace=self.namespace,
        )
        return True

    def manage_role_attributes(self, role_name, role):
        """Update role description and max_session_duration if changed.

        Returns True if any changes were made.
        """
        changed = False
        description = self.module.params.get('description')
        max_session_duration = self.module.params.get('max_session_duration')

        needs_update = False
        kwargs = dict(
            role_name=role_name,
            x_emc_namespace=self.namespace,
        )

        if description is not None:
            current_desc = role.get('Description', '') if role else ''
            if description != current_desc:
                kwargs['description'] = description
                needs_update = True

        if max_session_duration is not None:
            current_dur = role.get('MaxSessionDuration') if role else None
            if max_session_duration != current_dur:
                kwargs['max_session_duration'] = max_session_duration
                needs_update = True

        if needs_update:
            self.iam_api.iam_service_update_role(**kwargs)
            changed = True

        return changed

    # ------------------------------------------------------------------
    # State capture for diff mode
    # ------------------------------------------------------------------

    def capture_current_state(self, role_name, role):
        """Capture current state of role and sub-resources for diff mode."""
        if role is None:
            return {}

        return {
            'role': role,
            'tags': self.list_role_tags(role_name),
            'managed_policies': self.list_attached_policies(role_name),
            'inline_policies': self.list_inline_policy_names(role_name),
        }

    # ------------------------------------------------------------------
    # Main orchestrator
    # ------------------------------------------------------------------

    def perform_module_operation(self):
        """Perform different actions based on parameters chosen in playbook."""
        result = dict(changed=False)

        role_name = self.module.params['role_name']
        state = self.module.params['state']

        if state == 'absent':
            role = self.get_role(role_name)

            if role:
                if self.module.check_mode:
                    result['changed'] = True
                else:
                    if self.module._diff:
                        before_state = self.capture_current_state(role_name, role)

                    if self.module.params.get('force_delete'):
                        self.force_delete_cleanup(role_name)

                    self.delete_role(role_name)
                    result['changed'] = True

                    if self.module._diff:
                        result['diff'] = {
                            'before': before_state,
                            'after': {},
                        }
            else:
                if self.module._diff:
                    result['diff'] = {'before': {}, 'after': {}}

        elif state == 'present':
            role = self.get_role(role_name)

            if role is None:
                # Role doesn't exist — create it
                if self.module.check_mode:
                    result['changed'] = True
                    self.module.exit_json(**result)
                    return

                self.create_role(role_name)
                result['changed'] = True
                # Re-fetch role after creation
                role = self.get_role(role_name)

            if role is not None:
                if self.module._diff:
                    before_state = self.capture_current_state(role_name, role)

                # Manage role attributes (description, max_session_duration)
                if self.module.params.get('description') is not None or \
                   self.module.params.get('max_session_duration') is not None:
                    if not self.module.check_mode:
                        if self.manage_role_attributes(role_name, role):
                            result['changed'] = True
                    else:
                        # Check mode: compare attributes
                        desc = self.module.params.get('description')
                        dur = self.module.params.get('max_session_duration')
                        if desc is not None and desc != (role.get('Description', '') or ''):
                            result['changed'] = True
                        if dur is not None and dur != role.get('MaxSessionDuration'):
                            result['changed'] = True

                # Manage assume role policy document (trust policy)
                if self.module.params.get('assume_role_policy_document') is not None:
                    if not self.module.check_mode:
                        if self.manage_assume_role_policy(
                            role_name,
                            self.module.params['assume_role_policy_document'],
                            role,
                        ):
                            result['changed'] = True
                    else:
                        desired_doc = self.module.params['assume_role_policy_document']
                        current_doc = role.get('AssumeRolePolicyDocument')
                        if isinstance(current_doc, str):
                            from urllib.parse import unquote
                            try:
                                current_doc = json.loads(unquote(current_doc))
                            except (json.JSONDecodeError, ValueError):
                                pass
                        if current_doc != desired_doc:
                            result['changed'] = True

                # Manage tags
                if self.module.params.get('tags') is not None:
                    if not self.module.check_mode:
                        if self.manage_tags(
                            role_name,
                            self.module.params['tags'],
                            self.module.params.get('purge_tags', True),
                        ):
                            result['changed'] = True
                    else:
                        current_tags = self.list_role_tags(role_name)
                        current_dict = {t['Key']: t['Value'] for t in current_tags}
                        desired = self.module.params['tags']
                        if current_dict != desired:
                            result['changed'] = True

                # Manage managed policies
                if self.module.params.get('managed_policies') is not None:
                    if not self.module.check_mode:
                        if self.manage_managed_policies(
                            role_name,
                            self.module.params['managed_policies'],
                            self.module.params.get('purge_managed_policies', True),
                        ):
                            result['changed'] = True
                    else:
                        current = self.list_attached_policies(role_name)
                        current_arns = {p['PolicyArn'] for p in current}
                        desired_set = set(self.module.params['managed_policies'])
                        if current_arns != desired_set:
                            result['changed'] = True

                # Manage inline policies
                if self.module.params.get('inline_policies') is not None:
                    if not self.module.check_mode:
                        if self.manage_inline_policies(
                            role_name,
                            self.module.params['inline_policies'],
                            self.module.params.get('purge_inline_policies', True),
                        ):
                            result['changed'] = True
                    else:
                        current_names = set(self.list_inline_policy_names(role_name))
                        desired_names = set(self.module.params['inline_policies'].keys())
                        if current_names != desired_names:
                            result['changed'] = True

                # Manage permissions boundary
                if self.module.params.get('permissions_boundary') is not None:
                    if not self.module.check_mode:
                        if self.manage_permissions_boundary(
                            role_name,
                            self.module.params['permissions_boundary'],
                            role,
                        ):
                            result['changed'] = True
                    else:
                        desired_boundary = self.module.params['permissions_boundary']
                        current_boundary = None
                        if role and role.get('PermissionsBoundary'):
                            current_boundary = role['PermissionsBoundary'].get(
                                'PermissionsBoundaryArn')
                        if desired_boundary == '':
                            if current_boundary:
                                result['changed'] = True
                        elif desired_boundary != current_boundary:
                            result['changed'] = True

                if self.module._diff:
                    after_state = self.capture_current_state(role_name, role)
                    result['diff'] = {
                        'before': before_state,
                        'after': after_state,
                    }

            result['role'] = role

        self.module.exit_json(**result)

    @staticmethod
    def get_iam_role_parameters():
        """Return the argument spec for IAM role module parameters."""
        return dict(
            role_name=dict(type='str', required=True),
            namespace_name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            assume_role_policy_document=dict(type='dict'),
            description=dict(type='str'),
            max_session_duration=dict(type='int'),
            path=dict(type='str', default='/'),
            permissions_boundary=dict(type='str'),
            tags=dict(type='dict'),
            purge_tags=dict(type='bool', default=True),
            managed_policies=dict(type='list', elements='str'),
            purge_managed_policies=dict(type='bool', default=True),
            inline_policies=dict(type='dict'),
            purge_inline_policies=dict(type='bool', default=True),
            force_delete=dict(type='bool', default=False),
        )


def main():
    """Create ObjectScale IAM Role object and perform actions on it."""
    obj = IamRole()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
