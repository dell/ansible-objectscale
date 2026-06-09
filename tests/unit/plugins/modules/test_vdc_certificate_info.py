# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
)

SAMPLE_CHAIN_PEM = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIUTestSerial0001\n"
    "dGVzdCBjZXJ0aWZpY2F0ZSBkYXRh\n"
    "-----END CERTIFICATE-----\n"
)

SAMPLE_CHAIN_RESPONSE = {'chain': SAMPLE_CHAIN_PEM}


def _make_api_exception(status, reason="error"):
    """Create a mock ApiException with a status attribute."""
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import ApiException
    exc = ApiException(status=status, reason=reason)
    return exc


def _make_obj(params=None, has_client=True):
    """Create a VdcCertificateInfo instance with mocked dependencies."""
    from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock):
        obj = VdcCertificateInfo()

    obj.module = module_mock
    obj.keystore_api = MagicMock()
    return obj


class TestVdcCertificateInfoInit:

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        obj = VdcCertificateInfo()

        assert obj.module is module_mock
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        VdcCertificateInfo()

        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'objectscale_client' in kwargs['msg']

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock
        mock_conn.side_effect = Exception("connection refused")

        VdcCertificateInfo()

        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'connection refused' in kwargs['msg']


class TestVdcCertificateInfoPerformOperation:

    def test_info_returns_chain(self):
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert 'vdc_certificate_details' in kwargs
        details = kwargs['vdc_certificate_details']
        assert details['chain'] == SAMPLE_CHAIN_PEM
        assert details['chain_length'] == 1
        assert details['fingerprint'] != ''

    def test_info_changed_always_false(self):
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_info_404_fails(self):
        obj = _make_obj()
        exc = _make_api_exception(404, "not found")
        obj.keystore_api.get_certificate_chain.side_effect = exc

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'FC-224' in kwargs['msg']

    def test_info_401_fails(self):
        obj = _make_obj()
        exc = _make_api_exception(401, "unauthorized")
        obj.keystore_api.get_certificate_chain.side_effect = exc

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'FC-222' in kwargs['msg']

    def test_info_500_fails(self):
        obj = _make_obj()
        exc = _make_api_exception(500, "server error")
        obj.keystore_api.get_certificate_chain.side_effect = exc

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'Failed to get VDC certificate chain' in kwargs['msg']

    def test_info_generic_exception(self):
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.side_effect = RuntimeError("unexpected")

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_info_empty_chain(self):
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = {'chain': ''}

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        details = kwargs['vdc_certificate_details']
        assert details['fingerprint'] == ''
        assert details['chain_length'] == 0

    def test_info_check_mode_safe(self):
        obj = _make_obj()
        obj.module.check_mode = True
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_info_diff_unchanged(self):
        obj = _make_obj()
        obj.module._diff = True
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        # Info module should not include diff
        assert 'diff' not in kwargs

    def test_info_metadata_with_cryptography(self):
        """When cryptography is available, metadata fields are populated."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        with patch(f'{MODULE}.parse_certificate_metadata') as mock_parse:
            mock_parse.return_value = {
                'fingerprint': 'abc123',
                'chain': SAMPLE_CHAIN_PEM,
                'chain_length': 1,
                'leaf_subject': 'CN=test.example.com',
                'leaf_serial': 'ff01',
                'not_before': '2026-01-01T00:00:00',
                'not_after': '2027-01-01T00:00:00',
            }
            obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        details = kwargs['vdc_certificate_details']
        assert details['leaf_subject'] == 'CN=test.example.com'

    def test_info_metadata_without_cryptography(self):
        """When cryptography is not available, only basic fields are returned."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        with patch(f'{MODULE}.parse_certificate_metadata') as mock_parse:
            mock_parse.return_value = {
                'fingerprint': 'abc123',
                'chain': SAMPLE_CHAIN_PEM,
                'chain_length': 1,
            }
            obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        details = kwargs['vdc_certificate_details']
        assert 'leaf_subject' not in details


class TestVdcCertificateInfoMain:

    @patch(f'{MODULE}.VdcCertificateInfo')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import main
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        main()

        mock_instance.perform_module_operation.assert_called_once()


class TestEnsureClientStubCompatibility:

    @patch(f'{MODULE}.objectscale_api_client')
    def test_secret_str_patch(self, mock_client):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo
        mock_client.SecretStr = str

        VdcCertificateInfo._ensure_client_stub_compatibility()

        assert mock_client.SecretStr is not str
        inst = mock_client.SecretStr("test")
        assert inst.get_secret_value() == "test"

    @patch(f'{MODULE}.objectscale_client_stubs')
    @patch(f'{MODULE}.objectscale_api_client', None)
    def test_base_model_patch(self, mock_stubs):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo

        class FakeBaseModel:
            pass

        mock_stubs.BaseModel = FakeBaseModel

        VdcCertificateInfo._ensure_client_stub_compatibility()

        inst = FakeBaseModel()
        inst.__dict__ = {'key': 'val'}
        assert inst.model_dump() == {'key': 'val'}
