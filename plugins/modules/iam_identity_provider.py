#!/usr/bin/python
# Copyright: (c) 2025, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing IAM SAML Identity Providers on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_identity_provider

version_added: '1.0.0'

short_description: Manage IAM SAML Identity Providers on Dell ObjectScale

description:
- Manages IAM SAML identity providers on the Dell ObjectScale storage system.
  This includes creating, updating, and deleting SAML identity providers.
- All operations are scoped to a specific ObjectScale namespace.
- Supports check mode and diff mode.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: Supports check mode. No changes will be made when check mode is enabled.
  diff_mode:
    support: full
    description: Supports diff mode. Shows before and after state of the identity provider.

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

  provider_name:
    description:
    - The name of the SAML identity provider.
    - This name is used to construct the provider ARN.
    type: str
    required: true

  namespace:
    description:
    - The ObjectScale namespace in which the identity provider resides.
    - Maps to the C(X-Emc-Namespace) header in IAM API requests.
    type: str
    required: true

  saml_metadata_document:
    description:
    - The SAML metadata XML document from the identity provider.
    - Required when creating a new identity provider (I(state=present) and provider does not exist).
    - When provided for an existing provider, the metadata will be compared and updated if different.
    - Must be between 1000 and 10000000 characters in length.
    type: str
    required: false
    no_log: true

  state:
    description:
    - The desired state of the identity provider.
    - C(present) ensures the provider exists; C(absent) ensures it does not.
    type: str
    choices: ['present', 'absent']
    default: present

extends_documentation_fragment:
- dellemc.objectscale.objectscale

notes:
- The SAML metadata document must contain a valid X.509 certificate.
- Provider ARN format is C(urn:ecs:iam::<namespace>:saml-provider/<provider_name>).
- This module interacts with the ObjectScale IAM API (AWS IAM-compatible).
'''

EXAMPLES = r'''
- name: Create a SAML identity provider
  dellemc.objectscale.iam_identity_provider:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    provider_name: "my-saml-idp"
    namespace: "my-namespace"
    saml_metadata_document: "{{ lookup('file', 'saml-metadata.xml') }}"
    state: "present"

- name: Update a SAML identity provider metadata
  dellemc.objectscale.iam_identity_provider:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    provider_name: "my-saml-idp"
    namespace: "my-namespace"
    saml_metadata_document: "{{ lookup('file', 'updated-saml-metadata.xml') }}"
    state: "present"

- name: Check mode - preview identity provider creation
  dellemc.objectscale.iam_identity_provider:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    provider_name: "preview-idp"
    namespace: "my-namespace"
    saml_metadata_document: "{{ lookup('file', 'saml-metadata.xml') }}"
    state: "present"
  check_mode: true

- name: Delete a SAML identity provider
  dellemc.objectscale.iam_identity_provider:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    provider_name: "my-saml-idp"
    namespace: "my-namespace"
    state: "absent"
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
    sample: false

iam_identity_provider_details:
    description: Identity provider details.
    returned: When state is C(present) and the provider exists
    type: dict
    contains:
        provider_name:
            description: The name of the SAML identity provider.
            type: str
        arn:
            description: The ARN of the SAML identity provider.
            type: str
        create_date:
            description: The date and time when the provider was created.
            type: str
        valid_until:
            description: The expiration date of the provider metadata.
            type: str
    sample:
        {
            "provider_name": "my-saml-idp",
            "arn": "urn:ecs:iam::my-namespace:saml-provider/my-saml-idp",
            "create_date": "2025-01-15T12:00:00Z",
            "valid_until": "2030-12-31T23:59:59Z"
        }

diff:
    description: Diff of the identity provider before and after changes.
    returned: When diff mode is enabled
    type: dict
'''

from typing import Any, Dict, Optional, TYPE_CHECKING
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


class IamIdentityProvider(object):
    """Class with operations on ObjectScale IAM SAML Identity Providers"""

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_identity_provider_parameters())

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

    @staticmethod
    def get_identity_provider_parameters() -> Dict[str, Any]:
        """Return the argument spec for the identity provider module."""
        return dict(
            provider_name=dict(type='str', required=True),
            namespace=dict(type='str', required=True),
            saml_metadata_document=dict(type='str', required=False, no_log=True),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_arn(self, provider_name: str, namespace: str) -> str:
        """Build a SAML provider ARN from name and namespace."""
        return 'urn:ecs:iam::%s:saml-provider/%s' % (namespace, provider_name)

    def _normalize_details(self, provider_name: str, namespace: str,
                           raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw API response into a consistent return dict."""
        return {
            'provider_name': provider_name,
            'arn': self._build_arn(provider_name, namespace),
            'create_date': raw.get('CreateDate', ''),
            'valid_until': raw.get('ValidUntil', ''),
        }

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_provider(self, provider_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get identity provider details. Returns normalized dict or None."""
        arn = self._build_arn(provider_name, namespace)
        try:
            result = self.iam_api.get_saml_provider(arn, namespace)
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Getting identity provider %s failed with error: %s" % (provider_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

        if result is None:
            return None

        details = self._normalize_details(provider_name, namespace, result)
        details['saml_metadata_document'] = result.get('SAMLMetadataDocument', '')
        return details

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_provider(self, provider_name: str, namespace: str,
                        saml_metadata_document: str) -> Optional[Dict[str, Any]]:
        """Create a new SAML identity provider."""
        try:
            if not self.module.check_mode:
                self.iam_api.create_saml_provider(
                    provider_name, saml_metadata_document, namespace
                )
            return self.get_provider(provider_name, namespace) if not self.module.check_mode else {
                'provider_name': provider_name,
                'arn': self._build_arn(provider_name, namespace),
                'create_date': '',
                'valid_until': '',
            }
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Creating identity provider %s failed with error: %s" % (provider_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

    def update_provider(self, provider_name: str, namespace: str,
                        saml_metadata_document: str) -> Optional[Dict[str, Any]]:
        """Update a SAML identity provider's metadata."""
        arn = self._build_arn(provider_name, namespace)
        try:
            if not self.module.check_mode:
                self.iam_api.update_saml_provider(
                    arn, saml_metadata_document, namespace
                )
            return self.get_provider(provider_name, namespace) if not self.module.check_mode else {
                'provider_name': provider_name,
                'arn': arn,
                'create_date': '',
                'valid_until': '',
            }
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Updating identity provider %s failed with error: %s" % (provider_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

    def delete_provider(self, provider_name: str, namespace: str) -> Optional[bool]:
        """Delete a SAML identity provider."""
        arn = self._build_arn(provider_name, namespace)
        try:
            if not self.module.check_mode:
                self.iam_api.delete_saml_provider(arn, namespace)
            return True
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Deleting identity provider %s failed with error: %s" % (provider_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def perform_module_operation(self) -> None:
        """Main entry point for module execution."""
        provider_name = self.module.params['provider_name']
        namespace = self.module.params['namespace']
        state = self.module.params['state']
        saml_metadata_document = self.module.params.get('saml_metadata_document')

        changed = False
        provider_details = None  # type: Optional[Dict[str, Any]]
        diff = dict(before={}, after={})

        # Get current state
        current = self.get_provider(provider_name, namespace)

        if state == 'present':
            if current is None:
                # Create
                if saml_metadata_document is None:
                    self.module.exit_json(
                        failed=True,
                        msg="saml_metadata_document is required when creating a new identity provider"
                    )
                    return

                if self.module._diff:
                    diff['before'] = {}
                    diff['after'] = {'provider_name': provider_name, 'state': 'present'}

                provider_details = self.create_provider(provider_name, namespace, saml_metadata_document)
                changed = True
            else:
                # Exists — check if update needed
                if saml_metadata_document is not None:
                    existing_metadata = current.get('saml_metadata_document', '')
                    if existing_metadata != saml_metadata_document:
                        if self.module._diff:
                            diff['before'] = {
                                'provider_name': provider_name,
                                'valid_until': current.get('valid_until', ''),
                            }

                        provider_details = self.update_provider(
                            provider_name, namespace, saml_metadata_document
                        )
                        changed = True

                        if self.module._diff:
                            diff['after'] = {
                                'provider_name': provider_name,
                                'valid_until': provider_details.get('valid_until', '') if provider_details else '',
                            }
                    else:
                        # No change — metadata is the same
                        provider_details = {k: v for k, v in current.items() if k != 'saml_metadata_document'}
                else:
                    # No metadata provided, no update needed
                    provider_details = {k: v for k, v in current.items() if k != 'saml_metadata_document'}

        elif state == 'absent':
            if current is not None:
                if self.module._diff:
                    diff['before'] = {'provider_name': provider_name, 'state': 'present'}
                    diff['after'] = {}

                self.delete_provider(provider_name, namespace)
                changed = True
            # else: already absent, nothing to do

        result = dict(
            changed=changed,
            iam_identity_provider_details=provider_details if provider_details else {},
        )

        if self.module._diff:
            result['diff'] = diff

        self.module.exit_json(**result)


def main():
    """Main entry point for the module."""
    obj = IamIdentityProvider()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
