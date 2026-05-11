#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering IAM user information from Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_user_info

version_added: '1.0.0'

short_description: Gather IAM user information from Dell ObjectScale

description:
- Gather information about IAM users on Dell ObjectScale.
- Can retrieve a single user by name or list all users in a namespace.
- Supports optional enrichment with access keys, inline policies, attached policies,
  group memberships, and user tags.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

extends_documentation_fragment:
- dellemc.objectscale.objectscale

options:
  user_name:
    description:
    - The name of the IAM user to retrieve.
    - If not specified, all users in the namespace are listed.
    type: str
    required: false

  namespace_name:
    description:
    - The ObjectScale namespace to query IAM users from.
    type: str
    required: true

  include_access_keys:
    description:
    - Whether to include access key metadata for each user.
    type: bool
    default: false
    required: false

  include_access_key_last_used:
    description:
    - Whether to include last-used information for each access key.
    - Requires I(include_access_keys) to also be set to C(true).
    type: bool
    default: false
    required: false

  include_inline_policies:
    description:
    - Whether to include inline policy names for each user.
    type: bool
    default: false
    required: false

  inline_policy_name:
    description:
    - Name of a specific inline policy to retrieve the document for.
    type: str
    required: false

  include_attached_policies:
    description:
    - Whether to include attached managed policies for each user.
    type: bool
    default: false
    required: false

  include_groups:
    description:
    - Whether to include group memberships for each user.
    type: bool
    default: false
    required: false

  include_tags:
    description:
    - Whether to include user tags for each user.
    type: bool
    default: false
    required: false

notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: List all IAM users in a namespace
  dellemc.objectscale.iam_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
  register: all_users

- name: Get a specific IAM user with access keys and tags
  dellemc.objectscale.iam_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
    user_name: "alice"
    include_access_keys: true
    include_tags: true
  register: user_info

- name: List all users with full enrichment
  dellemc.objectscale.iam_user_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
    include_access_keys: true
    include_access_key_last_used: true
    include_inline_policies: true
    include_attached_policies: true
    include_groups: true
    include_tags: true
  register: enriched_users
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed. Always false for info modules.
    returned: always
    type: bool
    sample: false

iam_users:
    description: List of IAM user dictionaries.
    returned: always
    type: list
    elements: dict
    contains:
        UserName:
            description: The friendly name of the user.
            type: str
        UserId:
            description: The unique identifier for the user.
            type: str
        Arn:
            description: The Amazon Resource Name (ARN) of the user.
            type: str
        CreateDate:
            description: The date and time the user was created.
            type: str
        Path:
            description: The path to the user.
            type: str
        access_keys:
            description: List of access key metadata (when include_access_keys is true).
            type: list
            returned: when include_access_keys is true
        inline_policies:
            description: List of inline policy names (when include_inline_policies is true).
            type: list
            returned: when include_inline_policies is true
        attached_policies:
            description: List of attached managed policies (when include_attached_policies is true).
            type: list
            returned: when include_attached_policies is true
        groups:
            description: List of group memberships (when include_groups is true).
            type: list
            returned: when include_groups is true
        user_tags:
            description: List of user tags (when include_tags is true).
            type: list
            returned: when include_tags is true
    sample:
        [
            {
                "UserName": "alice",
                "UserId": "AIDA123",
                "Arn": "urn:ecs:iam::testns:user/alice",
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


class IamUserInfo(object):
    """Class for gathering IAM user information from ObjectScale."""

    def __init__(self):
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_user_info_parameters())

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
    def get_iam_user_info_parameters():
        """Return dict of module-specific parameters."""
        return dict(
            user_name=dict(type='str', required=False, default=None),
            namespace_name=dict(type='str', required=True),
            include_access_keys=dict(type='bool', required=False, default=False),
            include_access_key_last_used=dict(type='bool', required=False, default=False),
            include_inline_policies=dict(type='bool', required=False, default=False),
            inline_policy_name=dict(type='str', required=False, default=None),
            include_attached_policies=dict(type='bool', required=False, default=False),
            include_groups=dict(type='bool', required=False, default=False),
            include_tags=dict(type='bool', required=False, default=False),
        )

    def get_user(self, user_name):
        """Get a single IAM user by name.

        Returns the user dict from the API response.
        On 404: calls module.fail_json (user must exist for info query).
        On other errors: calls module.fail_json.
        """
        try:
            response = self.iam_api.iam_service_get_user(
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            result = response.to_dict()
            return result['GetUserResult']['User']
        except Exception as e:
            status = getattr(e, 'status', None)
            error_msg = utils.determine_error(e)
            if status == 404:
                self.module.fail_json(
                    msg="User '%s' not found: %s" % (user_name, error_msg)
                )
            else:
                self.module.fail_json(
                    msg="Getting IAM user '%s' failed with error: %s" % (user_name, error_msg)
                )

    def list_all_users(self):
        """List all IAM users in the namespace with auto-pagination.

        Returns a list of user dicts.
        On error: calls module.fail_json.
        """
        try:
            all_users = []
            marker = None
            while True:
                kwargs = dict(x_emc_namespace=self.namespace)
                if marker:
                    kwargs['marker'] = marker
                response = self.iam_api.iam_service_list_users(**kwargs)
                result = response.to_dict()
                list_result = result['ListUsersResult']
                users = list_result.get('Users') or []
                all_users.extend(users)
                if list_result.get('IsTruncated'):
                    marker = list_result.get('Marker')
                else:
                    break
            return all_users
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(
                msg="Listing IAM users failed with error: %s" % error_msg
            )

    def _enrich_field(self, user, user_name, field, fetch_func, desc):
        """Enrich a single field on the user dict, handling errors gracefully."""
        try:
            user[field] = fetch_func(user_name)
        except Exception as e:
            user[field] = {'error': str(e)}
            self.module.warn(
                "Failed to %s for user %s: %s" % (desc, user_name, str(e))
            )

    def _enrich_access_keys(self, user, user_name):
        """Enrich user with access key data and optional last-used info."""
        try:
            keys = self.list_access_keys(user_name)
            if self.module.params.get('include_access_key_last_used'):
                for key in keys:
                    try:
                        key['last_used'] = self.get_access_key_last_used(key.get('AccessKeyId'))
                    except Exception as lu_err:
                        key['last_used'] = {'error': str(lu_err)}
                        self.module.warn(
                            "Failed to get last used info for access key %s: %s"
                            % (key.get('AccessKeyId'), str(lu_err))
                        )
            user['access_keys'] = keys
        except Exception as e:
            user['access_keys'] = {'error': str(e)}
            self.module.warn(
                "Failed to list access keys for user %s: %s" % (user_name, str(e))
            )

    def enrich_user(self, user):
        """Enrich a user dict with optional detail based on include_* flags.

        On enrichment failure: embeds error in the field, warns, and continues.
        Returns the enriched user dict.
        """
        params = self.module.params
        user_name = user.get('UserName')

        if params.get('include_access_keys'):
            self._enrich_access_keys(user, user_name)

        if params.get('include_inline_policies'):
            self._enrich_field(
                user, user_name, 'inline_policies',
                self.list_inline_policy_names, "list inline policies")

        if params.get('inline_policy_name'):
            policy_name = params['inline_policy_name']
            try:
                user['inline_policy_document'] = self.get_user_policy_document(
                    user_name, policy_name)
            except Exception as e:
                user['inline_policy_document'] = {'error': str(e)}
                self.module.warn(
                    "Failed to get inline policy document for user %s: %s"
                    % (user_name, str(e)))

        if params.get('include_attached_policies'):
            self._enrich_field(
                user, user_name, 'attached_policies',
                self.list_attached_policies, "list attached policies")

        if params.get('include_groups'):
            self._enrich_field(
                user, user_name, 'groups',
                self.list_groups_for_user, "list groups")

        if params.get('include_tags'):
            self._enrich_field(
                user, user_name, 'user_tags',
                self.list_user_tags, "list tags")

        return user

    def list_access_keys(self, user_name):
        """List access keys for a user with auto-pagination.

        Returns a list of access key metadata dicts.
        Lets exceptions propagate to caller (enrich_user handles them).
        """
        all_keys = []
        marker = None
        while True:
            kwargs = dict(user_name=user_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_access_keys(**kwargs)
            result = response.to_dict()
            list_result = result['ListAccessKeysResult']
            keys = list_result.get('AccessKeyMetadata') or []
            all_keys.extend(keys)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_keys

    def get_access_key_last_used(self, access_key_id):
        """Get last-used information for an access key.

        Returns the last-used details dict.
        Lets exceptions propagate to caller.
        """
        response = self.iam_api.iam_service_get_access_key_last_used(
            access_key_id=access_key_id,
            x_emc_namespace=self.namespace,
        )
        result = response.to_dict()
        return result['GetAccessKeyLastUsedResult']['AccessKeyLastUsed']

    def list_inline_policy_names(self, user_name):
        """List inline policy names for a user with auto-pagination.

        Returns a list of policy name strings.
        Lets exceptions propagate to caller.
        """
        all_names = []
        marker = None
        while True:
            kwargs = dict(user_name=user_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_user_policies(**kwargs)
            result = response.to_dict()
            list_result = result['ListUserPoliciesResult']
            names = list_result.get('PolicyNames') or []
            all_names.extend(names)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_names

    def get_user_policy_document(self, user_name, policy_name):
        """Get a specific inline policy document for a user.

        Returns the decoded JSON policy document as a dict.
        Lets exceptions propagate to caller.
        """
        response = self.iam_api.iam_service_get_user_policy(
            user_name=user_name,
            policy_name=policy_name,
            x_emc_namespace=self.namespace,
        )
        result = response.to_dict()
        encoded_doc = result['GetUserPolicyResult']['PolicyDocument']
        decoded_doc = url_decode(encoded_doc)
        try:
            return json.loads(decoded_doc)
        except ValueError:
            # Return raw decoded string if it's not valid JSON
            return decoded_doc

    def list_attached_policies(self, user_name):
        """List attached managed policies for a user with auto-pagination.

        Returns a list of attached policy dicts.
        Lets exceptions propagate to caller.
        """
        all_policies = []
        marker = None
        while True:
            kwargs = dict(user_name=user_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_attached_user_policies(**kwargs)
            result = response.to_dict()
            list_result = result['ListAttachedUserPoliciesResult']
            policies = list_result.get('AttachedPolicies') or []
            all_policies.extend(policies)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_policies

    def list_groups_for_user(self, user_name):
        """List groups for a user with auto-pagination.

        Returns a list of group dicts.
        Lets exceptions propagate to caller.
        """
        all_groups = []
        marker = None
        while True:
            kwargs = dict(user_name=user_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_groups_for_user(**kwargs)
            result = response.to_dict()
            list_result = result['ListGroupsForUserResult']
            groups = list_result.get('Groups') or []
            all_groups.extend(groups)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_groups

    def list_user_tags(self, user_name):
        """List tags for a user with auto-pagination.

        Returns a list of tag dicts.
        Lets exceptions propagate to caller.
        """
        all_tags = []
        marker = None
        while True:
            kwargs = dict(user_name=user_name, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_user_tags(**kwargs)
            result = response.to_dict()
            list_result = result['ListUserTagsResult']
            tags = list_result.get('Tags') or []
            all_tags.extend(tags)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_tags

    def perform_module_operation(self):
        """Perform the main module operation.

        If user_name is provided, get a single user; otherwise list all users.
        Enrich each user based on include_* flags.
        Always returns changed=False (read-only info module).
        """
        user_name = self.module.params.get('user_name')

        if user_name:
            user = self.get_user(user_name)
            users = [user] if user else []
        else:
            users = self.list_all_users() or []

        enriched_users = []
        for user in users:
            enriched_users.append(self.enrich_user(user))

        self.module.exit_json(changed=False, iam_users=enriched_users)


def main():
    """Create IamUserInfo object and perform module operation."""
    obj = IamUserInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
