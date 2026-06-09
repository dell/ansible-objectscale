# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the vdc_keystore_api wrapper module.

Tests cover:
  - PEM utility helpers (normalize, fingerprint, validate, count, parse)
  - VdcKeystoreApi wrapper (GET/PUT via generated client)
  - ObjectCertKeystoreApi wrapper (GET/PUT via generated client)
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api import (
    VdcKeystoreApi,
    ObjectCertKeystoreApi,
    fingerprint_chain,
    validate_pem_certificate,
    validate_pem_private_key,
    count_certificates,
    parse_certificate_metadata,
    _normalize_pem,
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import (
    ApiException,
    NotFoundException,
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


# ---------------------------------------------------------------------------
# PEM utility helpers
# ---------------------------------------------------------------------------
class TestNormalizePem:

    def test_strips_whitespace(self):
        pem = "  -----BEGIN CERTIFICATE-----  \n  data  \n  -----END CERTIFICATE-----  \n"
        normalized = _normalize_pem(pem)
        assert not any(line.startswith(' ') for line in normalized.strip().splitlines())

    def test_consistent_output(self):
        fp1 = fingerprint_chain(SAMPLE_CHAIN_PEM)
        fp2 = fingerprint_chain(SAMPLE_CHAIN_PEM + "  \n\n")
        assert fp1 == fp2

    def test_ends_with_newline(self):
        result = _normalize_pem(SAMPLE_CHAIN_PEM)
        assert result.endswith('\n')


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
        real_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

        def mock_import(name, *args, **kwargs):
            if name == 'cryptography' or name.startswith('cryptography.'):
                raise ImportError("mocked no cryptography")
            return real_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            meta = parse_certificate_metadata(SAMPLE_CHAIN_PEM)
        assert 'fingerprint' in meta
        assert meta['chain_length'] == 1


# ---------------------------------------------------------------------------
# Helper to build a mock generated-client response
# ---------------------------------------------------------------------------
def _mock_get_response(chain_pem):
    """Build a mock response matching VdcKeystoreServiceGetCertificateChainResponse.to_dict()."""
    resp = MagicMock()
    resp.to_dict.return_value = {
        'certificate_chain': {'chain': chain_pem},
    }
    return resp


def _mock_get_response_none():
    """Simulate a None response from the generated client."""
    return None


# ---------------------------------------------------------------------------
# VdcKeystoreApi wrapper tests
# ---------------------------------------------------------------------------
class TestVdcKeystoreApiGet:

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_get_returns_chain(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_get_certificate_chain.return_value = _mock_get_response(SAMPLE_CHAIN_PEM)

        api = VdcKeystoreApi(MagicMock(), timeout=30)
        result = api.get_certificate_chain()

        assert result['chain'] == SAMPLE_CHAIN_PEM
        mock_gen.vdc_keystore_service_get_certificate_chain.assert_called_once()

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_get_returns_empty_on_none_response(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_get_certificate_chain.return_value = None

        api = VdcKeystoreApi(MagicMock(), timeout=30)
        result = api.get_certificate_chain()

        assert result == {'chain': ''}

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_get_returns_empty_on_none_chain(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        resp = MagicMock()
        resp.to_dict.return_value = {'certificate_chain': None}
        mock_gen.vdc_keystore_service_get_certificate_chain.return_value = resp

        api = VdcKeystoreApi(MagicMock(), timeout=30)
        result = api.get_certificate_chain()

        assert result == {'chain': ''}

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_get_404_raises(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_get_certificate_chain.side_effect = NotFoundException(status=404)

        api = VdcKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.get_certificate_chain()
        assert exc_info.value.status == 404

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_get_api_exception_404_raises(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_get_certificate_chain.side_effect = ApiException(status=404)

        api = VdcKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.get_certificate_chain()
        assert exc_info.value.status == 404

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_get_api_exception_500_propagates(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_get_certificate_chain.side_effect = ApiException(status=500)

        api = VdcKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.get_certificate_chain()
        assert exc_info.value.status == 500


class TestVdcKeystoreApiPut:

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_put_calls_api(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_set_key_certificate_pair.return_value = _mock_get_response(SAMPLE_CHAIN_PEM)

        api = VdcKeystoreApi(MagicMock(), timeout=30)
        result = api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        assert result['chain'] == SAMPLE_CHAIN_PEM
        mock_gen.vdc_keystore_service_set_key_certificate_pair.assert_called_once()

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_put_returns_empty_on_none(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_set_key_certificate_pair.return_value = None

        api = VdcKeystoreApi(MagicMock(), timeout=30)
        result = api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        assert result == {'chain': ''}

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_put_400_raises(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_set_key_certificate_pair.side_effect = ApiException(status=400)

        api = VdcKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
        assert exc_info.value.status == 400

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_put_403_raises(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_set_key_certificate_pair.side_effect = ApiException(status=403)

        api = VdcKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
        assert exc_info.value.status == 403

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_put_409_raises(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_set_key_certificate_pair.side_effect = ApiException(status=409)

        api = VdcKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
        assert exc_info.value.status == 409

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.vdc_keystore_api.VdcKeystoreApi'
    )
    def test_put_request_body_contents(self, mock_gen_cls):
        """Verify the request model is built with correct key and cert."""
        mock_gen = mock_gen_cls.return_value
        mock_gen.vdc_keystore_service_set_key_certificate_pair.return_value = _mock_get_response(SAMPLE_CHAIN_PEM)

        api = VdcKeystoreApi(MagicMock(), timeout=30)
        api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        call_args = mock_gen.vdc_keystore_service_set_key_certificate_pair.call_args
        # Python 3.7 compatibility: use [1] for kwargs dict
        kwargs_dict = call_args[1] if isinstance(call_args, tuple) else call_args.kwargs
        request_body = kwargs_dict.get('vdc_keystore_service_set_key_certificate_pair_request')
        if request_body is None:
            args_tuple = call_args[0] if isinstance(call_args, tuple) else call_args.args
            if args_tuple:
                request_body = args_tuple[0]
        assert request_body is not None
        assert request_body.key_and_certificate.private_key == SAMPLE_KEY_PEM
        assert request_body.key_and_certificate.certificate_chain == SAMPLE_CHAIN_PEM


# ---------------------------------------------------------------------------
# ObjectCertKeystoreApi wrapper tests
# ---------------------------------------------------------------------------
class TestObjectCertKeystoreApiGet:

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_get_returns_chain(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_get_certificate_chain.return_value = _mock_get_response(SAMPLE_CHAIN_PEM)

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)
        result = api.get_certificate_chain()

        assert result['chain'] == SAMPLE_CHAIN_PEM

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_get_returns_empty_on_none_response(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_get_certificate_chain.return_value = None

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)
        result = api.get_certificate_chain()

        assert result == {'chain': ''}

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_get_returns_empty_on_none_chain(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        resp = MagicMock()
        resp.to_dict.return_value = {'certificate_chain': None}
        mock_gen.object_certificate_service_get_certificate_chain.return_value = resp

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)
        result = api.get_certificate_chain()

        assert result == {'chain': ''}

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_get_404_not_found_raises(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_get_certificate_chain.side_effect = NotFoundException(status=404)

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.get_certificate_chain()
        assert exc_info.value.status == 404

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_get_api_exception_500_propagates(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_get_certificate_chain.side_effect = ApiException(status=500)

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.get_certificate_chain()
        assert exc_info.value.status == 500


class TestObjectCertKeystoreApiPut:

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_put_calls_api(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_set_key_certificate_pair.return_value = _mock_get_response(SAMPLE_CHAIN_PEM)

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)
        result = api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        assert result['chain'] == SAMPLE_CHAIN_PEM
        mock_gen.object_certificate_service_set_key_certificate_pair.assert_called_once()

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_put_returns_empty_on_none(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_set_key_certificate_pair.return_value = None

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)
        result = api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        assert result == {'chain': ''}

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_put_400_raises(self, mock_gen_cls):
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_set_key_certificate_pair.side_effect = ApiException(status=400)

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)

        with pytest.raises(ApiException) as exc_info:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
        assert exc_info.value.status == 400

    @patch(
        'ansible_collections.dellemc.objectscale.plugins.module_utils'
        '.objectscale_client.api.object_certificate_api.ObjectCertificateApi'
    )
    def test_put_request_body_contents(self, mock_gen_cls):
        """Verify the request model is built with correct key and cert."""
        mock_gen = mock_gen_cls.return_value
        mock_gen.object_certificate_service_set_key_certificate_pair.return_value = _mock_get_response(SAMPLE_CHAIN_PEM)

        api = ObjectCertKeystoreApi(MagicMock(), timeout=30)
        api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        call_args = mock_gen.object_certificate_service_set_key_certificate_pair.call_args
        # Python 3.7 compatibility: use [1] for kwargs dict
        kwargs_dict = call_args[1] if isinstance(call_args, tuple) else call_args.kwargs
        request_body = kwargs_dict.get('object_certificate_service_set_key_certificate_pair_request')
        if request_body is None:
            args_tuple = call_args[0] if isinstance(call_args, tuple) else call_args.args
            if args_tuple:
                request_body = args_tuple[0]
        assert request_body is not None
        assert request_body.key_and_certificate.private_key == SAMPLE_KEY_PEM
        assert request_body.key_and_certificate.certificate_chain == SAMPLE_CHAIN_PEM
