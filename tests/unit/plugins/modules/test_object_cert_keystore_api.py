# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api import (
    ObjectCertKeystoreApi,
    OBJECT_CERT_KEYSTORE_PATH,
    fingerprint_chain,
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


def _make_api(status=200, data='{}'):
    """Create an ObjectCertKeystoreApi with mocked rest client."""
    api_client_mock = MagicMock()
    api_client_mock.configuration.host = 'https://10.0.0.1:4443'
    api_client_mock.configuration.api_key = {'AuthToken': 'test-token'}

    resp_mock = MagicMock()
    resp_mock.status = status
    resp_mock.data = data
    api_client_mock.rest_client.request.return_value = resp_mock

    api = ObjectCertKeystoreApi(api_client_mock, timeout=30)
    return api, api_client_mock


class TestObjectCertKeystoreApiGet:

    def test_get_returns_chain(self):
        data = json.dumps({'certificate_chain': {'chain': SAMPLE_CHAIN_PEM}})
        api, _ = _make_api(200, data)

        result = api.get_certificate_chain()

        assert result['chain'] == SAMPLE_CHAIN_PEM

    def test_get_uses_correct_endpoint(self):
        data = json.dumps({'certificate_chain': {'chain': SAMPLE_CHAIN_PEM}})
        api, client = _make_api(200, data)

        api.get_certificate_chain()

        call_args = client.rest_client.request.call_args
        url = call_args[0][1]
        assert '/object-cert/keystore' in url

    def test_get_404_raises(self):
        api, _ = _make_api(404, '')

        try:
            api.get_certificate_chain()
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 404

    def test_get_401_raises(self):
        api, _ = _make_api(401, 'unauthorized')

        try:
            api.get_certificate_chain()
            assert False, "Should have raised"
        except Exception:
            pass

    def test_get_500_retries_then_raises(self):
        api, client = _make_api()
        resp_500 = MagicMock(status=500, data='error')
        client.rest_client.request.return_value = resp_500

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api.time.sleep'):
            try:
                api.get_certificate_chain()
                assert False, "Should have raised"
            except Exception:
                pass

    def test_get_invalid_json(self):
        api, _ = _make_api(200, 'not-json')

        try:
            api.get_certificate_chain()
            assert False, "Should have raised"
        except Exception as e:
            assert 'Invalid JSON' in str(e)

    def test_get_empty_chain(self):
        data = json.dumps({'certificate_chain': {}})
        api, _ = _make_api(200, data)

        result = api.get_certificate_chain()

        assert result['chain'] == ''

    def test_get_multi_chain(self):
        data = json.dumps({'certificate_chain': {'chain': MULTI_CHAIN_PEM}})
        api, _ = _make_api(200, data)

        result = api.get_certificate_chain()

        assert result['chain'] == MULTI_CHAIN_PEM


class TestObjectCertKeystoreApiPut:

    def test_put_calls_api(self):
        data = json.dumps({'certificate_chain': {'chain': SAMPLE_CHAIN_PEM}})
        api, client = _make_api(200, data)

        result = api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        assert result['chain'] == SAMPLE_CHAIN_PEM
        call_args = client.rest_client.request.call_args
        assert call_args[0][0] == 'PUT'
        url = call_args[0][1]
        assert '/object-cert/keystore' in url

    def test_put_sends_correct_payload(self):
        data = json.dumps({'certificate_chain': {'chain': SAMPLE_CHAIN_PEM}})
        api, client = _make_api(200, data)

        api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)

        call_args = client.rest_client.request.call_args
        body = json.loads(call_args[1].get('body', call_args[0][3] if len(call_args[0]) > 3 else '{}'))
        assert 'key_and_certificate' in body
        assert 'private_key' in body['key_and_certificate']
        assert 'certificate_chain' in body['key_and_certificate']

    def test_put_400_raises(self):
        api, _ = _make_api(400, 'bad input')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 400

    def test_put_403_raises(self):
        api, _ = _make_api(403, 'forbidden')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 403

    def test_put_409_raises(self):
        api, _ = _make_api(409, 'conflict')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert getattr(e, 'status', None) == 409

    def test_put_invalid_json_response(self):
        api, _ = _make_api(200, 'not-json')

        try:
            api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            assert False, "Should have raised"
        except Exception as e:
            assert 'Invalid JSON' in str(e)

    def test_put_500_raises(self):
        api, client = _make_api()
        resp_500 = MagicMock(status=500, data='error')
        client.rest_client.request.return_value = resp_500

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api.time.sleep'):
            try:
                api.set_key_certificate_pair(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
                assert False, "Should have raised"
            except Exception:
                pass


class TestObjectCertKeystoreApiRetry:

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

    def test_503_retries(self):
        api, client = _make_api()
        resp_503 = MagicMock(status=503, data='unavailable')
        resp_200 = MagicMock(status=200, data=json.dumps({'certificate_chain': {'chain': 'ok'}}))
        client.rest_client.request.side_effect = [resp_503, resp_200]

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_keystore_api.time.sleep'):
            result = api.get_certificate_chain()

        assert result['chain'] == 'ok'

    def test_400_not_retried(self):
        api, client = _make_api(400, 'bad')

        try:
            api.get_certificate_chain()
            assert False, "Should have raised"
        except Exception:
            # Should be called exactly once — no retries for 400
            assert client.rest_client.request.call_count == 1
