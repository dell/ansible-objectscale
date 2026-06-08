#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible info module for querying the ObjectScale VDC keystore certificate chain."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: vdc_certificate_info

version_added: '1.1.0'

short_description: Read the VDC keystore certificate chain on Dell ObjectScale

description:
- Returns the current VDC keystore certificate chain via GET /vdc/keystore.
- Parses certificate metadata (subject, issuer, expiry, serial) when the
  C(cryptography) Python library is available.
- Read-only; never reports C(changed=true).

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

  validate_certs:
    description:
    - Boolean value to enable or disable SSL certificate verification.
    type: bool
    default: true

  timeout:
    description:
    - Timeout in seconds for API requests.
    type: int
    default: 30

notes:
- This is an info module. It always returns C(changed=false).
- No special role required — any authenticated user can query the certificate chain.
- Supports check mode.

requirements:
- python >= 3.9
- cryptography (optional, enables richer certificate metadata)
'''

EXAMPLES = r'''
- name: Get current VDC certificate chain
  dellemc.objectscale.vdc_certificate_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
  register: cert_info

- name: Display certificate details
  ansible.builtin.debug:
    msg: |
      Leaf Subject: {{ cert_info.vdc_certificate_details.leaf_subject | default('unknown') }}
      Expires: {{ cert_info.vdc_certificate_details.not_after | default('unknown') }}
      Fingerprint: {{ cert_info.vdc_certificate_details.fingerprint }}
      Chain Length: {{ cert_info.vdc_certificate_details.chain_length }}

- name: Check certificate expiry for compliance audit
  dellemc.objectscale.vdc_certificate_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
  register: audit_cert

- name: Warn if certificate metadata is unavailable
  ansible.builtin.debug:
    msg: "Install cryptography library for full certificate metadata"
  when: audit_cert.vdc_certificate_details.leaf_subject is not defined
'''

RETURN = r'''
changed:
    description: Always false for info modules.
    returned: always
    type: bool

vdc_certificate_details:
    description: Current VDC keystore certificate details.
    returned: success
    type: dict
    contains:
        fingerprint:
            description: SHA-256 hex digest of the normalised chain bytes.
            type: str
            sample: "ab12cd34..."
        chain:
            description: PEM-encoded certificate chain (public).
            type: str
        leaf_subject:
            description: X.509 subject of the leaf certificate (cryptography only).
            type: str
            sample: "CN=obs.example.com"
        leaf_serial:
            description: Hex serial number of the leaf certificate (cryptography only).
            type: str
        not_before:
            description: ISO-8601 leaf NotBefore timestamp (cryptography only).
            type: str
        not_after:
            description: ISO-8601 leaf NotAfter timestamp (cryptography only).
            type: str
        chain_length:
            description: Count of certificates in the chain.
            type: int
            sample: 3
'''

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (  # noqa: E402
    HAS_OBJECTSCALE_CLIENT,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api import (  # noqa: E402
    VdcKeystoreApi,
    parse_certificate_metadata,
)

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import (  # noqa: E402
        api_client as objectscale_api_client,
    )
except Exception:
    objectscale_api_client = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import (  # noqa: E402
        _stubs as objectscale_client_stubs,
    )
except Exception:
    objectscale_client_stubs = None


class VdcCertificateInfo(object):
    """Gather VDC keystore certificate chain details from ObjectScale."""

    @staticmethod
    def _ensure_client_stub_compatibility():
        if objectscale_api_client is not None:
            secret_str_cls = getattr(objectscale_api_client, 'SecretStr', None)
            if secret_str_cls is str:
                class _CompatSecretStr(str):
                    def get_secret_value(self):
                        return str(self)
                objectscale_api_client.SecretStr = _CompatSecretStr

        if objectscale_client_stubs is not None:
            base_model_cls = getattr(objectscale_client_stubs, 'BaseModel', None)
            if base_model_cls is not None and not hasattr(base_model_cls, 'model_dump'):
                def _model_dump(self, *args, **kwargs):
                    data = getattr(self, '__dict__', None)
                    if isinstance(data, dict):
                        return dict(data)
                    return {}
                base_model_cls.model_dump = _model_dump

    def __init__(self):
        self.module_params = utils.get_objectscale_management_host_parameters()

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil",
            )
            return

        try:
            self._ensure_client_stub_compatibility()
            self.api_client = utils.get_objectscale_connection(self.module.params)
            timeout = self.module.params.get('timeout', 30)
            self.keystore_api = VdcKeystoreApi(self.api_client, timeout=timeout)
        except Exception as e:
            self.module.exit_json(
                failed=True,
                msg="Failed to connect to ObjectScale: %s" % str(e),
            )

    def perform_module_operation(self):
        try:
            response = self.keystore_api.get_certificate_chain()
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) == '404':
                self.module.exit_json(
                    failed=True,
                    msg="FC-224: VDC keystore not found at endpoint /vdc/keystore",
                )
                return
            if str(status) == '401':
                self.module.exit_json(
                    failed=True,
                    msg="FC-222: authentication failed — %s" % str(e),
                )
                return
            error_msg = utils.determine_error(e) if hasattr(utils, 'determine_error') else str(e)
            self.module.exit_json(
                failed=True,
                msg="Failed to get VDC certificate chain: %s" % error_msg,
            )
            return

        chain_pem = response.get('chain', '')
        details = parse_certificate_metadata(chain_pem) if chain_pem else {
            'fingerprint': '',
            'chain': '',
            'chain_length': 0,
        }

        self.module.exit_json(
            changed=False,
            vdc_certificate_details=details,
        )


def main():
    obj = VdcCertificateInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
