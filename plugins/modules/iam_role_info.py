#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering IAM role information from Dell ObjectScale

NOTE: Integration tests for this module have been migrated to the QE repository
(ansible-objectscale-qe) following the established pattern for IAM modules.
See ansible-objectscale-qe/IAM_Role/ for functional tests.
This migration ensures proper separation of concerns and enables CI/CD integration.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_role_info

version_added: '1.0.0'

short_description: Gather IAM role information from Dell ObjectScale

description:
- Gather information about IAM roles on Dell ObjectScale.
- Can retrieve a single role by name or list all roles in a namespace.
- Supports optional enrichment with attached managed policies, inline policies,
  and role tags.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

extends_documentation_fragment:
- dellemc.objectscale.objectscale

options:
  role_name:
    description:
    - The name of the IAM role to retrieve.
    - If not specified, all roles in the namespace are listed.
    type: str
    required: false

  namespace_name:
    description:
    - The ObjectScale namespace to query IAM roles from.
    type: str
    required: true

  include_attached_policies:
    description:
    - Whether to include attached managed policies for each role.
    type: bool
    default: false
    required: false

  include_inline_policies:
    description:
    - Whether to include inline policy names for each role.
    type: bool
    default: false
    required: false

  inline_policy_name:
    description:
    - Name of a specific inline policy to retrieve the document for.
    type: str
    required: false

  include_tags:
    description:
    - Whether to include role tags for each role.
    type: bool
    default: false
    required: false

notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: List all IAM roles in a namespace
  dellemc.objectscale.iam_role_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
  register: all_roles

- name: Get a specific IAM role with policies and tags
  dellemc.objectscale.iam_role_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
    role_name: "app-data-access-role"
    include_attached_policies: true
    include_inline_policies: true
    include_tags: true
  register: role_info

- name: List all roles with full enrichment
  dellemc.objectscale.iam_role_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
    include_attached_policies: true
    include_inline_policies: true
    include_tags: true
  register: enriched_roles
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed. Always false for info modules.
    returned: always
    type: bool
    sample: false

iam_roles:
    description: List of IAM role dictionaries.
    returned: always
    type: list
    elements: dict
    contains:
        RoleName:
            description: The friendly name of the role.
            type: str
        RoleId:
            description: The unique identifier for the role.
            type: str
        Arn:
            description: The Amazon Resource Name (ARN) of the role.
            type: str
        CreateDate:
            description: The date and time the role was created.
            type: str
        Path:
            description: The path to the role.
            type: str
        AssumeRolePolicyDocument:
            description: The trust relationship policy document (JSON string).
            type: str
        Description:
            description: The description of the role.
            type: str
        MaxSessionDuration:
            description: The maximum session duration in seconds.
            type: int
        PermissionsBoundary:
            description: The permission boundary details if set.
            type: dict
        attached_policies:
            description: List of attached managed policies (when include_attached_policies is true).
            type: list
            returned: when include_attached_policies is true
        inline_policies:
            description: List of inline policy names (when include_inline_policies is true).
            type: list
            returned: when include_inline_policies is true
        role_tags:
            description: List of role tags (when include_tags is true).
            type: list
            returned: when include_tags is true
    sample:
        [
            {
                "RoleName": "app-data-access-role",
                "RoleId": "AROA123",
                "Arn": "urn:ecs:iam::testns:role/app-data-access-role",
                "CreateDate": "2025-01-15T10:30:00Z",
                "Path": "/"
            }
        ]
'''

import json
from urllib.parse import unquote as url_decode

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi
except Exception:
    IamApi = None  # type: ignore[assignment,misc]


class IamRoleInfo(object):
    """Class for gathering IAM role information from ObjectScale."""

    def __init__(self):
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_role_info_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
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

        self.namespace = self.module.params.get('namespace_name')

    @staticmethod
    def get_iam_role_info_parameters():
        """Return dict of module-specific parameters."""
        return dict(
            role_name=dict(type='str', required=False, default=None),
            namespace_name=dict(type='str', required=True),
            include_attached_policies=dict(type='bool', required=False, default=False),
            include_inline_policies=dict(type='bool', required=False, default=False),
            inline_policy_name=dict(type='str', required=False, default=None),
            include_tags=dict(type='bool', required=False, default=False),
        )

    def get_role(self, role_name):
        """Get a single IAM role by name.

        Returns the role dict from the API response, or None if not found.
        On 404: returns None (role not found is a valid state for info modules).
        On other errors: calls module.fail_json.
        """
        try:
            # Use raw API call because the generated Pydantic model
            # can't properly deserialize the GetRoleResult.Role nested object
            from urllib.parse import urlencode
            base = self.iam_api.api_client.configuration.host
            qs = urlencode({'Action': 'GetRole', 'RoleName': role_name})
            url = f"{base}/iam?{qs}"
            headers = {}
            for key in ['AuthToken']:
                token = self.iam_api.api_client.configuration.api_key.get(key)
                if token:
                    headers['X-SDS-AUTH-TOKEN'] = token
            if self.namespace:
                headers['x-emc-namespace'] = self.namespace
            headers['Accept'] = 'application/json'
            resp = self.iam_api.api_client.rest_client.request('POST', url, headers=headers)
            resp.read()  # Ensure response data is available
            if resp.status >= 400:
                raw_err = json.loads(resp.data.decode('utf-8')) if resp.data else {}
                # Return None on 404 (role not found) - info modules should not fail
                if resp.status == 404 or 'NoSuchEntity' in str(raw_err):
                    return None
                raise RuntimeError(str(raw_err))
            raw = json.loads(resp.data.decode('utf-8'))
            return raw.get('GetRoleResult', {}).get('Role')
        except Exception as e:
            status = getattr(e, 'status', None)
            error_msg = utils.determine_error(e)
            # Return None on 404-like errors
            if status == 404 or 'NoSuchEntity' in str(e) or 'not found' in str(e).lower():
                return None
            # Fail on other errors
            self.module.fail_json(
                msg="Getting IAM role '%s' failed with error: %s" % (role_name, error_msg)
            )

    def list_all_roles(self):
        """List all IAM roles in the namespace with auto-pagination.

        Returns a list of role dicts.
        On error: calls module.fail_json.
        """
        try:
            all_roles = []
            marker = None
            while True:
                kwargs = dict(x_emc_namespace=self.namespace)
                if marker:
                    kwargs['marker'] = marker
                response = self.iam_api.iam_service_list_roles(**kwargs)
                result = response.to_dict()
                list_result = result['ListRolesResult']
                roles = list_result.get('Roles') or []
                all_roles.extend(roles)
                if list_result.get('IsTruncated'):
                    marker = list_result.get('Marker')
                else:
                    break
            return all_roles
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(
                msg="Listing IAM roles failed with error: %s" % error_msg
            )

    def enrich_role(self, role):
        """Enrich a role dict with optional detail based on include_* flags.

        On enrichment failure: embeds error in the field, warns, and continues.
        Returns the enriched role dict.
        """
        params = self.module.params
        role_name = role.get('RoleName')

        # Inline policies
        if params.get('include_inline_policies'):
            try:
                role['inline_policies'] = self.list_inline_policy_names(role_name)
            except Exception as e:
                role['inline_policies'] = {'error': str(e)}
                self.module.warn(
                    "Failed to list inline policies for role %s: %s" % (role_name, str(e))
                )

        # Inline policy document
        if params.get('inline_policy_name'):
            try:
                role['inline_policy_document'] = self.get_role_policy_document(
                    role_name, params['inline_policy_name']
                )
            except Exception as e:
                role['inline_policy_document'] = {'error': str(e)}
                self.module.warn(
                    "Failed to get inline policy document for role %s: %s" % (role_name, str(e))
                )

        # Attached policies
        if params.get('include_attached_policies'):
            try:
                role['attached_policies'] = self.list_attached_policies(role_name)
            except Exception as e:
                role['attached_policies'] = {'error': str(e)}
                self.module.warn(
                    "Failed to list attached policies for role %s: %s" % (role_name, str(e))
                )

        # Tags
        if params.get('include_tags'):
            try:
                role['role_tags'] = self.list_role_tags(role_name)
            except Exception as e:
                role['role_tags'] = {'error': str(e)}
                self.module.warn(
                    "Failed to list tags for role %s: %s" % (role_name, str(e))
                )

        return role

    def list_inline_policy_names(self, role_name):
        """List inline policy names for a role with auto-pagination.

        Returns a list of policy name strings.
        Lets exceptions propagate to caller.
        """
        all_names = []
        marker = None
        while True:
            kwargs = dict(role_name=role_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_role_policies(**kwargs)
            result = response.to_dict()
            list_result = result['ListRolePoliciesResult']
            names = list_result.get('PolicyNames') or []
            all_names.extend(names)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_names

    def get_role_policy_document(self, role_name, policy_name):
        """Get a specific inline policy document for a role.

        Returns the decoded JSON policy document as a dict.
        Lets exceptions propagate to caller.
        """
        response = self.iam_api.iam_service_get_role_policy(
            role_name=role_name,
            policy_name=policy_name,
            x_emc_namespace=self.namespace,
        )
        result = response.to_dict()
        encoded_doc = result['GetRolePolicyResult']['PolicyDocument']
        decoded_doc = url_decode(encoded_doc)
        try:
            return json.loads(decoded_doc)
        except (json.JSONDecodeError, ValueError):
            # Return raw decoded string if it's not valid JSON
            return decoded_doc

    def list_attached_policies(self, role_name):
        """List attached managed policies for a role with auto-pagination.

        Returns a list of attached policy dicts.
        Lets exceptions propagate to caller.
        """
        all_policies = []
        marker = None
        while True:
            kwargs = dict(role_name=role_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_attached_role_policies(**kwargs)
            result = response.to_dict()
            list_result = result['ListAttachedRolePoliciesResult']
            policies = list_result.get('AttachedPolicies') or []
            all_policies.extend(policies)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_policies

    def list_role_tags(self, role_name):
        """List tags for a role with auto-pagination.

        Returns a list of tag dicts.
        Lets exceptions propagate to caller.
        """
        all_tags = []
        marker = None
        while True:
            kwargs = dict(role_name=role_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_role_tags(**kwargs)
            result = response.to_dict()
            list_result = result['ListRoleTagsResult']
            tags = list_result.get('Tags') or []
            all_tags.extend(tags)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_tags

    def perform_module_operation(self):
        """Perform the main module operation.

        If role_name is provided, get a single role; otherwise list all roles.
        Enrich each role based on include_* flags.
        Always returns changed=False (read-only info module).
        """
        role_name = self.module.params.get('role_name')

        if role_name:
            role = self.get_role(role_name)
            roles = [role] if role else []
        else:
            roles = self.list_all_roles() or []

        enriched_roles = []
        for role in roles:
            enriched_roles.append(self.enrich_role(role))

        self.module.exit_json(changed=False, iam_roles=enriched_roles)


def main():
    """Create IamRoleInfo object and perform module operation."""
    obj = IamRoleInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
