#!/usr/bin/python
# Copyright: (c) 2025, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for retrieving IAM SAML Identity Provider information on Dell ObjectScale"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iam_identity_provider_info

version_added: '1.0.0'

short_description: Get IAM SAML Identity Provider information from Dell ObjectScale

description:
- Retrieves information about IAM SAML identity providers on the Dell ObjectScale storage system.
- Can retrieve details of a specific provider or list all providers in a namespace.
- This is a read-only module that does not make any changes.

author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: This module is read-only and always operates as if in check mode.

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
    - The name of a specific SAML identity provider to retrieve.
    - When omitted, all providers in the namespace are listed.
    type: str
    required: false

  namespace:
    description:
    - The ObjectScale namespace to query for identity providers.
    - Maps to the C(X-Emc-Namespace) header in IAM API requests.
    type: str
    required: true

extends_documentation_fragment:
- dellemc.objectscale.objectscale

notes:
- This is a read-only module; it never makes changes to the system.
- Provider ARN format is C(urn:ecs:iam::<namespace>:saml-provider/<provider_name>).
'''

EXAMPLES = r'''
- name: Get details of a specific SAML identity provider
  dellemc.objectscale.iam_identity_provider_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    provider_name: "my-saml-idp"
    namespace: "my-namespace"
  register: provider_info

- name: List all SAML identity providers in a namespace
  dellemc.objectscale.iam_identity_provider_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    namespace: "my-namespace"
  register: all_providers

- name: Display provider information
  ansible.builtin.debug:
    var: all_providers.identity_providers
'''

RETURN = r'''
changed:
    description: Always false for info modules.
    returned: always
    type: bool
    sample: false

identity_providers:
    description: List of identity provider details.
    returned: always
    type: list
    elements: dict
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
        saml_metadata_document:
            description: The SAML metadata XML document (only when querying a specific provider).
            type: str
    sample:
        [
            {
                "provider_name": "my-saml-idp",
                "arn": "urn:ecs:iam::my-namespace:saml-provider/my-saml-idp",
                "create_date": "2025-01-15T12:00:00Z",
                "valid_until": "2030-12-31T23:59:59Z"
            }
        ]
'''

from typing import Any, Dict, List, Optional, TYPE_CHECKING
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


class IamIdentityProviderInfo(object):
    """Class for retrieving ObjectScale IAM SAML Identity Provider information"""

    def __init__(self) -> None:
        """Define all parameters required by this module."""
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_identity_provider_info_parameters())

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
    def get_identity_provider_info_parameters() -> Dict[str, Any]:
        """Return the argument spec for the identity provider info module."""
        return dict(
            provider_name=dict(type='str', required=False),
            namespace=dict(type='str', required=True),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_arn(provider_name: str, namespace: str) -> str:
        """Build a SAML provider ARN from name and namespace."""
        return 'urn:ecs:iam::%s:saml-provider/%s' % (namespace, provider_name)

    @staticmethod
    def _extract_name_from_arn(arn: str) -> str:
        """Extract provider name from ARN string."""
        if arn and '/' in arn:
            return arn.rsplit('/', 1)[-1]
        return arn or ''

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_provider_details(self, provider_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific identity provider."""
        arn = self._build_arn(provider_name, namespace)
        try:
            result = self.iam_api.get_saml_provider(arn, namespace)
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Getting identity provider %s failed with error: %s" % (provider_name, error_msg)
            self.module.exit_json(failed=True, msg=msg)
            return None

        if result is None:
            self.module.exit_json(
                failed=True,
                msg="Identity provider '%s' not found in namespace '%s'" % (provider_name, namespace)
            )
            return None

        return {
            'provider_name': provider_name,
            'arn': arn,
            'create_date': result.get('CreateDate', ''),
            'valid_until': result.get('ValidUntil', ''),
            'saml_metadata_document': result.get('SAMLMetadataDocument', ''),
        }

    def list_providers(self, namespace: str) -> List[Dict[str, Any]]:
        """List all identity providers in a namespace."""
        try:
            raw_list = self.iam_api.list_saml_providers(namespace)
        except Exception as e:
            error_msg = utils.determine_error(e)
            msg = "Listing identity providers failed with error: %s" % error_msg
            self.module.exit_json(failed=True, msg=msg)
            return []

        providers = []
        for entry in raw_list:
            arn = entry.get('Arn', '')
            providers.append({
                'provider_name': self._extract_name_from_arn(arn),
                'arn': arn,
                'create_date': entry.get('CreateDate', ''),
                'valid_until': entry.get('ValidUntil', ''),
            })

        return providers

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def perform_module_operation(self) -> None:
        """Main entry point for module execution."""
        provider_name = self.module.params.get('provider_name')
        namespace = self.module.params['namespace']

        if provider_name:
            details = self.get_provider_details(provider_name, namespace)
            providers = [details] if details else []
        else:
            providers = self.list_providers(namespace)

        self.module.exit_json(
            changed=False,
            identity_providers=providers,
        )


def main():
    """Main entry point for the module."""
    obj = IamIdentityProviderInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
