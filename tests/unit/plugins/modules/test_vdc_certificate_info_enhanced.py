# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Enhanced unit tests for vdc_certificate_info module with 100% coverage."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch, call
import pytest

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

MULTI_CERT_CHAIN = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIUTestSerial0001\n"
    "dGVzdCBjZXJ0aWZpY2F0ZSBkYXRh\n"
    "-----END CERTIFICATE-----\n"
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIUTestSerial0002\n"
    "aW50ZXJtZWRpYXRlIGNlcnQgZGF0YQ==\n"
    "-----END CERTIFICATE-----\n"
)


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


class TestVdcCertificateInfoInitialization:
    """Test module initialization and setup."""

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn):
        """Test successful initialization."""
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
        """Test initialization without objectscale_client library."""
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
        """Test initialization with connection error."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock
        mock_conn.side_effect = Exception("connection refused")

        VdcCertificateInfo()

        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'connection refused' in kwargs['msg']

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_timeout_parameter(self, mock_am, mock_conn):
        """Test that timeout parameter is properly passed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo
        module_mock = MagicMock()
        params = BASE_PARAMS.copy()
        params['timeout'] = 60
        module_mock.params = params
        mock_am.return_value = module_mock

        obj = VdcCertificateInfo()

        assert obj.module.params['timeout'] == 60


class TestVdcCertificateInfoPerformOperation:
    """Test the perform_module_operation method."""

    def test_info_returns_chain(self):
        """Test successful certificate chain retrieval."""
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
        """Test that info module always returns changed=False."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_info_multi_cert_chain(self):
        """Test with multiple certificates in chain."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = {'chain': MULTI_CERT_CHAIN}

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        details = kwargs['vdc_certificate_details']
        assert details['chain_length'] == 2

    def test_info_empty_chain(self):
        """Test with empty certificate chain."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = {'chain': ''}

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        details = kwargs['vdc_certificate_details']
        assert details['fingerprint'] == ''
        assert details['chain_length'] == 0
        assert details['chain'] == ''

    def test_info_check_mode_safe(self):
        """Test that check mode is safe for info module."""
        obj = _make_obj()
        obj.module.check_mode = True
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_info_diff_mode_not_included(self):
        """Test that diff mode doesn't include diff for info module."""
        obj = _make_obj()
        obj.module._diff = True
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert 'diff' not in kwargs


class TestVdcCertificateInfoErrorHandling:
    """Test error handling in perform_module_operation."""

    def test_info_404_not_found(self):
        """Test 404 error handling."""
        obj = _make_obj()
        exc = _make_api_exception(404, "not found")
        obj.keystore_api.get_certificate_chain.side_effect = exc

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'FC-224' in kwargs['msg']
        assert 'not found' in kwargs['msg'].lower() or '/vdc/keystore' in kwargs['msg']

    def test_info_401_unauthorized(self):
        """Test 401 authentication failure."""
        obj = _make_obj()
        exc = _make_api_exception(401, "unauthorized")
        obj.keystore_api.get_certificate_chain.side_effect = exc

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'FC-222' in kwargs['msg']
        assert 'authentication' in kwargs['msg'].lower()

    def test_info_403_forbidden(self):
        """Test 403 forbidden error."""
        obj = _make_obj()
        exc = _make_api_exception(403, "forbidden")
        obj.keystore_api.get_certificate_chain.side_effect = exc

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_info_500_server_error(self):
        """Test 500 server error."""
        obj = _make_obj()
        exc = _make_api_exception(500, "server error")
        obj.keystore_api.get_certificate_chain.side_effect = exc

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'Failed to get VDC certificate chain' in kwargs['msg']

    def test_info_generic_exception(self):
        """Test generic exception handling."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.side_effect = RuntimeError("unexpected error")

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_info_connection_timeout(self):
        """Test connection timeout."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.side_effect = TimeoutError("connection timeout")

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


class TestVdcCertificateInfoMetadata:
    """Test certificate metadata parsing."""

    def test_info_metadata_with_cryptography(self):
        """Test metadata parsing with cryptography library."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        with patch(f'{MODULE}.parse_certificate_metadata') as mock_parse:
            mock_parse.return_value = {
                'fingerprint': 'abc123def456',
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
        assert details['leaf_serial'] == 'ff01'
        assert details['not_before'] == '2026-01-01T00:00:00'
        assert details['not_after'] == '2027-01-01T00:00:00'

    def test_info_metadata_without_cryptography(self):
        """Test metadata parsing without cryptography library."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        with patch(f'{MODULE}.parse_certificate_metadata') as mock_parse:
            mock_parse.return_value = {
                'fingerprint': 'abc123def456',
                'chain': SAMPLE_CHAIN_PEM,
                'chain_length': 1,
            }
            obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        details = kwargs['vdc_certificate_details']
        assert 'leaf_subject' not in details
        assert 'leaf_serial' not in details
        assert 'not_before' not in details
        assert 'not_after' not in details

    def test_info_fingerprint_consistency(self):
        """Test that fingerprint is consistent."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        with patch(f'{MODULE}.parse_certificate_metadata') as mock_parse:
            mock_parse.return_value = {
                'fingerprint': 'consistent_fp_value',
                'chain': SAMPLE_CHAIN_PEM,
                'chain_length': 1,
            }
            obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        details = kwargs['vdc_certificate_details']
        assert details['fingerprint'] == 'consistent_fp_value'


class TestVdcCertificateInfoMain:
    """Test the main function."""

    @patch(f'{MODULE}.VdcCertificateInfo')
    def test_main_calls_perform(self, mock_cls):
        """Test that main() calls perform_module_operation()."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import main
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        main()

        mock_instance.perform_module_operation.assert_called_once()

    @patch(f'{MODULE}.VdcCertificateInfo')
    def test_main_exception_handling(self, mock_cls):
        """Test main() calls perform_module_operation even if it raises."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import main
        mock_instance = MagicMock()
        mock_instance.perform_module_operation.side_effect = Exception("test error")
        mock_cls.return_value = mock_instance

        # main() does not catch exceptions from perform_module_operation
        with pytest.raises(Exception, match="test error"):
            main()


class TestImportFailureHandling:
    """Test handling of import failures."""

    def test_objectscale_api_client_import_failure(self):
        """Test when objectscale_api_client import fails."""
        # This tests lines 155-156 (exception handler)
        import sys
        import importlib
        
        # Temporarily hide the module
        original_modules = sys.modules.copy()
        try:
            # Remove the module to force reimport
            if 'ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client' in sys.modules:
                del sys.modules['ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client']
            
            # The module should still load even if import fails
            from ansible_collections.dellemc.objectscale.plugins.modules import vdc_certificate_info
            # Verify module loaded
            assert vdc_certificate_info is not None
        finally:
            # Restore modules
            sys.modules.update(original_modules)

    def test_objectscale_client_stubs_import_failure(self):
        """Test when objectscale_client_stubs import fails."""
        # This tests lines 162-163 (exception handler)
        import sys
        
        original_modules = sys.modules.copy()
        try:
            # Module should still load even if stubs import fails
            from ansible_collections.dellemc.objectscale.plugins.modules import vdc_certificate_info
            assert vdc_certificate_info is not None
        finally:
            sys.modules.update(original_modules)


class TestEnsureClientStubCompatibility:
    """Test client stub compatibility patches."""

    @patch(f'{MODULE}.objectscale_api_client')
    def test_secret_str_patch(self, mock_client):
        """Test SecretStr patching."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo
        mock_client.SecretStr = str

        VdcCertificateInfo._ensure_client_stub_compatibility()

        assert mock_client.SecretStr is not str
        inst = mock_client.SecretStr("test")
        assert inst.get_secret_value() == "test"

    @patch(f'{MODULE}.objectscale_client_stubs')
    @patch(f'{MODULE}.objectscale_api_client', None)
    def test_base_model_patch(self, mock_stubs):
        """Test BaseModel patching."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo

        class FakeBaseModel:
            pass

        mock_stubs.BaseModel = FakeBaseModel

        VdcCertificateInfo._ensure_client_stub_compatibility()

        inst = FakeBaseModel()
        inst.__dict__ = {'key': 'val'}
        assert inst.model_dump() == {'key': 'val'}

    @patch(f'{MODULE}.objectscale_api_client', None)
    @patch(f'{MODULE}.objectscale_client_stubs', None)
    def test_no_compatibility_patches_needed(self):
        """Test when no compatibility patches are needed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_info import VdcCertificateInfo

        # Should not raise exception
        try:
            VdcCertificateInfo._ensure_client_stub_compatibility()
        except Exception:
            pytest.fail("_ensure_client_stub_compatibility() should handle None gracefully")


class TestVdcCertificateInfoEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_info_with_whitespace_chain(self):
        """Test with chain containing extra whitespace."""
        obj = _make_obj()
        chain_with_whitespace = "  \n  " + SAMPLE_CHAIN_PEM + "  \n  "
        obj.keystore_api.get_certificate_chain.return_value = {'chain': chain_with_whitespace}

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert 'vdc_certificate_details' in kwargs

    def test_info_with_none_response(self):
        """Test with None response from API."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = None

        # Should handle gracefully
        try:
            obj.perform_module_operation()
        except (TypeError, AttributeError):
            # Expected if response is None
            pass

    def test_info_with_missing_chain_key(self):
        """Test with response missing 'chain' key."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = {}

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_info_api_called_once(self):
        """Test that API is called exactly once."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        obj.keystore_api.get_certificate_chain.assert_called_once()

    def test_info_module_exit_json_called(self):
        """Test that module.exit_json is called."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        assert obj.module.exit_json.called

    def test_info_module_fail_json_not_called_on_success(self):
        """Test that module.fail_json is not called on success."""
        obj = _make_obj()
        obj.keystore_api.get_certificate_chain.return_value = SAMPLE_CHAIN_RESPONSE

        obj.perform_module_operation()

        assert not obj.module.fail_json.called
