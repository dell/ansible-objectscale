#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM (S3) policies on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_policy

version_added: '1.0.0'

short_description: Manages IAM (S3) policies on Dell ObjectScale

description:
- Manages IAM (S3) managed policies on the Dell ObjectScale storage system.
  This includes creating, modifying (via policy versions), deleting, and retrieving
  details of IAM policies. Also supports attaching and detaching policies to/from
  IAM users, groups, and roles.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

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

  policy_name:
    description:
    - The friendly name of the IAM policy.
    - Required when creating a new policy.
    - Used to construct the policy ARN if I(policy_arn) is not provided.
    type: str

  policy_arn:
    description:
    - The Amazon Resource Name (ARN) of the IAM policy.
    - Used to identify an existing policy for get, update, delete, attach, and detach operations.
    - Takes precedence over I(policy_name) for identifying existing policies.
    type: str

  policy_document:
    description:
    - The JSON policy document that defines the permissions for the policy.
    - Must be a valid JSON string.
    - Required when creating a new policy (C(state=present) and policy does not exist).
    - When provided for an existing policy, a new policy version is created with the
      updated document and set as the default version.
    type: json

  description:
    description:
    - A friendly description for the policy.
    - Only used during policy creation.
    type: str

  path:
    description:
    - The path for the policy.
    - Defaults to "/" and only "/" is supported.
    type: str
    default: "/"

  namespace_name:
    description:
    - The ObjectScale namespace (ECS namespace) that the IAM entity belongs to.
    - Required when the request is performed by a management user.
    type: str

  attach_entities:
    description:
    - List of entities to attach the policy to.
    - Each entity must have I(entity_type) and I(entity_name).
    type: list
    elements: dict
    suboptions:
      entity_type:
        description:
        - Type of the IAM entity.
        type: str
        required: true
        choices: ['user', 'group', 'role']
      entity_name:
        description:
        - Name of the IAM entity.
        type: str
        required: true

  detach_entities:
    description:
    - List of entities to detach the policy from.
    - Each entity must have I(entity_type) and I(entity_name).
    type: list
    elements: dict
    suboptions:
      entity_type:
        description:
        - Type of the IAM entity.
        type: str
        required: true
        choices: ['user', 'group', 'role']
      entity_name:
        description:
        - Name of the IAM entity.
        type: str
        required: true

  state:
    description:
    - The desired state of the IAM policy.
    - C(present) ensures the policy exists.
    - C(absent) ensures the policy is deleted.
    choices: ['present', 'absent']
    type: str
    required: true

notes:
- The I(check_mode) is supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client) and install with C(make install_client).
'''

EXAMPLES = r'''
- name: Create an IAM policy with S3 read-only access
  dellemc.objectscale.iam_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "{{ namespace_name }}"
    policy_name: "S3ReadOnlyPolicy"
    policy_document: |
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": "*"
          }
        ]
      }
    description: "Grants read-only access to S3 buckets"
    state: present

- name: Attach a policy to a user, group, and role
  dellemc.objectscale.iam_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "{{ namespace_name }}"
    policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
    attach_entities:
      - entity_type: user
        entity_name: alice
      - entity_type: group
        entity_name: developers
      - entity_type: role
        entity_name: s3-readonly-role
    state: present

- name: Update the policy document (creates a new version)
  dellemc.objectscale.iam_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "{{ namespace_name }}"
    policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
    policy_document: |
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket", "s3:GetBucketLocation"],
            "Resource": "*"
          }
        ]
      }
    state: present

- name: Detach a policy from a user, group, and role
  dellemc.objectscale.iam_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "{{ namespace_name }}"
    policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
    detach_entities:
      - entity_type: user
        entity_name: alice
      - entity_type: group
        entity_name: developers
      - entity_type: role
        entity_name: s3-readonly-role
    state: present

- name: Delete an IAM policy
  dellemc.objectscale.iam_policy:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace_name: "{{ namespace_name }}"
    policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
    state: absent
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: false

policy_details:
    description: IAM policy details.
    returned: When a policy exists
    type: dict
    contains:
        Arn:
            description: The Amazon Resource Name (ARN) of the policy.
            type: str
        PolicyId:
            description: Unique stable identifier of the policy.
            type: str
        PolicyName:
            description: Friendly name of the policy.
            type: str
        Description:
            description: Friendly description of the policy.
            type: str
        Path:
            description: Path of the policy.
            type: str
        DefaultVersionId:
            description: Identifier of the default policy version.
            type: str
        AttachmentCount:
            description: Number of entities the policy is attached to.
            type: int
        IsAttachable:
            description: Whether the policy can be attached to entities.
            type: bool
        CreateDate:
            description: ISO 8601 creation timestamp.
            type: str
        UpdateDate:
            description: ISO 8601 last update timestamp.
            type: str
    sample:
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
'''

import json
import urllib.parse
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi
except ImportError:
    pass


class IamPolicy(object):
    """Class with operations on ObjectScale IAM managed policies."""

    def __init__(self) -> None:
        """Define all parameters required by this module and initialize API connection."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_policy_parameters())

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

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.iam_api: IamApi = IamApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))

        self.module.log('Connected to ObjectScale at %s' % self.module.params['objectscale_host'])

    def get_policy_details(self, policy_arn: str) -> Optional[Dict[str, Any]]:
        """Get the details of an IAM managed policy by ARN.

        Returns policy details dict on success, None if not found (404/400).
        """
        try:
            self.module.log('Getting IAM policy details for ARN: %s' % policy_arn)
            response = self.iam_api.iam_service_get_policy(
                policy_arn=policy_arn,
                x_emc_namespace=self.module.params.get('namespace_name'),
            )
            return response.to_dict()
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            msg = "Getting IAM policy %s details failed with error: %s" % (policy_arn, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def create_policy(self, policy_name: str, policy_document: str,
                      description: Optional[str] = None, path: str = '/') -> Optional[Dict[str, Any]]:
        """Create a new IAM managed policy. Returns the created policy response dict."""
        if not policy_name:
            self.module.exit_json(
                failed=True,
                msg="policy_name is required when creating a new policy."
            )
            return None

        if not policy_document:
            self.module.exit_json(
                failed=True,
                msg="policy_document is required when creating a new policy."
            )
            return None

        try:
            self.module.log('Creating IAM policy: %s' % policy_name)
            response = self.iam_api.iam_service_create_policy(
                policy_name=policy_name,
                policy_document=policy_document,
                description=description,
                path=path,
                x_emc_namespace=self.module.params.get('namespace_name'),
            )
            return response.to_dict()
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating IAM policy %s failed with error: %s" % (policy_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def delete_policy(self, policy_arn: str) -> Optional[bool]:
        """Delete an IAM managed policy by ARN. Returns True on success."""
        try:
            self.module.log('Deleting IAM policy: %s' % policy_arn)
            self.iam_api.iam_service_delete_policy(
                policy_arn=policy_arn,
                x_emc_namespace=self.module.params.get('namespace_name'),
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Deleting IAM policy %s failed with error: %s" % (policy_arn, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def get_policy_version(self, policy_arn: str, version_id: str) -> Optional[Dict[str, Any]]:
        """Get the policy version details including the document.

        Returns the version response dict, or None if not found.
        """
        try:
            response = self.iam_api.iam_service_get_policy_version(
                policy_arn=policy_arn,
                version_id=version_id,
                x_emc_namespace=self.module.params.get('namespace_name'),
            )
            return response.to_dict()
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            msg = "Getting policy version %s for %s failed with error: %s" % (version_id, policy_arn, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def create_policy_version(self, policy_arn: str, policy_document: str,
                              set_as_default: bool = True) -> Optional[bool]:
        """Create a new version of an IAM policy with the given document.

        Optionally sets it as the default version. Returns True on success.
        """
        try:
            self.module.log('Creating new policy version for: %s' % policy_arn)
            self.iam_api.iam_service_create_policy_version(
                policy_arn=policy_arn,
                policy_document=policy_document,
                set_as_default=set_as_default,
                x_emc_namespace=self.module.params.get('namespace_name'),
            )
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating policy version for %s failed with error: %s" % (policy_arn, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def attach_entity(self, policy_arn: str, entity_type: str, entity_name: str) -> Optional[bool]:
        """Attach policy to an IAM entity (user, group, or role). Returns True on success."""
        try:
            self.module.log('Attaching policy %s to %s: %s' % (policy_arn, entity_type, entity_name))
            ns = self.module.params.get('namespace_name')
            if entity_type == 'user':
                self.iam_api.iam_service_attach_user_policy(
                    policy_arn=policy_arn, user_name=entity_name, x_emc_namespace=ns)
            elif entity_type == 'group':
                self.iam_api.iam_service_attach_group_policy(
                    policy_arn=policy_arn, group_name=entity_name, x_emc_namespace=ns)
            elif entity_type == 'role':
                self.iam_api.iam_service_attach_role_policy(
                    policy_arn=policy_arn, role_name=entity_name, x_emc_namespace=ns)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Attaching policy %s to %s %s failed with error: %s" % (
                policy_arn, entity_type, entity_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def detach_entity(self, policy_arn: str, entity_type: str, entity_name: str) -> Optional[bool]:
        """Detach policy from an IAM entity (user, group, or role). Returns True on success."""
        try:
            self.module.log('Detaching policy %s from %s: %s' % (policy_arn, entity_type, entity_name))
            ns = self.module.params.get('namespace_name')
            if entity_type == 'user':
                self.iam_api.iam_service_detach_user_policy(
                    policy_arn=policy_arn, user_name=entity_name, x_emc_namespace=ns)
            elif entity_type == 'group':
                self.iam_api.iam_service_detach_group_policy(
                    policy_arn=policy_arn, group_name=entity_name, x_emc_namespace=ns)
            elif entity_type == 'role':
                self.iam_api.iam_service_detach_role_policy(
                    policy_arn=policy_arn, role_name=entity_name, x_emc_namespace=ns)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Detaching policy %s from %s %s failed with error: %s" % (
                policy_arn, entity_type, entity_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)

    def validate_policy_document(self, document: str) -> None:
        """Validate that the policy document is valid JSON. Calls fail_json if invalid."""
        if not document or not document.strip():
            self.module.exit_json(
                failed=True,
                msg="policy_document must not be empty."
            )
            return
        try:
            json.loads(document)
        except (json.JSONDecodeError, ValueError) as e:
            self.module.exit_json(
                failed=True,
                msg="policy_document must be a valid JSON string: %s" % str(e)
            )

    @staticmethod
    def _normalize_policy_value(value: Union[str, List[str]]) -> List[str]:
        """Normalize a policy field value to a sorted list.

        The ObjectScale API normalises single-string Action/Resource values
        into single-element arrays.  This helper ensures both sides of a
        comparison use the same representation.
        """
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return sorted(value)
        return value

    @classmethod
    def _normalize_policy_doc(cls, doc: Any) -> Any:
        """Recursively normalise an IAM policy document for comparison.

        Converts Action, NotAction, Resource, and NotResource fields from
        strings to single-element lists so that documents differing only in
        that representation are considered equal.
        """
        if isinstance(doc, dict):
            normalised = {}
            for key, val in doc.items():
                if key in ('Action', 'NotAction', 'Resource', 'NotResource'):
                    normalised[key] = cls._normalize_policy_value(val)
                else:
                    normalised[key] = cls._normalize_policy_doc(val)
            return normalised
        if isinstance(doc, list):
            return [cls._normalize_policy_doc(item) for item in doc]
        return doc

    def is_policy_document_modified(self, policy_arn: str, current_details: Dict[str, Any],
                                    new_document: str) -> bool:
        """Check if the policy document has changed by comparing current default version
        document with the new document. Returns True if different."""
        default_version_id = current_details.get('DefaultVersionId')
        if not default_version_id:
            return True

        version_resp = self.get_policy_version(policy_arn, default_version_id)
        if not version_resp:
            return True

        version_result = version_resp.get('GetPolicyVersionResult', {})
        policy_version = version_result.get('PolicyVersion', {})
        current_document = policy_version.get('Document', '')

        # The ObjectScale API returns the document URL-encoded (RFC 3986).
        if isinstance(current_document, str):
            current_document = urllib.parse.unquote(current_document)

        try:
            current_parsed = json.loads(current_document) if isinstance(current_document, str) else current_document
            new_parsed = json.loads(new_document) if isinstance(new_document, str) else new_document
            return self._normalize_policy_doc(current_parsed) != self._normalize_policy_doc(new_parsed)
        except (json.JSONDecodeError, ValueError):
            return current_document != new_document

    def _resolve_policy_arn(self) -> Optional[str]:
        """Resolve the policy ARN from module parameters."""
        policy_arn = self.module.params.get('policy_arn')
        if policy_arn:
            return policy_arn

        policy_name = self.module.params.get('policy_name')
        namespace_name = self.module.params.get('namespace_name')
        if policy_name and namespace_name:
            return 'urn:ecs:iam::%s:policy/%s' % (namespace_name, policy_name)
        elif policy_name:
            return policy_name

        return None

    def _extract_policy(self, response_dict: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract the Policy object from various API response formats."""
        if not response_dict:
            return None

        for result_key in ('GetPolicyResult', 'CreatePolicyResult'):
            result = response_dict.get(result_key)
            if result and isinstance(result, dict):
                policy = result.get('Policy')
                if policy:
                    return policy

        if 'Arn' in response_dict or 'PolicyName' in response_dict:
            return response_dict

        return response_dict

    def _validate_params(self) -> None:
        """Validate module parameters. Calls exit_json on failure."""
        policy_name = self.module.params.get('policy_name')
        if not policy_name and not self.module.params.get('policy_arn'):
            self.module.exit_json(
                failed=True,
                msg="policy_name or policy_arn is required."
            )
            return
        if policy_name is not None and not policy_name.strip():
            self.module.exit_json(
                failed=True,
                msg="policy_name must not be empty."
            )

    def _handle_absent(self, policy_arn: str,
                       policy_details: Optional[Dict[str, Any]],
                       result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle state=absent logic. Returns updated policy_details."""
        if policy_details:
            if not self.module.check_mode:
                self.delete_policy(policy_arn)
                self.module.log('Deleted IAM policy: %s' % policy_arn)
            result['changed'] = True
            return None
        self.module.log('Policy %s not found, nothing to delete' % policy_arn)
        return None

    def _handle_present_create(self, policy_arn: str,
                               result: Dict[str, Any]) -> tuple:
        """Handle creating a new policy. Returns (policy_details, policy_arn)."""
        policy_name = self.module.params.get('policy_name')
        policy_document = self.module.params.get('policy_document')
        description = self.module.params.get('description')
        path = self.module.params.get('path', '/')

        if not policy_document:
            self.module.exit_json(
                failed=True,
                msg="policy_document is required when creating a new policy."
            )
            return None, policy_arn
        if not policy_name:
            self.module.exit_json(
                failed=True,
                msg="policy_name is required when creating a new policy."
            )
            return None, policy_arn

        policy_details = None
        if not self.module.check_mode:
            create_resp = self.create_policy(policy_name, policy_document, description, path)
            policy_details = self._extract_policy(create_resp)
            policy_arn = policy_details.get('Arn') if policy_details else policy_arn
        result['changed'] = True
        return policy_details, policy_arn

    def _handle_present_update(self, policy_arn: str,
                               policy_details: Dict[str, Any],
                               result: Dict[str, Any]) -> None:
        """Handle updating an existing policy's document."""
        policy_document = self.module.params.get('policy_document')
        if not policy_document:
            return

        self.module.log('Policy %s already exists, checking for modifications' % policy_arn)
        if self.is_policy_document_modified(policy_arn, policy_details, policy_document):
            self.module.log('Policy document update detected for: %s' % policy_arn)
            if not self.module.check_mode:
                self.create_policy_version(policy_arn, policy_document, set_as_default=True)
            result['changed'] = True
        else:
            self.module.log('Policy document unchanged, no version update needed')

    def _process_entities(self, policy_arn: str, result: Dict[str, Any]) -> None:
        """Process attach and detach entity lists."""
        attach_entities = self.module.params.get('attach_entities') or []
        detach_entities = self.module.params.get('detach_entities') or []

        if not self.module.check_mode:
            for entity in attach_entities:
                self.attach_entity(policy_arn, entity['entity_type'], entity['entity_name'])
                result['changed'] = True
            for entity in detach_entities:
                self.detach_entity(policy_arn, entity['entity_type'], entity['entity_name'])
                result['changed'] = True
        else:
            if attach_entities or detach_entities:
                result['changed'] = True

    def perform_module_operation(self) -> None:
        """Perform different actions based on parameters chosen in playbook.

        Main handler orchestrating the full policy lifecycle.
        """
        result: Dict[str, Any] = dict(changed=False, policy_details=None)
        state = self.module.params['state']
        policy_document = self.module.params.get('policy_document')

        self._validate_params()

        policy_arn = self._resolve_policy_arn()
        if policy_document:
            self.validate_policy_document(policy_document)

        policy_details_raw = self.get_policy_details(policy_arn) if policy_arn else None
        policy_details = self._extract_policy(policy_details_raw)
        before_state = policy_details.copy() if policy_details else None

        if state == 'absent':
            policy_details = self._handle_absent(policy_arn, policy_details, result)
        elif state == 'present':
            if not policy_details:
                policy_details, policy_arn = self._handle_present_create(policy_arn, result)
            else:
                self._handle_present_update(policy_arn, policy_details, result)
            self._process_entities(policy_arn, result)
            if result['changed'] and not self.module.check_mode and policy_arn:
                refreshed = self.get_policy_details(policy_arn)
                policy_details = self._extract_policy(refreshed)

        result['policy_details'] = policy_details
        if self.module._diff:
            after_state = policy_details.copy() if policy_details else None
            result['diff'] = {'before': before_state, 'after': after_state}

        self.module.exit_json(**result)

    @staticmethod
    def get_iam_policy_parameters() -> Dict[str, Dict[str, Any]]:
        """Return the argument specification dictionary for the iam_policy module."""
        entity_spec = dict(
            entity_type=dict(type='str', required=True, choices=['user', 'group', 'role']),
            entity_name=dict(type='str', required=True),
        )
        return dict(
            policy_name=dict(type='str'),
            policy_arn=dict(type='str'),
            policy_document=dict(type='json'),
            description=dict(type='str'),
            path=dict(type='str', default='/'),
            namespace_name=dict(type='str'),
            attach_entities=dict(
                type='list', elements='dict',
                options=entity_spec,
            ),
            detach_entities=dict(
                type='list', elements='dict',
                options=entity_spec,
            ),
            state=dict(required=True, type='str', choices=['present', 'absent']),
        )


def main() -> None:
    """Create ObjectScale IAM Policy object and perform actions on it."""
    obj = IamPolicy()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
