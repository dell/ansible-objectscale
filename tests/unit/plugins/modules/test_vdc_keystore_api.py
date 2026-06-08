# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api import (
    VdcKeystoreApi,
    fingerprint_chain,
    validate_pem_certificate,
    validate_pem_private_key,
    count_certificates,
    parse_certificate_metadata,
    _normalize_pem,
    _should_retry,
)

SAMPLE_CHAIN_PEM = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIUTestSerial0001\n"
    "dGVzdCBjZXJ0aWZpY2F0ZSBkYXRh\n"
    "-----END CERTIFICATE-----\n"
)

SAMPLE_KEY_PEM = (
    "-----BEGIN PRIVATE KEY-----\n"
    "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7\n"
    "dGVzdCBwcml2YXRlIGtleSBkYXRh\n"
    "-----END PRIVATE KEY-----\n"
)

MULTI_CHAIN_PEM = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIULeaf0001\n"
    "bGVhZiBjZXJ0IGRhdGE=\n"
    "-----END CERTIFICATE-----\n"
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIUInterm0002\n"
    "aW50ZXJtIGNlcnQgZGF0YQ==\n"
    "-----END CERTIFICATE-----\n"
)


class TestNormalizePem:

    def test_strips_whitespace(self):
        pem = "  -----BEGIN CERTIFICATE-----  \n  data  \n  -----END CERTIFICATE-----  \n"
        normalized = _normalize_pem(pem)
        assert not any(line.startswith(' ') for line in normalized.strip().splitlines())

    def test_consistent_output(self):
        fp1 = fingerprint_chain(SAMPLE_CHAIN_PEM)
        fp2 = fingerprint_chain(SAMPLE_CHAIN_PEM + "  \n\n")
        assert fp1 == fp2


class TestFingerprintChain:

    def test_returns_hex_string(self):
        fp = fingerprint_chain(SAMPLE_CHAIN_PEM)
        assert isinstance(fp, str)
        assert len(fp) == 64  # SHA-256 hex

    def test_different_chains_different_fingerprints(self):
        fp1 = fingerprint_chain(SAMPLE_CHAIN_PEM)
        fp2 = fingerprint_chain(MULTI_CHAIN_PEM)
        assert fp1 != fp2

    def test_same_chain_same_fingerprint(self):
        fp1 = fingerprint_chain(SAMPLE_CHAIN_PEM)
        fp2 = fingerprint_chain(SAMPLE_CHAIN_PEM)
        assert fp1 == fp2


class TestValidatePemCertificate:

    def test_valid_cert(self):
        assert validate_pem_certificate(SAMPLE_CHAIN_PEM) is True

    def test_invalid_cert(self):
        assert validate_pem_certificate("not a certificate") is False

    def test_multi_cert(self):
        assert validate_pem_certificate(MULTI_CHAIN_PEM) is True

    def test_empty_string(self):
        assert validate_pem_certificate("") is False


class TestValidatePemPrivateKey:

    def test_valid_key(self):
        assert validate_pem_private_key(SAMPLE_KEY_PEM) is True

    def test_rsa_key(self):
        rsa = SAMPLE_KEY_PEM.replace("PRIVATE KEY", "RSA PRIVATE KEY")
        assert validate_pem_private_key(rsa) is True

    def test_invalid_key(self):
        assert validate_pem_private_key("not a key") is False

    def test_empty_string(self):
        assert validate_pem_private_key("") is False

    def test_certificate_is_not_key(self):
        assert validate_pem_private_key(SAMPLE_CHAIN_PEM) is False


class TestCountCertificates:

    def test_single_cert(self):
        assert count_certificates(SAMPLE_CHAIN_PEM) == 1

    def test_multi_cert(self):
        assert count_certificates(MULTI_CHAIN_PEM) == 2

    def test_no_cert(self):
        assert count_certificates("no certs here") == 0


class TestParseCertificateMetadata:

    def test_basic_metadata(self):
        meta = parse_certificate_metadata(SAMPLE_CHAIN_PEM)
        assert 'fingerprint' in meta
        assert 'chain' in meta
        assert meta['chain_length'] == 1

    def test_multi_chain_metadata(self):
        meta = parse_certificate_metadata(MULTI_CHAIN_PEM)
        assert meta['chain_length'] == 2

    def test_no_cryptography(self):
        """Without cryptography, only basic fields are returned."""
        import importlib
        import sys
        # Temporarily block cryptography import to test fallback
        real_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

        def mock_import(name, *args, **kwargs):
            if name == 'cryptography' or name.startswith('cryptography.'):
                raise ImportError("mocked no cryptography")
            return real_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            meta = parse_certificate_metadata(SAMPLE_CHAIN_PEM)
        assert 'fingerprint' in meta
        assert meta['chain_length'] == 1


class TestShouldRetry:

    def test_429_retryable(self):
        assert _should_retry(429) is True

    def test_500_retryable(self):
        assert _should_retry(500) is True

    def test_503_retryable(self):
        assert _should_retry(503) is True

    def test_400_not_retryable(self):
        assert _should_retry(400) is False

    def test_403_not_retryable(self):
        assert _should_retry(403) is False

    def test_200_not_retryable(self):
        assert _should_retry(200) is False


def _make_api(status=200, data='{}'):
    """Create a VdcKeystoreApi with mocked rest client."""
    api_client_mock = MagicMock()
    api_client_mock.configuration.host = 'https://10.0.0.1:4443'
    api_client_mock.configuration.api_key = {'AuthToken': 'test-token'}

    resp_mock = MagicMock()
    resp_mock.status = status
    resp_mock.data = data
    api_client_mock.rest_client.request.return_value = resp_mock

    api = VdcKeystoreApi(api_client_mock, timeout=30)
    return api, api_client_mock


class TestVdcKeystoreApiGet:

    def test_get_returns_chain(self):
        data = json.dumps({'certificate_chain': {'chain': SAMPLE_CHAIN_PEM}})
        api, unused_client = _make_api(200, data)

        result = api.get_certificate_chain()

        assert result['chain'] == SAMPLE_CHAIN_PEM

    def test_get_404_raises(self):
        api, unused_client = _make_api(404, '')

        try:
            api.get_certificate_chain()
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 404

    def test_get_500_raises(self):
        api, client = _make_api()
        resp_500 = MagicMock(status=500, data='error')
        resp_200 = MagicMock(status=200, data=json.dumps({'certificate_chain': {'chain': 'pem'}}))
        # All attempts return 500
        client.rest_client.request.return_value = resp_500

        try:
            with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api.time.sleep'):
                api.get_certificate_chain()
            assert False, "Should have raised"
        except Exception:
            pass

    def test_get_invalid_json(self):
        api, unused_client = _make_api(200, 'not-json')

        try:
            api.get_certificate_chain()
            assert False, "Should have raised"
        except Exception as e:
            assert 'Invalid JSON' in str(e)


class TestVdcKeystoreApiPut:

    def test_put_calls_api(self):
        data = json.dumps({'certificate_chain': {'chain': SAMPLE_CHAIN_PEM}})
        api, client = _make_api(200, data)

        result = api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        assert result['chain'] == SAMPLE_CHAIN_PEM
        call_args = client.rest_client.request.call_args
        assert call_args[0][0] == 'PUT'
        body = json.loads(call_args[1].get('body', call_args[0][3] if len(call_args[0]) > 3 else '{}'))
        assert 'key_and_certificate' in body

    def test_put_400_raises(self):
        api, unused_client = _make_api(400, 'bad input')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 400

    def test_put_403_raises(self):
        api, unused_client = _make_api(403, 'forbidden')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 403

    def test_put_409_raises(self):
        api, unused_client = _make_api(409, 'conflict')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 409

    def test_put_invalid_json_response(self):
        api, unused_client = _make_api(200, 'not-json')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert 'Invalid JSON' in str(e)


class TestVdcKeystoreApiRetry:

    def test_retries_on_429(self):
        api, client = _make_api()
        resp_429 = MagicMock(status=429, data='rate limited')
        resp_200 = MagicMock(status=200, data=json.dumps({'certificate_chain': {'chain': 'pem'}}))
        client.rest_client.request.side_effect = [resp_429, resp_200]

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api.time.sleep') as mock_sleep:
            result = api.get_certificate_chain()

        assert result['chain'] == 'pem'
        mock_sleep.assert_called_once()

    def test_retries_on_500_then_success(self):
        api, client = _make_api()
        resp_500 = MagicMock(status=500, data='error')
        resp_200 = MagicMock(status=200, data=json.dumps({'certificate_chain': {'chain': 'ok'}}))
        client.rest_client.request.side_effect = [resp_500, resp_500, resp_200]

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api.time.sleep'):
            result = api.get_certificate_chain()

        assert result['chain'] == 'ok'

    def test_retry_exhausted_raises(self):
        api, client = _make_api()
        resp_500 = MagicMock(status=500, data='error')
        client.rest_client.request.return_value = resp_500

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api.time.sleep'):
            try:
                api.get_certificate_chain()
                assert False, "Should have raised"
            except Exception:
                pass

    def test_auth_token_in_headers(self):
        data = json.dumps({'certificate_chain': {'chain': 'pem'}})
        api, client = _make_api(200, data)

        api.get_certificate_chain()

        call_args = client.rest_client.request.call_args
        headers = call_args[1].get('headers', call_args[0][2] if len(call_args[0]) > 2 else {})
        assert headers.get('X-SDS-AUTH-TOKEN') == 'test-token'
