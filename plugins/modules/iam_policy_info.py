#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for gathering IAM policy information from Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_policy_info

version_added: '1.0.0'

short_description: Gather IAM policy information from Dell ObjectScale

description:
- Gather information about IAM managed policies on Dell ObjectScale.
- Can retrieve a single policy by ARN or name, or list all policies in a namespace.
- Supports optional enrichment with policy versions and the default policy document.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

extends_documentation_fragment:
- dellemc.objectscale.objectscale

options:
  policy_name:
    description:
    - The friendly name of the IAM policy to retrieve.
    - Used to construct the policy ARN if I(policy_arn) is not provided.
    type: str
    required: false

  policy_arn:
    description:
    - The Amazon Resource Name (ARN) of the IAM policy to retrieve.
    - Takes precedence over I(policy_name) for identifying a specific policy.
    type: str
    required: false

  namespace_name:
    description:
    - The ObjectScale namespace to query IAM policies from.
    type: str
    required: true

  include_policy_document:
    description:
    - Whether to include the default version policy document for each policy.
    type: bool
    default: false
    required: false

  include_versions:
    description:
    - Whether to include the list of policy versions for each policy.
    type: bool
    default: false
    required: false

  policy_scope:
    description:
    - The scope to use for filtering the results when listing all policies.
    - One of C(All), C(ECS), C(AWS), C(Local).
    type: str
    required: false
    choices: ['All', 'ECS', 'AWS', 'Local']

  only_attached:
    description:
    - A flag to filter the results to only the attached policies.
    type: bool
    default: false
    required: false

notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: List all IAM policies in a namespace
  dellemc.objectscale.iam_policy_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
  register: all_policies

- name: Get a specific IAM policy by ARN
  dellemc.objectscale.iam_policy_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
    policy_arn: "urn:ecs:iam::mynamespace:policy/S3ReadOnlyPolicy"
  register: policy_info

- name: Get a specific IAM policy by name with document and versions
  dellemc.objectscale.iam_policy_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
    policy_name: "S3ReadOnlyPolicy"
    include_policy_document: true
    include_versions: true
  register: enriched_policy

- name: List only attached policies in a namespace
  dellemc.objectscale.iam_policy_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "mynamespace"
    only_attached: true
  register: attached_policies
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed. Always false for info modules.
    returned: always
    type: bool
    sample: false

iam_policies:
    description: List of IAM policy dictionaries.
    returned: always
    type: list
    elements: dict
    contains:
        Arn:
            description: The Amazon Resource Name (ARN) of the policy.
            type: str
        PolicyId:
            description: The unique identifier for the policy.
            type: str
        PolicyName:
            description: The friendly name of the policy.
            type: str
        Description:
            description: The description of the policy.
            type: str
        Path:
            description: The path to the policy.
            type: str
        DefaultVersionId:
            description: The identifier for the default version of the policy.
            type: str
        AttachmentCount:
            description: The number of entities the policy is attached to.
            type: int
        IsAttachable:
            description: Whether the policy can be attached to entities.
            type: bool
        CreateDate:
            description: The date and time the policy was created.
            type: str
        UpdateDate:
            description: The date and time the policy was last updated.
            type: str
        policy_document:
            description: The default version policy document (when include_policy_document is true).
            type: dict
            returned: when include_policy_document is true
        versions:
            description: List of policy version dicts (when include_versions is true).
            type: list
            returned: when include_versions is true
    sample:
        [
            {
                "Arn": "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy",
                "PolicyId": "ANPA1234567890",
                "PolicyName": "S3ReadOnlyPolicy",
                "Description": "Grants read-only access to S3 buckets",
                "Path": "/",
                "DefaultVersionId": "v1",
                "AttachmentCount": 2,
                "IsAttachable": true,
                "CreateDate": "2025-01-15T10:30:00Z",
                "UpdateDate": "2025-01-15T10:30:00Z"
            }
        ]
'''

import json
import urllib.parse

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi
except Exception:
    IamApi = None  # type: ignore[assignment,misc]


class IamPolicyInfo(object):
    """Class for gathering IAM policy information from ObjectScale."""

    def __init__(self):
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_policy_info_parameters())

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
    def get_iam_policy_info_parameters():
        """Return dict of module-specific parameters."""
        return dict(
            policy_name=dict(type='str', required=False, default=None),
            policy_arn=dict(type='str', required=False, default=None),
            namespace_name=dict(type='str', required=True),
            include_policy_document=dict(type='bool', required=False, default=False),
            include_versions=dict(type='bool', required=False, default=False),
            policy_scope=dict(type='str', required=False, default=None,
                              choices=['All', 'ECS', 'AWS', 'Local']),
            only_attached=dict(type='bool', required=False, default=False),
        )

    def _resolve_policy_arn(self):
        """Resolve the policy ARN from module parameters."""
        policy_arn = self.module.params.get('policy_arn')
        if policy_arn:
            return policy_arn

        policy_name = self.module.params.get('policy_name')
        if policy_name:
            return 'urn:ecs:iam::%s:policy/%s' % (self.namespace, policy_name)

        return None

    def get_policy(self, policy_arn):
        """Get a single IAM policy by ARN.

        Returns the policy dict from the API response.
        On 404/400: calls module.fail_json (policy must exist for info query).
        On other errors: calls module.fail_json.
        """
        try:
            response = self.iam_api.iam_service_get_policy(
                policy_arn=policy_arn,
                x_emc_namespace=self.namespace,
            )
            result = response.to_dict()
            return result.get('GetPolicyResult', {}).get('Policy', result)
        except Exception as e:
            status = getattr(e, 'status', None)
            error_msg = utils.determine_error(e)
            if str(status) in ('404', '400'):
                self.module.fail_json(
                    msg="Policy '%s' not found: %s" % (policy_arn, error_msg)
                )
            else:
                self.module.fail_json(
                    msg="Getting IAM policy '%s' failed with error: %s" % (policy_arn, error_msg)
                )

    def list_all_policies(self):
        """List all IAM policies in the namespace with auto-pagination.

        Returns a list of policy dicts.
        On error: calls module.fail_json.
        """
        try:
            all_policies = []
            marker = None
            while True:
                kwargs = dict(x_emc_namespace=self.namespace)
                if marker:
                    kwargs['marker'] = marker
                policy_scope = self.module.params.get('policy_scope')
                if policy_scope:
                    kwargs['policy_scope'] = policy_scope
                if self.module.params.get('only_attached'):
                    kwargs['only_attached'] = True
                response = self.iam_api.iam_service_list_policies(**kwargs)
                result = response.to_dict()
                list_result = result.get('ListPoliciesResult', {})
                policies = list_result.get('Policies') or []
                all_policies.extend(policies)
                if list_result.get('IsTruncated'):
                    marker = list_result.get('Marker')
                else:
                    break
            return all_policies
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.fail_json(
                msg="Listing IAM policies failed with error: %s" % error_msg
            )

    def get_policy_version_document(self, policy_arn, version_id):
        """Get the policy document for a specific version.

        Returns the decoded JSON policy document as a dict.
        Lets exceptions propagate to caller (enrich_policy handles them).
        """
        response = self.iam_api.iam_service_get_policy_version(
            policy_arn=policy_arn,
            version_id=version_id,
            x_emc_namespace=self.namespace,
        )
        result = response.to_dict()
        version_result = result.get('GetPolicyVersionResult', {})
        policy_version = version_result.get('PolicyVersion', {})
        encoded_doc = policy_version.get('Document', '')

        if isinstance(encoded_doc, str):
            encoded_doc = urllib.parse.unquote(encoded_doc)

        try:
            return json.loads(encoded_doc)
        except (json.JSONDecodeError, ValueError):
            return encoded_doc

    def list_policy_versions(self, policy_arn):
        """List all versions for a policy with auto-pagination.

        Returns a list of version dicts.
        Lets exceptions propagate to caller (enrich_policy handles them).
        """
        all_versions = []
        marker = None
        while True:
            kwargs = dict(policy_arn=policy_arn, x_emc_namespace=self.namespace)
            if marker:
                kwargs['marker'] = marker
            response = self.iam_api.iam_service_list_policy_versions(**kwargs)
            result = response.to_dict()
            list_result = result.get('ListPolicyVersionsResult', {})
            versions = list_result.get('Versions') or []
            all_versions.extend(versions)
            if list_result.get('IsTruncated'):
                marker = list_result.get('Marker')
            else:
                break
        return all_versions

    def enrich_policy(self, policy):
        """Enrich a policy dict with optional detail based on include_* flags.

        On enrichment failure: embeds error in the field, warns, and continues.
        Returns the enriched policy dict.
        """
        params = self.module.params
        policy_arn = policy.get('Arn')

        # Policy document
        if params.get('include_policy_document'):
            try:
                version_id = policy.get('DefaultVersionId')
                if version_id and policy_arn:
                    policy['policy_document'] = self.get_policy_version_document(
                        policy_arn, version_id
                    )
                else:
                    policy['policy_document'] = None
            except Exception as e:
                policy['policy_document'] = {'error': str(e)}
                self.module.warn(
                    "Failed to get policy document for %s: %s" % (policy_arn, str(e))
                )

        # Versions
        if params.get('include_versions'):
            try:
                if policy_arn:
                    policy['versions'] = self.list_policy_versions(policy_arn)
                else:
                    policy['versions'] = []
            except Exception as e:
                policy['versions'] = {'error': str(e)}
                self.module.warn(
                    "Failed to list versions for %s: %s" % (policy_arn, str(e))
                )

        return policy

    def perform_module_operation(self):
        """Perform the main module operation.

        If policy_arn or policy_name is provided, get a single policy;
        otherwise list all policies.
        Enrich each policy based on include_* flags.
        Always returns changed=False (read-only info module).
        """
        policy_arn = self._resolve_policy_arn()

        if policy_arn:
            policy = self.get_policy(policy_arn)
            policies = [policy] if policy else []
        else:
            policies = self.list_all_policies() or []

        enriched_policies = []
        for policy in policies:
            enriched_policies.append(self.enrich_policy(policy))

        self.module.exit_json(changed=False, iam_policies=enriched_policies)


def main():
    """Create IamPolicyInfo object and perform module operation."""
    obj = IamPolicyInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
