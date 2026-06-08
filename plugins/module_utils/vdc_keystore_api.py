# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""API wrapper for ObjectScale VDC Keystore operations.

Covers two distinct endpoints:
  - VDC Keystore:         GET/PUT /vdc/keystore        (VDCKeystoreService)
  - Object-cert Keystore: GET/PUT /object-cert/keystore (ObjectCertificateService)
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import hashlib
import json
import re
import time
from typing import Any, Dict, Optional, Tuple

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import (
        ApiException,
    )
except Exception:
    ApiException = Exception  # type: ignore[assignment,misc]

VDC_KEYSTORE_PATH = '/vdc/keystore'
OBJECT_CERT_KEYSTORE_PATH = '/object-cert/keystore'

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

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1
RETRY_CAP = 8


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


def _should_retry(status_code: int) -> bool:
    """Return True if the HTTP status code is retryable (429 or 5xx)."""
    return status_code == 429 or 500 <= status_code <= 599


class VdcKeystoreApi:
    """Wrapper around the ObjectScale VDC Keystore REST API."""

    def __init__(self, api_client: Any, timeout: int = 30) -> None:
        self.api_client = api_client
        self.timeout = timeout
        self._base_url = api_client.configuration.host

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[str] = None,
    ) -> Tuple[int, str]:
        """Make an HTTP request with retry logic for 429 / 5xx."""
        url = self._base_url + path
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        # Inject auth token
        api_key = self.api_client.configuration.api_key
        if api_key and 'AuthToken' in api_key:
            headers['X-SDS-AUTH-TOKEN'] = api_key['AuthToken']

        last_exception = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = self.api_client.rest_client.request(
                    method,
                    url,
                    headers=headers,
                    body=body,
                    _request_timeout=self.timeout,
                )
                if _should_retry(resp.status) and attempt < MAX_RETRIES:
                    delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_CAP)
                    time.sleep(delay)
                    continue
                return resp.status, resp.data if resp.data else ''
            except ApiException as exc:
                status = getattr(exc, 'status', 0) or 0
                if _should_retry(status) and attempt < MAX_RETRIES:
                    delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_CAP)
                    time.sleep(delay)
                    last_exception = exc
                    continue
                raise
        if last_exception is not None:
            raise last_exception
        raise RuntimeError("Unexpected retry exhaustion")  # pragma: no cover

    def get_certificate_chain(self) -> Dict[str, Any]:
        """GET /vdc/keystore — returns the current VDC certificate chain.

        Returns:
            dict with 'chain' key containing PEM certificate chain string.

        Raises:
            ApiException on HTTP errors after retries.
        """
        status, data = self._request('GET', VDC_KEYSTORE_PATH + '.json')
        if status == 404:
            raise ApiException(status=404, reason="VDC keystore not found")
        if status < 200 or status >= 300:
            raise ApiException(status=status, reason="GET /vdc/keystore failed: %s" % data)
        try:
            parsed = json.loads(data)
        except (json.JSONDecodeError, TypeError, ValueError):
            raise ApiException(status=status, reason="Invalid JSON response from GET /vdc/keystore")
        cert_chain = parsed.get('certificate_chain', {})
        chain = cert_chain.get('chain', '')
        return {'chain': chain}

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
        payload = json.dumps({
            'key_and_certificate': {
                'private_key': private_key,
                'certificate_chain': certificate_chain,
            }
        })
        status, data = self._request('PUT', VDC_KEYSTORE_PATH, body=payload)
        if status == 400:
            raise ApiException(status=400, reason="Invalid PEM input: %s" % data)
        if status == 403:
            raise ApiException(status=403, reason="SECURITY_ADMIN role required")
        if status == 409:
            raise ApiException(status=409, reason="Concurrent keystore update conflict")
        if status < 200 or status >= 300:
            raise ApiException(status=status, reason="PUT /vdc/keystore failed: %s" % data)
        try:
            parsed = json.loads(data)
        except (json.JSONDecodeError, TypeError, ValueError):
            raise ApiException(status=status, reason="Invalid JSON response from PUT /vdc/keystore")
        cert_chain = parsed.get('certificate_chain', {})
        chain = cert_chain.get('chain', '')
        return {'chain': chain}


class ObjectCertKeystoreApi:
    """Wrapper around the ObjectScale Object-cert Keystore REST API.

    Operates on the ``/object-cert/keystore`` endpoint which is distinct
    from the VDC keystore (``/vdc/keystore``).  Used by the
    ``vdc_certificate_chain`` and ``vdc_certificate_chain_info`` modules.
    """

    def __init__(self, api_client: Any, timeout: int = 30) -> None:
        self.api_client = api_client
        self.timeout = timeout
        self._base_url = api_client.configuration.host

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[str] = None,
    ) -> Tuple[int, str]:
        """Make an HTTP request with retry logic for 429 / 5xx."""
        url = self._base_url + path
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        api_key = self.api_client.configuration.api_key
        if api_key and 'AuthToken' in api_key:
            headers['X-SDS-AUTH-TOKEN'] = api_key['AuthToken']

        last_exception = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = self.api_client.rest_client.request(
                    method,
                    url,
                    headers=headers,
                    body=body,
                    _request_timeout=self.timeout,
                )
                if _should_retry(resp.status) and attempt < MAX_RETRIES:
                    delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_CAP)
                    time.sleep(delay)
                    continue
                return resp.status, resp.data if resp.data else ''
            except ApiException as exc:
                status_code = getattr(exc, 'status', 0) or 0
                if _should_retry(status_code) and attempt < MAX_RETRIES:
                    delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_CAP)
                    time.sleep(delay)
                    last_exception = exc
                    continue
                raise
        if last_exception is not None:
            raise last_exception
        raise RuntimeError("Unexpected retry exhaustion")  # pragma: no cover

    def get_certificate_chain(self) -> Dict[str, Any]:
        """GET /object-cert/keystore — returns the current object-cert chain.

        Returns:
            dict with 'chain' key containing PEM certificate chain string.

        Raises:
            ApiException on HTTP errors after retries.
        """
        status, data = self._request('GET', OBJECT_CERT_KEYSTORE_PATH + '.json')
        if status == 404:
            raise ApiException(status=404, reason="Object-cert keystore not found")
        if status < 200 or status >= 300:
            raise ApiException(
                status=status,
                reason="GET /object-cert/keystore failed: %s" % data,
            )
        try:
            parsed = json.loads(data)
        except (json.JSONDecodeError, TypeError, ValueError):
            raise ApiException(
                status=status,
                reason="Invalid JSON response from GET /object-cert/keystore",
            )
        cert_chain = parsed.get('certificate_chain', {})
        chain = cert_chain.get('chain', '')
        return {'chain': chain}

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
        payload = json.dumps({
            'key_and_certificate': {
                'private_key': private_key,
                'certificate_chain': certificate_chain,
            }
        })
        status, data = self._request('PUT', OBJECT_CERT_KEYSTORE_PATH, body=payload)
        if status == 400:
            raise ApiException(status=400, reason="Invalid PEM input: %s" % data)
        if status == 403:
            raise ApiException(status=403, reason="SECURITY_ADMIN role required")
        if status == 409:
            raise ApiException(status=409, reason="Concurrent keystore update conflict")
        if status < 200 or status >= 300:
            raise ApiException(
                status=status,
                reason="PUT /object-cert/keystore failed: %s" % data,
            )
        try:
            parsed = json.loads(data)
        except (json.JSONDecodeError, TypeError, ValueError):
            raise ApiException(
                status=status,
                reason="Invalid JSON response from PUT /object-cert/keystore",
            )
        cert_chain = parsed.get('certificate_chain', {})
        chain = cert_chain.get('chain', '')
        return {'chain': chain}
