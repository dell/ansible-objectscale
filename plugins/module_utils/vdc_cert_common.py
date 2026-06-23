# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared helpers for the vdc_certificate and vdc_certificate_chain modules.

Both modules manage a keystore on ObjectScale (VDC vs Object-cert) and
share identical logic for PEM I/O, client-stub patching, idempotency
fingerprinting, and the connect/fetch/apply/verify workflow.  This
module holds that shared code so neither module duplicates it.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible_collections.dellemc.objectscale.plugins.module_utils import (
    utils,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api import (  # noqa: E501
    fingerprint_chain,
    parse_certificate_metadata,
)

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import (  # noqa: E501, E402
        api_client as objectscale_api_client,
    )
except Exception:
    objectscale_api_client = None

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client import (  # noqa: E501, E402
        _stubs as objectscale_client_stubs,
    )
except Exception:
    objectscale_client_stubs = None


# ------------------------------------------------------------------
# Client-stub compatibility
# ------------------------------------------------------------------

def ensure_client_stub_compatibility():
    """Patch generated stubs when pydantic is absent."""
    if objectscale_api_client is not None:
        secret_str_cls = getattr(
            objectscale_api_client, 'SecretStr', None,
        )
        if secret_str_cls is str:
            class _CompatSecretStr(str):
                def get_secret_value(self):
                    return str(self)
            objectscale_api_client.SecretStr = _CompatSecretStr

    if objectscale_client_stubs is not None:
        base_model_cls = getattr(
            objectscale_client_stubs, 'BaseModel', None,
        )
        if (
            base_model_cls is not None
            and not hasattr(base_model_cls, 'model_dump')
        ):
            def _model_dump(self, *a, **kw):  # noqa: W0613
                data = getattr(self, '__dict__', None)
                if isinstance(data, dict):
                    return dict(data)
                return {}
            base_model_cls.model_dump = _model_dump


# ------------------------------------------------------------------
# PEM parameter reading
# ------------------------------------------------------------------

def read_pem_param(module, path_param, content_param):
    """Read PEM from a file-path or inline-content parameter.

    Returns the PEM string or calls ``module.fail_json``.
    """
    path_val = module.params.get(path_param)
    content_val = module.params.get(content_param)

    if content_val:
        return content_val

    if path_val:
        if not os.path.isfile(path_val):
            module.fail_json(
                msg=(
                    "FC-221: file '%s' not readable: "
                    "No such file" % path_val
                ),
            )
        try:
            with open(path_val, 'r') as fh:
                return fh.read()
        except OSError as err:
            module.fail_json(
                msg=(
                    "FC-221: file '%s' not readable: %s"
                    % (path_val, str(err))
                ),
            )

    module.fail_json(
        msg=(
            "FC-230: one of %s, %s is required"
            % (path_param, content_param)
        ),
    )


# ------------------------------------------------------------------
# Certificate metadata helpers
# ------------------------------------------------------------------

def empty_cert_details(fingerprint=''):
    """Return an empty certificate-details dict."""
    return {
        'fingerprint': fingerprint,
        'chain': '',
        'chain_length': 0,
    }


def get_chain_metadata(chain, fallback_fp=''):
    """Parse certificate metadata or return empty details."""
    if chain:
        return parse_certificate_metadata(chain)
    return empty_cert_details(fallback_fp)


# ------------------------------------------------------------------
# Keystore workflow helpers (parameterised by *label*)
# ------------------------------------------------------------------

def connect_keystore(module, api_cls):
    """Create an API client and keystore wrapper, or fail.

    *api_cls* is the keystore wrapper class
    (``VdcKeystoreApi`` or ``ObjectCertKeystoreApi``).
    """
    try:
        api_client = utils.get_objectscale_connection(
            module.params,
        )
        timeout = module.params.get('timeout', 30)
        return api_cls(api_client, timeout=timeout)
    except Exception as e:
        module.fail_json(
            msg="Failed to connect to ObjectScale: %s"
            % str(e),
        )
        return None


def fetch_current_chain(module, keystore_api, label):
    """Fetch the current certificate chain or fail.

    *label* is a human-readable name used in error messages
    (e.g. ``"VDC"`` or ``"Object-cert"``).
    """
    try:
        return keystore_api.get_certificate_chain()
    except Exception as e:
        status = getattr(e, 'status', None)
        if str(status) == '401':
            module.fail_json(
                msg="FC-222: authentication failed "
                "\u2014 %s" % str(e),
            )
        error_msg = (
            utils.determine_error(e)
            if hasattr(utils, 'determine_error')
            else str(e)
        )
        module.fail_json(
            msg="Failed to get current %s certificate "
            "chain: %s" % (label, error_msg),
        )
        return None


def apply_certificate(
    module, keystore_api, private_key,
    certificate_chain, label,
):
    """PUT the new key + chain, or fail.

    *label* is ``"VDC"`` or ``"Object-cert"``.
    """
    try:
        return keystore_api.set_key_certificate_pair(
            private_key, certificate_chain,
        )
    except Exception as e:
        status = getattr(e, 'status', None)
        if str(status) == '403':
            module.fail_json(
                msg=(
                    "FC-223: SECURITY_ADMIN role required"
                    " to update %s keystore" % label
                ),
            )
        if str(status) == '400':
            module.fail_json(
                msg="FC-220: invalid PEM input "
                "\u2014 %s" % str(e),
            )
        if str(status) == '409':
            module.fail_json(
                msg="FC-227: concurrent keystore "
                "update conflict",
            )
        error_msg = (
            utils.determine_error(e)
            if hasattr(utils, 'determine_error')
            else str(e)
        )
        module.fail_json(
            msg="Failed to set %s certificate: %s"
            % (label, error_msg),
        )
        return None


def verify_and_get_details(
    module, keystore_api, desired_fp, put_response,
):
    """Post-PUT verification and detail extraction."""
    try:
        verify = keystore_api.get_certificate_chain()
        verify_chain = verify.get('chain', '')
        verify_fp = (
            fingerprint_chain(verify_chain)
            if verify_chain else ''
        )
        if verify_fp != desired_fp:
            module.fail_json(
                msg=(
                    "FC-235: post-PUT chain fingerprint "
                    "mismatch (expected %s, got %s)"
                    % (desired_fp, verify_fp)
                ),
            )
            return None
        return parse_certificate_metadata(verify_chain)
    except Exception:
        new_chain = put_response.get('chain', '')
        return get_chain_metadata(new_chain, desired_fp)
