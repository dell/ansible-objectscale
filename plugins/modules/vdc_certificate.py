#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing the VDC keystore key + certificate pair on Dell ObjectScale."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: vdc_certificate

version_added: '1.1.0'

short_description: Manage the VDC keystore key + certificate pair on Dell ObjectScale

description:
- Manages the VDC keystore on an ObjectScale cluster by setting or replacing the
  private key and certificate chain via the OBS Management API (PUT /vdc/keystore).
- Supports check mode and diff mode.
- Idempotent — fingerprints the desired chain against the live chain before issuing PUT.
- The C(private_key_content) parameter is marked C(no_log=true) and will never appear
  in logs, output, or diffs.

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

  state:
    description:
    - Desired state of the VDC keystore.
    type: str
    choices: ['present']
    default: present

  private_key_path:
    description:
    - Path on the control node to a PEM-encoded private key file.
    - Mutually exclusive with C(private_key_content).
    type: path
    required: false

  private_key_content:
    description:
    - PEM-encoded private key content.
    - Mutually exclusive with C(private_key_path).
    - Marked sensitive; use Ansible Vault.
    type: str
    required: false

  certificate_chain_path:
    description:
    - Path on the control node to a PEM-encoded certificate chain file
      (leaf + intermediates concatenated).
    - Mutually exclusive with C(certificate_chain_content).
    type: path
    required: false

  certificate_chain_content:
    description:
    - PEM-encoded certificate chain content.
    - Mutually exclusive with C(certificate_chain_path).
    type: str
    required: false

notes:
- Requires the C(SECURITY_ADMIN) role on the configured user.
- Operation is non-disruptive — OBS hot-reloads the chain.
- Supports check mode and diff mode.

requirements:
- python >= 3.9
- cryptography (optional, enables richer validation and metadata)
'''

EXAMPLES = r'''
- name: Rotate VDC keystore using Vault-stored content
  dellemc.objectscale.vdc_certificate:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: true
    private_key_content: "{{ vault_obs_private_key }}"
    certificate_chain_content: "{{ obs_chain_pem }}"
    state: present
  register: rot

- name: Rotate VDC keystore from on-disk PEM files
  dellemc.objectscale.vdc_certificate:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    private_key_path: /etc/pki/obs/obs.key
    certificate_chain_path: /etc/pki/obs/obs-chain.pem
    state: present
  check_mode: true
  diff: true

- name: Idempotent run (no change if chain matches)
  dellemc.objectscale.vdc_certificate:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    private_key_content: "{{ vault_obs_private_key }}"
    certificate_chain_content: "{{ lookup('file', 'certs/chain.pem') }}"
    state: present
  register: rerun
'''

RETURN = r'''
changed:
    description: Whether the VDC keystore was modified.
    type: bool
    returned: always
    sample: true

vdc_certificate_details:
    description: Current VDC keystore details after the run.
    type: dict
    returned: success
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
            description: Hex serial of the leaf certificate (cryptography only).
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

diff:
    description: Before/after metadata (private key NEVER included).
    type: dict
    returned: when diff mode enabled and changed is true
'''

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (  # noqa: E402
    HAS_OBJECTSCALE_CLIENT,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api import (  # noqa: E402
    VdcKeystoreApi,
    fingerprint_chain,
    validate_pem_certificate,
    validate_pem_private_key,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_cert_common import (  # noqa: E402, E501
    ensure_client_stub_compatibility,
    read_pem_param,
    get_chain_metadata,
    connect_keystore,
    fetch_current_chain,
    apply_certificate,
    verify_and_get_details,
)

# Keep module-level alias so existing tests that import
# ``_ensure_client_stub_compatibility`` from this module
# continue to work.
_ensure_client_stub_compatibility = ensure_client_stub_compatibility

_LABEL = "VDC"
_DETAILS_KEY = "vdc_certificate_details"


def main():
    _ensure_client_stub_compatibility()

    module_params = (
        utils.get_objectscale_management_host_parameters()
    )
    module_params.update(
        state=dict(
            type='str', choices=['present'],
            default='present',
        ),
        private_key_path=dict(
            type='path', required=False, no_log=False,
        ),
        private_key_content=dict(
            type='str', required=False, no_log=True,
        ),
        certificate_chain_path=dict(
            type='path', required=False, no_log=False,
        ),
        certificate_chain_content=dict(
            type='str', required=False, no_log=False,
        ),
    )

    module = AnsibleModule(
        argument_spec=module_params,
        supports_check_mode=True,
        mutually_exclusive=[
            ('private_key_path', 'private_key_content'),
            (
                'certificate_chain_path',
                'certificate_chain_content',
            ),
        ],
        required_one_of=[
            ('private_key_path', 'private_key_content'),
            (
                'certificate_chain_path',
                'certificate_chain_content',
            ),
        ],
    )

    if not HAS_OBJECTSCALE_CLIENT:
        module.exit_json(
            failed=True,
            msg=(
                "The objectscale_client Python package is "
                "required. Install it with: pip install "
                "pydantic urllib3 python-dateutil"
            ),
        )
        return

    # --- Read PEM inputs ---
    private_key = read_pem_param(
        module,
        'private_key_path',
        'private_key_content',
    )
    certificate_chain = read_pem_param(
        module,
        'certificate_chain_path',
        'certificate_chain_content',
    )

    # --- Validate PEM format ---
    if not validate_pem_private_key(private_key):
        module.fail_json(
            msg="FC-236: private_key contains no PEM block",
        )
    if not validate_pem_certificate(certificate_chain):
        module.fail_json(
            msg="FC-232: certificate_chain contains "
            "no PEM blocks",
        )

    # --- Connect ---
    keystore_api = connect_keystore(
        module, VdcKeystoreApi,
    )

    # --- Fetch current chain for idempotency ---
    current = fetch_current_chain(
        module, keystore_api, _LABEL,
    )

    current_chain = current.get('chain', '')
    desired_fp = fingerprint_chain(certificate_chain)
    current_fp = (
        fingerprint_chain(current_chain)
        if current_chain else ''
    )

    needs_change = desired_fp != current_fp

    result = {'changed': False}

    if not needs_change:
        result[_DETAILS_KEY] = get_chain_metadata(
            current_chain,
        )
        module.exit_json(**result)
        return

    # --- Check mode ---
    if module.check_mode:
        result['changed'] = True
        if module._diff:
            result['diff'] = {
                'before': {'fingerprint': current_fp},
                'after': {'fingerprint': desired_fp},
            }
        result[_DETAILS_KEY] = get_chain_metadata(
            current_chain,
        )
        module.exit_json(**result)
        return

    # --- Apply change ---
    put_response = apply_certificate(
        module, keystore_api,
        private_key, certificate_chain, _LABEL,
    )

    # --- Post-PUT verification ---
    details = verify_and_get_details(
        module, keystore_api, desired_fp, put_response,
    )

    result['changed'] = True
    result[_DETAILS_KEY] = details

    if module._diff:
        result['diff'] = {
            'before': {'fingerprint': current_fp},
            'after': {
                'fingerprint': details.get(
                    'fingerprint', desired_fp,
                ),
            },
        }

    module.exit_json(**result)


if __name__ == '__main__':  # pragma: no cover
    main()
