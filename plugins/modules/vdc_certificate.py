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
    no_log: true

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

import os  # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (  # noqa: E402
    HAS_OBJECTSCALE_CLIENT,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api import (  # noqa: E402
    VdcKeystoreApi,
    fingerprint_chain,
    parse_certificate_metadata,
    validate_pem_certificate,
    validate_pem_private_key,
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


def _ensure_client_stub_compatibility():
    """Patch generated stubs for runtime compatibility when pydantic is absent."""
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


def _read_pem_param(module, path_param, content_param, label):
    """Read PEM content from either a file path or inline content parameter.

    Returns the PEM string or calls module.fail_json on error.
    """
    path_val = module.params.get(path_param)
    content_val = module.params.get(content_param)

    if content_val:
        return content_val

    if path_val:
        path_val = os.path.expanduser(path_val)
        if not os.path.isfile(path_val):
            module.fail_json(
                msg="FC-221: file '%s' not readable: No such file" % path_val,
            )
        try:
            with open(path_val, 'r') as fh:
                return fh.read()
        except OSError as err:
            module.fail_json(
                msg="FC-221: file '%s' not readable: %s" % (path_val, str(err)),
            )

    module.fail_json(
        msg="FC-230: one of %s, %s is required" % (path_param, content_param),
    )


def main():
    _ensure_client_stub_compatibility()

    module_params = utils.get_objectscale_management_host_parameters()
    module_params.update(
        state=dict(type='str', choices=['present'], default='present'),
        private_key_path=dict(type='path', required=False, no_log=False),
        private_key_content=dict(type='str', required=False, no_log=True),
        certificate_chain_path=dict(type='path', required=False, no_log=False),
        certificate_chain_content=dict(type='str', required=False, no_log=False),
    )

    module = AnsibleModule(
        argument_spec=module_params,
        supports_check_mode=True,
        mutually_exclusive=[
            ('private_key_path', 'private_key_content'),
            ('certificate_chain_path', 'certificate_chain_content'),
        ],
        required_one_of=[
            ('private_key_path', 'private_key_content'),
            ('certificate_chain_path', 'certificate_chain_content'),
        ],
    )

    if not HAS_OBJECTSCALE_CLIENT:
        module.exit_json(
            failed=True,
            msg="The objectscale_client Python package is required. "
                "Install it with: pip install pydantic urllib3 python-dateutil",
        )
        return

    # --- Read PEM inputs ---
    private_key = _read_pem_param(
        module, 'private_key_path', 'private_key_content', 'private key',
    )
    certificate_chain = _read_pem_param(
        module, 'certificate_chain_path', 'certificate_chain_content', 'certificate chain',
    )

    # --- Validate PEM format ---
    if not validate_pem_private_key(private_key):
        module.fail_json(msg="FC-236: private_key contains no PEM block")
    if not validate_pem_certificate(certificate_chain):
        module.fail_json(msg="FC-232: certificate_chain contains no PEM blocks")

    # --- Connect ---
    try:
        api_client = utils.get_objectscale_connection(module.params)
        timeout = module.params.get('timeout', 30)
        keystore_api = VdcKeystoreApi(api_client, timeout=timeout)
    except Exception as e:
        module.fail_json(msg="Failed to connect to ObjectScale: %s" % str(e))
        return

    # --- Fetch current chain for idempotency ---
    try:
        current = keystore_api.get_certificate_chain()
    except Exception as e:
        status = getattr(e, 'status', None)
        if str(status) == '401':
            module.fail_json(msg="FC-222: authentication failed — %s" % str(e))
        error_msg = utils.determine_error(e) if hasattr(utils, 'determine_error') else str(e)
        module.fail_json(msg="Failed to get current VDC certificate chain: %s" % error_msg)
        return

    current_chain = current.get('chain', '')
    desired_fp = fingerprint_chain(certificate_chain)
    current_fp = fingerprint_chain(current_chain) if current_chain else ''

    needs_change = desired_fp != current_fp

    result = {'changed': False}

    if not needs_change:
        # Idempotent — no change needed
        details = parse_certificate_metadata(current_chain) if current_chain else {
            'fingerprint': '', 'chain': '', 'chain_length': 0,
        }
        result['vdc_certificate_details'] = details
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
        current_details = parse_certificate_metadata(current_chain) if current_chain else {
            'fingerprint': '', 'chain': '', 'chain_length': 0,
        }
        result['vdc_certificate_details'] = current_details
        module.exit_json(**result)
        return

    # --- Apply change ---
    try:
        put_response = keystore_api.set_key_certificate_pair(private_key, certificate_chain)
    except Exception as e:
        status = getattr(e, 'status', None)
        if str(status) == '403':
            module.fail_json(msg="FC-223: SECURITY_ADMIN role required to update VDC keystore")
        if str(status) == '400':
            module.fail_json(msg="FC-220: invalid PEM input — %s" % str(e))
        if str(status) == '409':
            module.fail_json(msg="FC-227: concurrent keystore update conflict")
        error_msg = utils.determine_error(e) if hasattr(utils, 'determine_error') else str(e)
        module.fail_json(msg="Failed to set VDC certificate: %s" % error_msg)
        return

    # --- Post-PUT verification ---
    try:
        verify = keystore_api.get_certificate_chain()
        verify_chain = verify.get('chain', '')
        verify_fp = fingerprint_chain(verify_chain) if verify_chain else ''
        if verify_fp != desired_fp:
            module.fail_json(
                msg="FC-235: post-PUT chain fingerprint mismatch (expected %s, got %s)"
                    % (desired_fp, verify_fp),
            )
            return
        details = parse_certificate_metadata(verify_chain)
    except Exception:
        # Verification fetch failed — use PUT response
        new_chain = put_response.get('chain', '')
        details = parse_certificate_metadata(new_chain) if new_chain else {
            'fingerprint': desired_fp, 'chain': '', 'chain_length': 0,
        }

    result['changed'] = True
    result['vdc_certificate_details'] = details

    if module._diff:
        result['diff'] = {
            'before': {'fingerprint': current_fp},
            'after': {'fingerprint': details.get('fingerprint', desired_fp)},
        }

    module.exit_json(**result)


if __name__ == '__main__':  # pragma: no cover
    main()
