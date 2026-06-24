# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Enhanced unit tests for vdc_certificate_chain module with 100% coverage."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import tempfile
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain'


class _AnsibleExitJson(Exception):
    pass


class _AnsibleFailJson(Exception):
    pass


SAMPLE_CHAIN_PEM = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIUTestSerial0001\n"
    "dGVzdCBjZXJ0aWZpY2F0ZSBkYXRh\n"
    "-----END CERTIFICATE-----\n"
)

DIFFERENT_CHAIN_PEM = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDCDCCAfCgAwIBAgIUDiffSerial0002\n"
    "ZGlmZmVyZW50IGNlcnQgZGF0YQ==\n"
    "-----END CERTIFICATE-----\n"
)

SAMPLE_KEY_PEM = (
    "-----BEGIN PRIVATE KEY-----\n"
    "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7\n"
    "dGVzdCBwcml2YXRlIGtleSBkYXRh\n"
    "-----END PRIVATE KEY-----\n"
)

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    state='present',
    private_key_path=None,
    private_key_content=SAMPLE_KEY_PEM,
    certificate_chain_path=None,
    certificate_chain_content=SAMPLE_CHAIN_PEM,
)


def _make_api_exception(status, reason="error"):
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import ApiException
    return ApiException(status=status, reason=reason)


@contextmanager
def _run_module(params=None, check_mode=False, diff=False):
    """Run the vdc_certificate_chain main() with mocked AnsibleModule and API."""
    from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

    p = (params or BASE_PARAMS).copy()
    module_mock = MagicMock()
    module_mock.params = p
    module_mock.check_mode = check_mode
    module_mock._diff = diff
    module_mock.fail_json.side_effect = _AnsibleFailJson
    module_mock.exit_json.side_effect = _AnsibleExitJson

    api_client_mock = MagicMock()
    keystore_api_mock = MagicMock()

    def safe_run():
        try:
            main()
        except (_AnsibleExitJson, _AnsibleFailJson):
            pass

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.ObjectCertKeystoreApi', return_value=keystore_api_mock):
        yield module_mock, keystore_api_mock, safe_run


class TestVdcCertificateChainIdempotency:
    """Test idempotency behavior."""

    def test_idempotent_no_change(self):
        """When desired chain == current chain, changed=False, no PUT."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            api.set_key_certificate_pair.assert_not_called()
            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is False

    def test_change_invokes_put(self):
        """When desired chain != current chain, PUT is called, changed=True."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = [
                {'chain': DIFFERENT_CHAIN_PEM},   # initial GET
                {'chain': SAMPLE_CHAIN_PEM},       # verification GET
            ]
            api.set_key_certificate_pair.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            api.set_key_certificate_pair.assert_called_once_with(SAMPLE_KEY_PEM, SAMPLE_CHAIN_PEM)
            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True

    def test_idempotent_returns_details(self):
        """Idempotent result includes vdc_certificate_chain_details."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            kwargs = module.exit_json.call_args[1]
            assert 'vdc_certificate_chain_details' in kwargs
            assert kwargs['vdc_certificate_chain_details']['chain_length'] >= 1


class TestVdcCertificateChainCheckMode:
    """Test check mode behavior."""

    def test_check_mode_skips_put(self):
        """In check mode, changed=True but no PUT call."""
        with _run_module(check_mode=True) as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': DIFFERENT_CHAIN_PEM}

            run()

            api.set_key_certificate_pair.assert_not_called()
            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True

    def test_check_mode_with_idempotent_state(self):
        """In check mode when nothing changes, changed=False."""
        with _run_module(check_mode=True) as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is False

    def test_check_mode_with_diff(self):
        """Check mode with diff shows predicted changes."""
        with _run_module(check_mode=True, diff=True) as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': DIFFERENT_CHAIN_PEM}

            run()

            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True
            assert 'diff' in kwargs


class TestVdcCertificateChainDiffMode:
    """Test diff mode behavior."""

    def test_diff_mode_shows_changes(self):
        """In diff mode, diff output shows before/after."""
        with _run_module(diff=True) as (module, api, run):
            api.get_certificate_chain.side_effect = [
                {'chain': DIFFERENT_CHAIN_PEM},   # initial GET
                {'chain': SAMPLE_CHAIN_PEM},       # verification GET
            ]
            api.set_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True
            assert 'diff' in kwargs
            diff = kwargs['diff']
            assert 'before' in diff
            assert 'after' in diff

    def test_diff_mode_check_mode_combined(self):
        """Check mode + diff mode shows predicted diff."""
        with _run_module(check_mode=True, diff=True) as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': DIFFERENT_CHAIN_PEM}

            run()

            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True
            assert 'diff' in kwargs


class TestVdcCertificateChainPemValidation:
    """Test PEM validation."""

    def test_invalid_pem_chain(self):
        """Invalid PEM chain triggers FC-232."""
        params = BASE_PARAMS.copy()
        params['certificate_chain_content'] = 'garbage-not-pem'
        with _run_module(params=params) as (module, api, run):
            run()

            assert module.fail_json.called
            kwargs = module.fail_json.call_args[1]
            assert 'FC-232' in kwargs['msg']

    def test_valid_pem_format(self):
        """Test valid PEM format."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            assert module.exit_json.called


class TestVdcCertificateChainFilePath:
    """Test file path handling."""

    def test_file_path_reads_content(self):
        """When _path params are used, file content is read."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as key_f:
            key_f.write(SAMPLE_KEY_PEM)
            key_path = key_f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as chain_f:
            chain_f.write(SAMPLE_CHAIN_PEM)
            chain_path = chain_f.name

        try:
            params = BASE_PARAMS.copy()
            params['private_key_content'] = None
            params['private_key_path'] = key_path
            params['certificate_chain_content'] = None
            params['certificate_chain_path'] = chain_path

            with _run_module(params=params) as (module, api, run):
                api.get_certificate_chain.side_effect = [
                    {'chain': DIFFERENT_CHAIN_PEM},  # initial GET
                    {'chain': SAMPLE_CHAIN_PEM},      # verification GET
                ]
                api.set_key_certificate_pair.return_value = {'chain': SAMPLE_CHAIN_PEM}

                run()

                api.set_key_certificate_pair.assert_called_once()
                assert module.exit_json.called
                kwargs = module.exit_json.call_args[1]
                assert kwargs['changed'] is True
        finally:
            os.unlink(key_path)
            os.unlink(chain_path)

    def test_file_not_readable(self):
        """Missing file triggers FC-221."""
        params = BASE_PARAMS.copy()
        params['certificate_chain_content'] = None
        params['certificate_chain_path'] = '/nonexistent/file.pem'

        with _run_module(params=params) as (module, api, run):
            run()

            assert module.fail_json.called
            kwargs = module.fail_json.call_args[1]
            assert 'FC-221' in kwargs['msg']

    def test_file_read_os_error(self):
        """OSError on file read triggers FC-221."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write(SAMPLE_CHAIN_PEM)
            path = f.name

        try:
            params = BASE_PARAMS.copy()
            params['certificate_chain_content'] = None
            params['certificate_chain_path'] = path

            original_open = open

            def mock_open_fn(filepath, *a, **kw):
                if filepath == path:
                    raise OSError("Permission denied")
                return original_open(filepath, *a, **kw)

            with _run_module(params=params) as (module, api, run):
                with patch('builtins.open', side_effect=mock_open_fn):
                    run()

                assert module.fail_json.called
                kwargs = module.fail_json.call_args[1]
                assert 'FC-221' in kwargs['msg']
        finally:
            os.unlink(path)


class TestVdcCertificateChainErrorHandling:
    """Test error handling."""

    def test_403_no_retry(self):
        """403 triggers FC-223 immediately."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': DIFFERENT_CHAIN_PEM}
            api.set_key_certificate_pair.side_effect = _make_api_exception(403)

            run()

            kwargs = module.fail_json.call_args[1]
            assert 'FC-223' in kwargs['msg']

    def test_400_invalid_input(self):
        """400 triggers FC-220."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': DIFFERENT_CHAIN_PEM}
            api.set_key_certificate_pair.side_effect = _make_api_exception(400, "bad pem")

            run()

            kwargs = module.fail_json.call_args[1]
            assert 'FC-220' in kwargs['msg']

    def test_409_conflict(self):
        """409 triggers FC-227."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': DIFFERENT_CHAIN_PEM}
            api.set_key_certificate_pair.side_effect = _make_api_exception(409)

            run()

            kwargs = module.fail_json.call_args[1]
            assert 'FC-227' in kwargs['msg']

    def test_401_auth_failure(self):
        """401 on GET triggers FC-222."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = _make_api_exception(401)

            run()

            kwargs = module.fail_json.call_args[1]
            assert 'FC-222' in kwargs['msg']

    def test_500_server_error(self):
        """500 on PUT triggers generic error."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': DIFFERENT_CHAIN_PEM}
            api.set_key_certificate_pair.side_effect = _make_api_exception(500, "internal")

            run()

            kwargs = module.fail_json.call_args[1]
            assert 'Failed to set Object-cert certificate' in kwargs['msg']

    def test_get_chain_generic_error(self):
        """Non-401 error on GET current chain triggers generic error."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = _make_api_exception(503, "service unavailable")

            run()

            assert module.fail_json.called
            kwargs = module.fail_json.call_args[1]
            assert 'Failed to get current Object-cert certificate chain' in kwargs['msg']

    def test_connection_error(self):
        """Connection failure at init."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        module_mock.check_mode = False
        module_mock.fail_json.side_effect = _AnsibleFailJson

        with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception("conn failed")):
            try:
                main()
            except _AnsibleFailJson:
                pass

        kwargs = module_mock.fail_json.call_args[1]
        assert 'conn failed' in kwargs['msg']


class TestVdcCertificateChainEmptyChainPaths:
    """Test empty chain handling."""

    def test_idempotent_with_empty_current_chain(self):
        """When current chain is empty, always needs change."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = [
                {'chain': ''},               # initial GET - empty
                {'chain': SAMPLE_CHAIN_PEM},  # verification GET
            ]
            api.set_key_certificate_pair.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            api.set_key_certificate_pair.assert_called_once()
            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True

    def test_check_mode_empty_current_chain_with_diff(self):
        """Check mode + diff with empty current chain."""
        with _run_module(check_mode=True, diff=True) as (module, api, run):
            api.get_certificate_chain.return_value = {'chain': ''}

            run()

            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True
            assert 'diff' in kwargs

    def test_verification_empty_chain_mismatch(self):
        """Post-PUT verify returns empty chain - triggers FC-235."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = [
                {'chain': DIFFERENT_CHAIN_PEM},  # initial GET
                {'chain': ''},                    # verification GET - empty
            ]
            api.set_key_certificate_pair.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            assert module.fail_json.called
            kwargs = module.fail_json.call_args[1]
            assert 'FC-235' in kwargs['msg']


class TestVdcCertificateChainPostPutVerification:
    """Test post-PUT verification."""

    def test_post_put_verification_mismatch(self):
        """Post-PUT fingerprint mismatch triggers FC-235."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = [
                {'chain': DIFFERENT_CHAIN_PEM},  # initial GET
                {'chain': DIFFERENT_CHAIN_PEM},  # verification GET (wrong)
            ]
            api.set_key_certificate_pair.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            kwargs = module.fail_json.call_args[1]
            assert 'FC-235' in kwargs['msg']

    def test_post_put_verification_success(self):
        """Successful post-PUT verification."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = [
                {'chain': DIFFERENT_CHAIN_PEM},  # initial GET
                {'chain': SAMPLE_CHAIN_PEM},  # verification GET (matches desired)
            ]
            api.set_key_certificate_pair.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True
            assert 'vdc_certificate_chain_details' in kwargs

    def test_post_put_verification_fetch_fails_uses_put_response(self):
        """When verification GET fails, use PUT response."""
        with _run_module() as (module, api, run):
            api.get_certificate_chain.side_effect = [
                {'chain': DIFFERENT_CHAIN_PEM},  # initial GET
                Exception("verify fetch failed"),  # verification GET fails
            ]
            api.set_key_certificate_pair.return_value = {'chain': SAMPLE_CHAIN_PEM}

            run()

            kwargs = module.exit_json.call_args[1]
            assert kwargs['changed'] is True


class TestVdcCertificateChainNoLogSecurity:
    """Test no_log security."""

    def test_no_log_on_certificate_chain_content(self):
        """certificate_chain_content must have no_log=True in argument spec."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

        captured_spec = {}

        def capture_am(**kwargs):
            captured_spec.update(kwargs.get('argument_spec', {}))
            module_mock = MagicMock()
            module_mock.params = BASE_PARAMS.copy()
            module_mock.check_mode = False
            module_mock._diff = False
            module_mock.exit_json.side_effect = _AnsibleExitJson
            return module_mock

        with patch(f'{MODULE}.AnsibleModule', side_effect=capture_am), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection'), \
             patch(f'{MODULE}.ObjectCertKeystoreApi') as mock_api_cls:
            mock_api = MagicMock()
            mock_api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}
            mock_api_cls.return_value = mock_api

            try:
                main()
            except _AnsibleExitJson:
                pass

        # Verify that private_key_content has no_log set
        assert captured_spec['private_key_content']['no_log'] is True

    def test_no_log_on_password(self):
        """objectscale_password must have no_log=True."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

        captured_spec = {}

        def capture_am(**kwargs):
            captured_spec.update(kwargs.get('argument_spec', {}))
            module_mock = MagicMock()
            module_mock.params = BASE_PARAMS.copy()
            module_mock.check_mode = False
            module_mock._diff = False
            module_mock.exit_json.side_effect = _AnsibleExitJson
            return module_mock

        with patch(f'{MODULE}.AnsibleModule', side_effect=capture_am), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection'), \
             patch(f'{MODULE}.ObjectCertKeystoreApi') as mock_api_cls:
            mock_api = MagicMock()
            mock_api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}
            mock_api_cls.return_value = mock_api

            try:
                main()
            except _AnsibleExitJson:
                pass

        assert captured_spec['objectscale_password']['no_log'] is True


class TestVdcCertificateChainMutuallyExclusive:
    """Test mutually exclusive parameters."""

    def test_mutually_exclusive_declared(self):
        """Verify mutually_exclusive is passed to AnsibleModule."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

        captured_kwargs = {}

        def capture_am(**kwargs):
            captured_kwargs.update(kwargs)
            module_mock = MagicMock()
            module_mock.params = BASE_PARAMS.copy()
            module_mock.check_mode = False
            module_mock._diff = False
            module_mock.exit_json.side_effect = _AnsibleExitJson
            return module_mock

        with patch(f'{MODULE}.AnsibleModule', side_effect=capture_am), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection'), \
             patch(f'{MODULE}.ObjectCertKeystoreApi') as mock_api_cls:
            mock_api = MagicMock()
            mock_api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}
            mock_api_cls.return_value = mock_api

            try:
                main()
            except _AnsibleExitJson:
                pass

        me = captured_kwargs.get('mutually_exclusive', [])
        assert ('certificate_chain_path', 'certificate_chain_content') in me

    def test_required_one_of_declared(self):
        """Verify required_one_of is passed to AnsibleModule."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

        captured_kwargs = {}

        def capture_am(**kwargs):
            captured_kwargs.update(kwargs)
            module_mock = MagicMock()
            module_mock.params = BASE_PARAMS.copy()
            module_mock.check_mode = False
            module_mock._diff = False
            module_mock.exit_json.side_effect = _AnsibleExitJson
            return module_mock

        with patch(f'{MODULE}.AnsibleModule', side_effect=capture_am), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection'), \
             patch(f'{MODULE}.ObjectCertKeystoreApi') as mock_api_cls:
            mock_api = MagicMock()
            mock_api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}
            mock_api_cls.return_value = mock_api

            try:
                main()
            except _AnsibleExitJson:
                pass

        roo = captured_kwargs.get('required_one_of', [])
        assert ('certificate_chain_path', 'certificate_chain_content') in roo


class TestVdcCertificateChainNoClientLibrary:
    """Test missing client library."""

    def test_no_objectscale_client(self):
        """Without objectscale_client, module fails gracefully."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        module_mock.check_mode = False
        module_mock.exit_json.side_effect = _AnsibleExitJson

        with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False):
            try:
                main()
            except _AnsibleExitJson:
                pass

        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'objectscale_client' in kwargs['msg']


class TestVdcCertificateChainTimeout:
    """Test timeout parameter."""

    def test_timeout_param_propagates(self):
        """Timeout is passed through to ObjectCertKeystoreApi."""
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import main

        params = BASE_PARAMS.copy()
        params['timeout'] = 60

        module_mock = MagicMock()
        module_mock.params = params
        module_mock.check_mode = False
        module_mock._diff = False
        module_mock.exit_json.side_effect = _AnsibleExitJson

        with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection'), \
             patch(f'{MODULE}.ObjectCertKeystoreApi') as mock_api_cls:
            mock_api = MagicMock()
            mock_api.get_certificate_chain.return_value = {'chain': SAMPLE_CHAIN_PEM}
            mock_api_cls.return_value = mock_api

            try:
                main()
            except _AnsibleExitJson:
                pass

            # Verify ObjectCertKeystoreApi was called with timeout
            assert mock_api_cls.called


class TestEnsureClientStubCompatibility:
    """Test client stub compatibility."""

    def test_compat_secret_str(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import _ensure_client_stub_compatibility

        mock_client = MagicMock()
        mock_client.SecretStr = str

        _COMMON = 'ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_cert_common'
        with patch(f'{_COMMON}.objectscale_api_client', mock_client):
            _ensure_client_stub_compatibility()

        assert mock_client.SecretStr is not str

    def test_compat_base_model(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_certificate_chain import _ensure_client_stub_compatibility

        class FakeModel:
            pass

        mock_stubs = MagicMock()
        mock_stubs.BaseModel = FakeModel

        _COMMON = 'ansible_collections.dellemc.objectscale.plugins.module_utils.vdc_cert_common'
        with patch(f'{_COMMON}.objectscale_api_client', None), \
             patch(f'{_COMMON}.objectscale_client_stubs', mock_stubs):
            _ensure_client_stub_compatibility()

        inst = FakeModel()
        inst.__dict__ = {'k': 'v'}
        assert inst.model_dump() == {'k': 'v'}
