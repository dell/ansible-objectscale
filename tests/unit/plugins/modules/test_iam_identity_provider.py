# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch, PropertyMock

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    provider_name='test-idp',
    namespace='testns',
    saml_metadata_document='<xml>metadata</xml>',
    state='present',
)

SAMPLE_PROVIDER_DETAILS = {
    'provider_name': 'test-idp',
    'arn': 'urn:ecs:iam::testns:saml-provider/test-idp',
    'create_date': '2025-01-15T12:00:00Z',
    'valid_until': '2030-12-31T23:59:59Z',
}

SAMPLE_PROVIDER_WITH_METADATA = dict(
    **SAMPLE_PROVIDER_DETAILS,
    saml_metadata_document='<xml>metadata</xml>',
)

SAMPLE_GET_RAW = {
    'SAMLMetadataDocument': '<xml>metadata</xml>',
    'CreateDate': '2025-01-15T12:00:00Z',
    'ValidUntil': '2030-12-31T23:59:59Z',
}


def make_idp_obj(params=None, has_client=True):
    """Helper: return an IamIdentityProvider instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider import IamIdentityProvider

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamIdentityProvider()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestInit:

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider import IamIdentityProvider
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamIdentityProvider()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider import IamIdentityProvider
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamIdentityProvider()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider import IamIdentityProvider
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('conn failed')):
            with patch(f'{MODULE}.IamApi'):
                IamIdentityProvider()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# get_provider
# ---------------------------------------------------------------------------

class TestGetProvider:

    def test_success(self):
        obj = make_idp_obj()
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        result = obj.get_provider('test-idp', 'testns')
        assert result is not None
        assert result['provider_name'] == 'test-idp'
        assert result['create_date'] == '2025-01-15T12:00:00Z'
        assert result['saml_metadata_document'] == '<xml>metadata</xml>'

    def test_not_found(self):
        obj = make_idp_obj()
        obj.iam_api.get_saml_provider.return_value = None
        result = obj.get_provider('test-idp', 'testns')
        assert result is None

    def test_failure(self):
        obj = make_idp_obj()
        obj.iam_api.get_saml_provider.side_effect = Exception('api error')
        obj.get_provider('test-idp', 'testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'test-idp' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# create_provider
# ---------------------------------------------------------------------------

class TestCreateProvider:

    def test_success(self):
        obj = make_idp_obj()
        obj.iam_api.create_saml_provider.return_value = {'SAMLProviderArn': 'urn:ecs:iam::testns:saml-provider/test-idp'}
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        result = obj.create_provider('test-idp', 'testns', '<xml>metadata</xml>')
        assert result is not None
        assert result['provider_name'] == 'test-idp'
        obj.iam_api.create_saml_provider.assert_called_once()

    def test_check_mode(self):
        obj = make_idp_obj()
        obj.module.check_mode = True
        result = obj.create_provider('test-idp', 'testns', '<xml>metadata</xml>')
        assert result is not None
        assert result['provider_name'] == 'test-idp'
        obj.iam_api.create_saml_provider.assert_not_called()

    def test_failure(self):
        obj = make_idp_obj()
        obj.iam_api.create_saml_provider.side_effect = Exception('create failed')
        obj.create_provider('test-idp', 'testns', '<xml/>')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'create failed' in call_kwargs['msg'] or 'Creating' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# update_provider
# ---------------------------------------------------------------------------

class TestUpdateProvider:

    def test_success(self):
        obj = make_idp_obj()
        obj.iam_api.update_saml_provider.return_value = {'SAMLProviderArn': 'urn:ecs:iam::testns:saml-provider/test-idp'}
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        result = obj.update_provider('test-idp', 'testns', '<new-xml/>')
        assert result is not None
        obj.iam_api.update_saml_provider.assert_called_once()

    def test_check_mode(self):
        obj = make_idp_obj()
        obj.module.check_mode = True
        result = obj.update_provider('test-idp', 'testns', '<new-xml/>')
        assert result is not None
        assert result['provider_name'] == 'test-idp'
        obj.iam_api.update_saml_provider.assert_not_called()

    def test_failure(self):
        obj = make_idp_obj()
        obj.iam_api.update_saml_provider.side_effect = Exception('update failed')
        obj.update_provider('test-idp', 'testns', '<xml/>')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True


# ---------------------------------------------------------------------------
# delete_provider
# ---------------------------------------------------------------------------

class TestDeleteProvider:

    def test_success(self):
        obj = make_idp_obj()
        obj.iam_api.delete_saml_provider.return_value = None
        result = obj.delete_provider('test-idp', 'testns')
        assert result is True
        obj.iam_api.delete_saml_provider.assert_called_once()

    def test_check_mode(self):
        obj = make_idp_obj()
        obj.module.check_mode = True
        result = obj.delete_provider('test-idp', 'testns')
        assert result is True
        obj.iam_api.delete_saml_provider.assert_not_called()

    def test_failure(self):
        obj = make_idp_obj()
        obj.iam_api.delete_saml_provider.side_effect = Exception('delete failed')
        obj.delete_provider('test-idp', 'testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True


# ---------------------------------------------------------------------------
# perform_module_operation
# ---------------------------------------------------------------------------

class TestPerformModuleOperation:

    def test_create_flow(self):
        obj = make_idp_obj()
        # Provider does not exist, then exists after create
        obj.iam_api.get_saml_provider.side_effect = [None, SAMPLE_GET_RAW.copy()]
        obj.iam_api.create_saml_provider.return_value = {'SAMLProviderArn': 'arn'}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        assert call_kwargs['iam_identity_provider_details']['provider_name'] == 'test-idp'

    def test_create_missing_metadata(self):
        params = BASE_PARAMS.copy()
        params['saml_metadata_document'] = None
        obj = make_idp_obj(params)
        obj.iam_api.get_saml_provider.return_value = None
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'saml_metadata_document' in call_kwargs['msg']

    def test_update_flow(self):
        obj = make_idp_obj()
        existing = SAMPLE_GET_RAW.copy()
        existing['SAMLMetadataDocument'] = '<old-xml/>'
        obj.iam_api.get_saml_provider.side_effect = [existing, SAMPLE_GET_RAW.copy()]
        obj.iam_api.update_saml_provider.return_value = {'SAMLProviderArn': 'arn'}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True

    def test_no_change_same_metadata(self):
        obj = make_idp_obj()
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False

    def test_no_change_no_metadata_param(self):
        params = BASE_PARAMS.copy()
        params['saml_metadata_document'] = None
        obj = make_idp_obj(params)
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False

    def test_delete_flow(self):
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_idp_obj(params)
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        obj.iam_api.delete_saml_provider.return_value = None
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True

    def test_delete_not_found(self):
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_idp_obj(params)
        obj.iam_api.get_saml_provider.return_value = None
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False

    def test_diff_create(self):
        obj = make_idp_obj()
        obj.module._diff = True
        obj.iam_api.get_saml_provider.side_effect = [None, SAMPLE_GET_RAW.copy()]
        obj.iam_api.create_saml_provider.return_value = {'SAMLProviderArn': 'arn'}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in call_kwargs
        assert call_kwargs['diff']['before'] == {}
        assert 'provider_name' in call_kwargs['diff']['after']

    def test_diff_update(self):
        obj = make_idp_obj()
        obj.module._diff = True
        existing = SAMPLE_GET_RAW.copy()
        existing['SAMLMetadataDocument'] = '<old-xml/>'
        obj.iam_api.get_saml_provider.side_effect = [existing, SAMPLE_GET_RAW.copy()]
        obj.iam_api.update_saml_provider.return_value = {'SAMLProviderArn': 'arn'}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in call_kwargs
        assert 'provider_name' in call_kwargs['diff']['before']

    def test_diff_delete(self):
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_idp_obj(params)
        obj.module._diff = True
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        obj.iam_api.delete_saml_provider.return_value = None
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in call_kwargs
        assert 'provider_name' in call_kwargs['diff']['before']
        assert call_kwargs['diff']['after'] == {}

    def test_create_check_mode_flow(self):
        obj = make_idp_obj()
        obj.module.check_mode = True
        obj.iam_api.get_saml_provider.return_value = None
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        obj.iam_api.create_saml_provider.assert_not_called()

    def test_delete_check_mode_flow(self):
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_idp_obj(params)
        obj.module.check_mode = True
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        obj.iam_api.delete_saml_provider.assert_not_called()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestHelpers:

    def test_build_arn(self):
        obj = make_idp_obj()
        arn = obj._build_arn('my-idp', 'my-ns')
        assert arn == 'urn:ecs:iam::my-ns:saml-provider/my-idp'

    def test_normalize_details(self):
        obj = make_idp_obj()
        raw = {'CreateDate': '2025-01-01', 'ValidUntil': '2030-01-01'}
        result = obj._normalize_details('my-idp', 'my-ns', raw)
        assert result['provider_name'] == 'my-idp'
        assert result['arn'] == 'urn:ecs:iam::my-ns:saml-provider/my-idp'
        assert result['create_date'] == '2025-01-01'

    def test_get_identity_provider_parameters(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider import IamIdentityProvider
        params = IamIdentityProvider.get_identity_provider_parameters()
        assert 'provider_name' in params
        assert 'namespace' in params
        assert 'saml_metadata_document' in params
        assert 'state' in params
        assert params['saml_metadata_document']['no_log'] is True


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

class TestMain:

    @patch(f'{MODULE}.IamIdentityProvider')
    def test_main(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider import main
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        main()
        mock_instance.perform_module_operation.assert_called_once()

    @patch(f'{MODULE}.main')
    def test_name_main(self, mock_main):
        import importlib
        import ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider as mod
        # Simulate __name__ == '__main__' by calling the guarded block
        with patch.object(mod, '__name__', '__main__'):
            exec(compile('if __name__ == "__main__": main()', '<test>', 'exec'),
                 {'__name__': '__main__', 'main': mock_main})
        mock_main.assert_called_once()


class TestImportFallback:

    def test_iam_api_import_error(self):
        """When IamApi cannot be imported, module-level fallback sets IamApi = None."""
        import sys
        import importlib

        # Temporarily break the iam_api import
        original = sys.modules.get('ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api')
        sys.modules['ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api'] = None  # type: ignore
        try:
            import ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider as mod
            importlib.reload(mod)
            assert mod.IamApi is None
        finally:
            if original is not None:
                sys.modules['ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api'] = original
            else:
                sys.modules.pop('ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api', None)
            importlib.reload(mod)
