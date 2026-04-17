#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM user access keys on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_user_access_key

version_added: '1.0.0'

short_description: Manages IAM user access keys on Dell ObjectScale

description:
- Manages IAM user S3-compatible access keys on the Dell ObjectScale storage system.
- Supports creating a new access key, updating the status of an existing key
  (Active/Inactive), and deleting an access key.
- Creating a key returns a C(secret_access_key) that is only available at creation time.
  Subsequent operations on the same key will never return the secret value.
- Supports C(check_mode) and C(diff) mode.

extends_documentation_fragment:
  - dellemc.objectscale.objectscale

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

options:
  user_name:
    description:
    - Name of the IAM user to which the access key belongs.
    type: str
    required: true

  namespace_name:
    description:
    - The ObjectScale namespace that owns the IAM user.
    type: str
    required: true

  access_key_id:
    description:
    - Identifier of an existing access key to update or delete.
    - Required when I(state=absent) and when updating I(status) of an
      existing key with I(state=present).
    - When omitted with I(state=present), a new access key is created.
    type: str
    required: false

  status:
    description:
    - Desired status of the access key.
    - Only applicable for updates of existing keys. New keys are always
      created in C(Active) state by the server.
    choices: ['Active', 'Inactive']
    type: str
    required: false

  state:
    description:
    - The desired state of the access key.
    - C(present) - the access key should exist. Creates a new key when
      I(access_key_id) is not supplied, or updates the status of an
      existing key when I(access_key_id) is supplied.
    - C(absent) - the access key identified by I(access_key_id) should
      not exist. The operation is idempotent.
    choices: ['present', 'absent']
    type: str
    default: present

notes:
- Creation is not idempotent by itself; each run with I(state=present)
  and no I(access_key_id) creates a new access key. To manage an
  existing key idempotently, always supply I(access_key_id).
- The C(secret_access_key) value is returned only on creation and is
  marked C(no_log). It is never logged, surfaced in diff output, or
  returned on update/delete operations.
- The I(check_mode) and I(diff) modes are supported.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client).
'''

EXAMPLES = r'''
- name: Create a new access key for an IAM user
  dellemc.objectscale.iam_user_access_key:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: sample_user_1
    namespace_name: ns1
    state: present
  register: access_key_result
  no_log: true

- name: Update access key status to Inactive
  dellemc.objectscale.iam_user_access_key:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: sample_user_1
    namespace_name: ns1
    access_key_id: "{{ access_key_result.access_key.AccessKeyId }}"
    status: Inactive
    state: present

- name: Delete an access key
  dellemc.objectscale.iam_user_access_key:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: sample_user_1
    namespace_name: ns1
    access_key_id: AKIA80817B9F1F4C72CB
    state: absent
'''

RETURN = r'''
changed:
    description: Whether any change was made.
    returned: always
    type: bool
    sample: true

access_key:
    description:
    - The access key metadata.
    - On creation, contains C(SecretAccessKey); on update and on
      subsequent operations the secret is never returned.
    returned: when state=present and the key exists or was created
    type: dict
    contains:
        AccessKeyId:
            description: The access key identifier.
            type: str
        UserName:
            description: The IAM user the access key belongs to.
            type: str
        Status:
            description: The status of the access key (Active or Inactive).
            type: str
        CreateDate:
            description: The date and time the access key was created.
            type: str
        SecretAccessKey:
            description:
            - The secret access key. Returned ONLY at creation time and
              marked C(no_log). Never populated on updates.
            type: str
            returned: only when a new access key is created

diff:
    description:
    - Standard Ansible diff dictionary returned in diff mode.
    - Secret access key values are never included in the diff. New
      keys show the placeholder C(<NEW_SECRET_KEY_GENERATED>); existing
      keys show C(<REDACTED>).
    returned: when run with --diff
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi
except (ImportError, Exception):
    IamApi = None  # type: ignore[assignment,misc]


REDACTED = '<REDACTED>'
NEW_SECRET_MARKER = '<NEW_SECRET_KEY_GENERATED>'


class IamUserAccessKey(object):
    """Class with operations on ObjectScale IAM user access keys."""

    def __init__(self):
        """Define all parameters and initialize the API client."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_user_access_key_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
            required_if=[
                ('state', 'absent', ['access_key_id']),
            ],
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self._fail(
                "The objectscale_client Python package is required but was not found. "
                "Install it with: pip install pydantic urllib3 python-dateutil, "
                "and regenerate the client with 'make build_client'."
            )
            return

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.iam_api = IamApi(self.api_client)
        except Exception as e:
            self._fail(
                "Failed to connect to ObjectScale management endpoint '%s:%s'. "
                "Verify hostname, port, credentials, and network connectivity. "
                "Underlying error: %s" % (
                    self.module.params.get('objectscale_host'),
                    self.module.params.get('objectscale_port'),
                    str(e),
                )
            )
            return

        self.namespace = self.module.params.get('namespace_name')

    # ------------------------------------------------------------------
    # Error helper: spec mandates exit_json(fail=True, msg=...) instead of fail_json()
    # ------------------------------------------------------------------

    def _fail(self, msg, **extra):
        """Exit the module with a failure, following the project spec rule.

        Per the module specification, NEVER call fail_json. Always exit
        via exit_json(fail=True, msg=...). Error messages must clearly
        describe what operation failed, why, and how to resolve it.
        """
        payload = dict(changed=False, failed=True, msg=msg)
        payload.update(extra)
        self.module.exit_json(**payload)

    # ------------------------------------------------------------------
    # Low-level API helpers
    # ------------------------------------------------------------------

    def list_access_keys(self, user_name):
        """List all access keys for a user with auto-pagination.

        Returns a list of dicts with AccessKeyId/UserName/Status/CreateDate.
        """
        try:
            all_keys = []
            marker = None
            while True:
                kwargs = dict(user_name=user_name, x_emc_namespace=self.namespace)
                if marker:
                    kwargs['marker'] = marker
                response = self.iam_api.iam_service_list_access_keys(**kwargs)
                result = response.to_dict()
                list_result = result.get('ListAccessKeysResult') or {}
                keys = list_result.get('AccessKeyMetadata') or []
                all_keys.extend(keys)
                if list_result.get('IsTruncated'):
                    marker = list_result.get('Marker')
                else:
                    break
            return all_keys
        except Exception as e:
            error_msg = utils.determine_error(e)
            self._fail(
                "Failed to list access keys for user '%s' in namespace '%s'. "
                "Verify that the user exists and that the caller has "
                "iam:ListAccessKeys permission. Underlying error: %s" % (
                    user_name, self.namespace, error_msg,
                )
            )

    def find_access_key(self, user_name, access_key_id):
        """Return the metadata dict for access_key_id, or None if absent."""
        for key in self.list_access_keys(user_name) or []:
            if key.get('AccessKeyId') == access_key_id:
                return key
        return None

    def create_access_key(self, user_name):
        """Create a new access key for a user. Returns the full key dict.

        The returned dict is the only place SecretAccessKey is ever
        available; callers must treat it as sensitive.
        """
        try:
            response = self.iam_api.iam_service_create_access_key(
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
            result = response.to_dict()
            return result['CreateAccessKeyResult']['AccessKey']
        except Exception as e:
            error_msg = utils.determine_error(e)
            self._fail(
                "Failed to create access key for user '%s' in namespace '%s'. "
                "Common causes: the user does not exist, the user has already "
                "reached the maximum number of access keys (typically 2), or "
                "the caller lacks iam:CreateAccessKey permission. "
                "Underlying error: %s" % (user_name, self.namespace, error_msg)
            )

    def delete_access_key(self, user_name, access_key_id):
        """Delete an access key by id."""
        try:
            self.iam_api.iam_service_delete_access_key(
                access_key_id=access_key_id,
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self._fail(
                "Failed to delete access key '%s' for user '%s' in namespace '%s'. "
                "Verify the access key id is correct and that the caller has "
                "iam:DeleteAccessKey permission. Underlying error: %s" % (
                    access_key_id, user_name, self.namespace, error_msg,
                )
            )

    def update_access_key_status(self, user_name, access_key_id, status):
        """Update the status of an existing access key."""
        try:
            self.iam_api.iam_service_update_access_key(
                access_key_id=access_key_id,
                status=status,
                user_name=user_name,
                x_emc_namespace=self.namespace,
            )
        except Exception as e:
            error_msg = utils.determine_error(e)
            self._fail(
                "Failed to update status of access key '%s' for user '%s' in "
                "namespace '%s' to '%s'. Verify the access key id is correct, "
                "the status is one of Active/Inactive, and the caller has "
                "iam:UpdateAccessKey permission. Underlying error: %s" % (
                    access_key_id, user_name, self.namespace, status, error_msg,
                )
            )

    # ------------------------------------------------------------------
    # Diff-mode helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_for_diff(key_dict, secret_marker=REDACTED):
        """Return a copy of a key dict safe for inclusion in diff output.

        Any SecretAccessKey present is replaced with a marker. The API
        only returns a secret on create; on all other operations we
        substitute REDACTED.
        """
        if not key_dict:
            return {}
        sanitized = {k: v for k, v in key_dict.items() if k != 'SecretAccessKey'}
        sanitized['SecretAccessKey'] = secret_marker
        return sanitized

    # ------------------------------------------------------------------
    # Main orchestrator
    # ------------------------------------------------------------------

    def perform_module_operation(self):
        """Perform different actions based on parameters chosen in playbook."""
        result = dict(changed=False)

        user_name = self.module.params['user_name']
        access_key_id = self.module.params.get('access_key_id')
        desired_status = self.module.params.get('status')
        state = self.module.params['state']

        if state == 'absent':
            # access_key_id is required_if state=absent
            existing = self.find_access_key(user_name, access_key_id)

            if existing is None:
                # Idempotent no-op; return empty diff
                if self.module._diff:
                    result['diff'] = {'before': {}, 'after': {}}
                self.module.exit_json(**result)
                return

            before = self._sanitize_for_diff(existing)

            if not self.module.check_mode:
                self.delete_access_key(user_name, access_key_id)

            result['changed'] = True
            if self.module._diff:
                result['diff'] = {'before': before, 'after': {}}

            self.module.exit_json(**result)
            return

        # state == 'present'
        if access_key_id is None:
            # No id supplied -> create a new access key
            if self.module.check_mode:
                result['changed'] = True
                if self.module._diff:
                    result['diff'] = {
                        'before': {},
                        'after': {
                            'AccessKeyId': '<WILL_BE_GENERATED>',
                            'UserName': user_name,
                            'Status': 'Active',
                            'SecretAccessKey': NEW_SECRET_MARKER,
                        },
                    }
                self.module.exit_json(**result)
                return

            created = self.create_access_key(user_name)
            result['changed'] = True
            result['access_key'] = created

            if self.module._diff:
                result['diff'] = {
                    'before': {},
                    'after': self._sanitize_for_diff(created, secret_marker=NEW_SECRET_MARKER),
                }

            self.module.exit_json(**result)
            return

        # state == 'present' and access_key_id is supplied
        existing = self.find_access_key(user_name, access_key_id)
        if existing is None:
            self._fail(
                "Access key '%s' was not found for user '%s' in namespace '%s'. "
                "To create a new access key omit the 'access_key_id' parameter; "
                "to update an existing key supply a valid id." % (
                    access_key_id, user_name, self.namespace,
                )
            )
            return

        before = self._sanitize_for_diff(existing)

        if desired_status is not None and existing.get('Status') != desired_status:
            if not self.module.check_mode:
                self.update_access_key_status(user_name, access_key_id, desired_status)
                # Reflect the change in the returned key metadata
                existing = dict(existing)
                existing['Status'] = desired_status
            else:
                existing = dict(existing)
                existing['Status'] = desired_status

            result['changed'] = True

        after = self._sanitize_for_diff(existing)
        result['access_key'] = {k: v for k, v in existing.items() if k != 'SecretAccessKey'}

        if self.module._diff:
            result['diff'] = {'before': before, 'after': after}

        self.module.exit_json(**result)

    # ------------------------------------------------------------------
    # Argument spec
    # ------------------------------------------------------------------

    @staticmethod
    def get_iam_user_access_key_parameters():
        """Return the argument spec for the module parameters."""
        return dict(
            user_name=dict(type='str', required=True),
            namespace_name=dict(type='str', required=True),
            access_key_id=dict(type='str', required=False, no_log=False),
            status=dict(type='str', required=False, choices=['Active', 'Inactive']),
            state=dict(type='str', default='present', choices=['present', 'absent']),
        )


def main():
    """Create IamUserAccessKey object and perform module operation."""
    obj = IamUserAccessKey()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
