#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible info module for IAM user access keys on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_user_access_key_info

version_added: '1.0.0'

short_description: Gather IAM user access key information from Dell ObjectScale

description:
- Gather information about IAM user S3-compatible access keys on Dell ObjectScale.
- Supports both a read operation (when I(access_key_id) is supplied) and a
  list operation (when only I(user_name) and I(namespace_name) are supplied).
- This is a read-only module and does not make any modifications to the
  target system.
- The C(secret_access_key) is NEVER returned by this module. Only access
  key metadata (id, status, create date, user name) is returned.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

extends_documentation_fragment:
- dellemc.objectscale.objectscale

options:
  user_name:
    description:
    - Name of the IAM user whose access keys should be queried.
    type: str
    required: true

  namespace_name:
    description:
    - The ObjectScale namespace that owns the IAM user.
    type: str
    required: true

  access_key_id:
    description:
    - Identifier of a specific access key to read.
    - When supplied, the module returns only that key's metadata (or
      an empty list if it does not exist).
    - When omitted, all access keys for the user are returned.
    type: str
    required: false

notes:
- The I(check_mode) is supported. This is a read-only info module.
- The objectscale_client Python package must be installed.
  Generate it with C(make build_client).
'''

EXAMPLES = r'''
- name: List all access keys for an IAM user
  dellemc.objectscale.iam_user_access_key_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: sample_user_1
    namespace_name: ns1
  register: all_keys

- name: Get details of a specific access key
  dellemc.objectscale.iam_user_access_key_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    user_name: sample_user_1
    namespace_name: ns1
    access_key_id: AKIA80817B9F1F4C72CB
  register: specific_key
'''

RETURN = r'''
changed:
    description: Always false for info modules.
    returned: always
    type: bool
    sample: false

access_keys:
    description:
    - List of access key metadata dicts.
    - When I(access_key_id) is supplied, contains 0 or 1 entries.
    - The C(SecretAccessKey) is never included.
    returned: always
    type: list
    elements: dict
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
    sample:
        - AccessKeyId: AKIA80817B9F1F4C72CB
          UserName: sample_user_1
          Status: Active
          CreateDate: '2025-01-15T10:30:00Z'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils \
    import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.iam_api import IamApi
except Exception:
    IamApi = None  # type: ignore[assignment,misc]


class IamUserAccessKeyInfo(object):
    """Read-only class for gathering IAM user access key info from ObjectScale."""

    def __init__(self):
        """Define module parameters and initialize the API client."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_iam_user_access_key_info_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
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
        """Exit the module with a failure using exit_json(fail=True)."""
        payload = dict(changed=False, failed=True, msg=msg)
        payload.update(extra)
        self.module.exit_json(**payload)

    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------

    @staticmethod
    def get_iam_user_access_key_info_parameters():
        """Return the argument spec for this info module."""
        return dict(
            user_name=dict(type='str', required=True),
            namespace_name=dict(type='str', required=True),
            access_key_id=dict(type='str', required=False, no_log=False),
        )

    # ------------------------------------------------------------------
    # API interactions
    # ------------------------------------------------------------------

    def list_access_keys(self, user_name):
        """List all access keys for a user with auto-pagination."""
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
            return []

    # ------------------------------------------------------------------
    # Main orchestrator
    # ------------------------------------------------------------------

    def perform_module_operation(self):
        """Perform the read or list operation and exit."""
        user_name = self.module.params['user_name']
        access_key_id = self.module.params.get('access_key_id')

        all_keys = self.list_access_keys(user_name) or []

        if access_key_id:
            matched = [k for k in all_keys if k.get('AccessKeyId') == access_key_id]
            self.module.exit_json(changed=False, access_keys=matched)
            return

        self.module.exit_json(changed=False, access_keys=all_keys)


def main():
    """Create IamUserAccessKeyInfo object and perform module operation."""
    obj = IamUserAccessKeyInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
