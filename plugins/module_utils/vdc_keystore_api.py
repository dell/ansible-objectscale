# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""API wrapper for ObjectScale VDC Keystore operations.

Covers two distinct endpoints:
  - VDC Keystore:         GET/PUT /vdc/keystore        (VDCKeystoreService)
  - Object-cert Keystore: GET/PUT /object-cert/keystore (ObjectCertificateService)

This module provides thin wrapper classes that delegate to the generated
OpenAPI client classes in ``objectscale_client.api``.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import hashlib
import re
from typing import Any, Dict

from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import (
    ApiException,
    NotFoundException,
)

PEM_CERT_RE = re.compile(
    r'-----BEGIN\s+CERTIFICATE-----\s+\S[\s\S]*?-----END\s+CERTIFICATE-----',
    re.MULTILINE,
)
PEM_KEY_RE = re.compile(
    r'-----BEGIN\s+(?:RSA\s+)?(?:EC\s+)?PRIVATE\s+KEY-----'
    r'\s+\S[\s\S]*?'
    r'-----END\s+(?:RSA\s+)?(?:EC\s+)?PRIVATE\s+KEY-----',
    re.MULTILINE,
)


def _normalize_pem(pem_text: str) -> str:
    """Strip whitespace variations for consistent fingerprinting."""
    lines = []
    for line in pem_text.strip().splitlines():
        lines.append(line.strip())
    return '\n'.join(lines) + '\n'


def fingerprint_chain(chain_pem: str) -> str:
    """Return a SHA-256 hex digest of the normalised chain bytes."""
    normalized = _normalize_pem(chain_pem)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def validate_pem_certificate(pem_text: str) -> bool:
    """Check that *pem_text* contains at least one PEM certificate block."""
    return bool(PEM_CERT_RE.search(pem_text))


def validate_pem_private_key(pem_text: str) -> bool:
    """Check that *pem_text* contains a PEM private key block."""
    return bool(PEM_KEY_RE.search(pem_text))


def count_certificates(chain_pem: str) -> int:
    """Count the number of certificate blocks in a PEM chain."""
    return len(PEM_CERT_RE.findall(chain_pem))


def parse_certificate_metadata(chain_pem: str) -> Dict[str, Any]:
    """Extract certificate metadata if *cryptography* is available.

    Returns a dict with leaf_subject, leaf_serial, not_before, not_after, chain_length
    when cryptography is importable; otherwise returns only chain_length and fingerprint.
    """
    meta: Dict[str, Any] = {
        'fingerprint': fingerprint_chain(chain_pem),
        'chain': chain_pem,
        'chain_length': count_certificates(chain_pem),
    }

    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import serialization  # noqa: F401

        certs = PEM_CERT_RE.findall(chain_pem)
        if certs:
            leaf_pem = certs[0]
            leaf = x509.load_pem_x509_certificate(leaf_pem.encode('utf-8'))
            meta['leaf_subject'] = leaf.subject.rfc4514_string()
            meta['leaf_serial'] = format(leaf.serial_number, 'x')
            meta['not_before'] = leaf.not_valid_before_utc.isoformat()
            meta['not_after'] = leaf.not_valid_after_utc.isoformat()
    except ImportError:
        pass
    except Exception:
        pass

    return meta


class VdcKeystoreApi:
    """A wrapper class for ObjectScale VDC Keystore API calls.

    Delegates to the generated ``objectscale_client.api.vdc_keystore_api``
    client, following the same pattern as :class:`BucketApi`.
    """

    def __init__(self, api_client: Any, timeout: int = 30) -> None:
        """Initialize the VdcKeystoreApi with an authenticated API client."""
        self.api_client = api_client
        self.timeout = timeout

    def get_certificate_chain(self) -> Dict[str, Any]:
        """GET /vdc/keystore — returns the current VDC certificate chain.

        Returns:
            dict with 'chain' key containing PEM certificate chain string.

        Raises:
            ApiException on HTTP errors after retries.
        """
        try:
            from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import (
                vdc_keystore_api as generated_vdc_keystore_api,
            )
            api = generated_vdc_keystore_api.VdcKeystoreApi(self.api_client)
            response = api.vdc_keystore_service_get_certificate_chain(
                _request_timeout=self.timeout,
            )
            if response is None:
                return {'chain': ''}
            result = response.to_dict()
            cert_chain = result.get('certificate_chain', {})
            if cert_chain is None:
                cert_chain = {}
            chain = cert_chain.get('chain', '')
            return {'chain': chain if chain else ''}
        except NotFoundException:
            raise ApiException(status=404, reason="VDC keystore not found")
        except ApiException as e:
            if e.status == 404:
                raise ApiException(status=404, reason="VDC keystore not found")
            raise

    def set_key_certificate_pair(
        self,
        private_key: str,
        certificate_chain: str,
    ) -> Dict[str, Any]:
        """PUT /vdc/keystore — sets the VDC private key and certificate chain.

        Args:
            private_key: PEM-encoded private key.
            certificate_chain: PEM-encoded certificate chain.

        Returns:
            dict with 'chain' key containing the newly set PEM certificate chain.

        Raises:
            ApiException on HTTP errors.
        """
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import (
            vdc_keystore_api as generated_vdc_keystore_api,
        )
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.vdc_keystore_service_set_key_certificate_pair_request import (  # noqa: E501
            VdcKeystoreServiceSetKeyCertificatePairRequest,
        )
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.vdc_keystore_service_set_key_certificate_pair_request_key_and_certificate import (  # noqa: E501
            VdcKeystoreServiceSetKeyCertificatePairRequestKeyAndCertificate,
        )

        api = generated_vdc_keystore_api.VdcKeystoreApi(self.api_client)
        key_cert = VdcKeystoreServiceSetKeyCertificatePairRequestKeyAndCertificate(
            private_key=private_key,
            certificate_chain=certificate_chain,
        )
        request_body = VdcKeystoreServiceSetKeyCertificatePairRequest(
            key_and_certificate=key_cert,
        )
        response = api.vdc_keystore_service_set_key_certificate_pair(
            vdc_keystore_service_set_key_certificate_pair_request=request_body,
            _request_timeout=self.timeout,
        )
        if response is None:
            return {'chain': ''}
        result = response.to_dict()
        cert_chain = result.get('certificate_chain', {})
        if cert_chain is None:
            cert_chain = {}
        chain = cert_chain.get('chain', '')
        return {'chain': chain if chain else ''}


class ObjectCertKeystoreApi:
    """A wrapper class for ObjectScale Object-cert Keystore API calls.

    Operates on the ``/object-cert/keystore`` endpoint which is distinct
    from the VDC keystore (``/vdc/keystore``).  Used by the
    ``vdc_certificate_chain`` and ``vdc_certificate_chain_info`` modules.

    Delegates to the generated ``objectscale_client.api.object_certificate_api``
    client, following the same pattern as :class:`BucketApi`.
    """

    def __init__(self, api_client: Any, timeout: int = 30) -> None:
        """Initialize the ObjectCertKeystoreApi with an authenticated API client."""
        self.api_client = api_client
        self.timeout = timeout

    def get_certificate_chain(self) -> Dict[str, Any]:
        """GET /object-cert/keystore — returns the current object-cert chain.

        Returns:
            dict with 'chain' key containing PEM certificate chain string.

        Raises:
            ApiException on HTTP errors after retries.
        """
        try:
            from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import (
                object_certificate_api as generated_object_cert_api,
            )
            api = generated_object_cert_api.ObjectCertificateApi(self.api_client)
            response = api.object_certificate_service_get_certificate_chain(
                _request_timeout=self.timeout,
            )
            if response is None:
                return {'chain': ''}
            result = response.to_dict()
            cert_chain = result.get('certificate_chain', {})
            if cert_chain is None:
                cert_chain = {}
            chain = cert_chain.get('chain', '')
            return {'chain': chain if chain else ''}
        except NotFoundException:
            raise ApiException(status=404, reason="Object-cert keystore not found")
        except ApiException as e:
            if e.status == 404:
                raise ApiException(status=404, reason="Object-cert keystore not found")
            raise

    def set_key_certificate_pair(
        self,
        private_key: str,
        certificate_chain: str,
    ) -> Dict[str, Any]:
        """PUT /object-cert/keystore — sets the object-cert key and chain.

        Args:
            private_key: PEM-encoded private key.
            certificate_chain: PEM-encoded certificate chain.

        Returns:
            dict with 'chain' key containing the newly set PEM certificate chain.

        Raises:
            ApiException on HTTP errors.
        """
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import (
            object_certificate_api as generated_object_cert_api,
        )
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.object_certificate_service_set_key_certificate_pair_request import (  # noqa: E501
            ObjectCertificateServiceSetKeyCertificatePairRequest,
        )
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.object_certificate_service_set_key_certificate_pair_request_key_and_certificate import (  # noqa: E501
            ObjectCertificateServiceSetKeyCertificatePairRequestKeyAndCertificate,
        )

        api = generated_object_cert_api.ObjectCertificateApi(self.api_client)
        key_cert = ObjectCertificateServiceSetKeyCertificatePairRequestKeyAndCertificate(
            private_key=private_key,
            certificate_chain=certificate_chain,
        )
        request_body = ObjectCertificateServiceSetKeyCertificatePairRequest(
            key_and_certificate=key_cert,
        )
        response = api.object_certificate_service_set_key_certificate_pair(
            object_certificate_service_set_key_certificate_pair_request=request_body,
            _request_timeout=self.timeout,
        )
        if response is None:
            return {'chain': ''}
        result = response.to_dict()
        cert_chain = result.get('certificate_chain', {})
        if cert_chain is None:
            cert_chain = {}
        chain = cert_chain.get('chain', '')
        return {'chain': chain if chain else ''}
