# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    provider_name=None,
    namespace='testns',
)

SAMPLE_GET_RAW = {
    'SAMLMetadataDocument': '<xml>metadata</xml>',
    'CreateDate': '2025-01-15T12:00:00Z',
    'ValidUntil': '2030-12-31T23:59:59Z',
}

SAMPLE_LIST_RAW = [
    {
        'Arn': 'urn:ecs:iam::testns:saml-provider/idp1',
        'CreateDate': '2025-01-15T12:00:00Z',
        'ValidUntil': '2030-12-31T23:59:59Z',
    },
    {
        'Arn': 'urn:ecs:iam::testns:saml-provider/idp2',
        'CreateDate': '2025-02-01T08:00:00Z',
        'ValidUntil': '2031-01-01T00:00:00Z',
    },
]


def make_info_obj(params=None, has_client=True):
    """Helper: return an IamIdentityProviderInfo instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import IamIdentityProviderInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = True
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamIdentityProviderInfo()

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
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import IamIdentityProviderInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamIdentityProviderInfo()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import IamIdentityProviderInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamIdentityProviderInfo()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import IamIdentityProviderInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('conn fail')):
            with patch(f'{MODULE}.IamApi'):
                IamIdentityProviderInfo()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn fail' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# get_provider_details
# ---------------------------------------------------------------------------

class TestGetProviderDetails:

    def test_success(self):
        obj = make_info_obj()
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        result = obj.get_provider_details('test-idp', 'testns')
        assert result is not None
        assert result['provider_name'] == 'test-idp'
        assert result['saml_metadata_document'] == '<xml>metadata</xml>'
        assert result['arn'] == 'urn:ecs:iam::testns:saml-provider/test-idp'

    def test_not_found(self):
        obj = make_info_obj()
        obj.iam_api.get_saml_provider.return_value = None
        obj.get_provider_details('missing-idp', 'testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'not found' in call_kwargs['msg']

    def test_failure(self):
        obj = make_info_obj()
        obj.iam_api.get_saml_provider.side_effect = Exception('api error')
        obj.get_provider_details('test-idp', 'testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True


# ---------------------------------------------------------------------------
# list_providers
# ---------------------------------------------------------------------------

class TestListProviders:

    def test_success(self):
        obj = make_info_obj()
        obj.iam_api.list_saml_providers.return_value = SAMPLE_LIST_RAW[:]
        result = obj.list_providers('testns')
        assert len(result) == 2
        assert result[0]['provider_name'] == 'idp1'
        assert result[1]['provider_name'] == 'idp2'

    def test_empty(self):
        obj = make_info_obj()
        obj.iam_api.list_saml_providers.return_value = []
        result = obj.list_providers('testns')
        assert result == []

    def test_failure(self):
        obj = make_info_obj()
        obj.iam_api.list_saml_providers.side_effect = Exception('list error')
        obj.list_providers('testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True


# ---------------------------------------------------------------------------
# perform_module_operation
# ---------------------------------------------------------------------------

class TestPerformModuleOperation:

    def test_with_provider_name(self):
        params = BASE_PARAMS.copy()
        params['provider_name'] = 'test-idp'
        obj = make_info_obj(params)
        obj.iam_api.get_saml_provider.return_value = SAMPLE_GET_RAW.copy()
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        assert len(call_kwargs['identity_providers']) == 1
        assert call_kwargs['identity_providers'][0]['provider_name'] == 'test-idp'

    def test_without_provider_name(self):
        obj = make_info_obj()
        obj.iam_api.list_saml_providers.return_value = SAMPLE_LIST_RAW[:]
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        assert len(call_kwargs['identity_providers']) == 2

    def test_get_not_found_exits(self):
        params = BASE_PARAMS.copy()
        params['provider_name'] = 'missing'
        obj = make_info_obj(params)
        obj.iam_api.get_saml_provider.return_value = None
        obj.perform_module_operation()
        # exit_json called with failed inside get_provider_details
        assert obj.module.exit_json.called


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestHelpers:

    def test_build_arn(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import IamIdentityProviderInfo
        arn = IamIdentityProviderInfo._build_arn('my-idp', 'my-ns')
        assert arn == 'urn:ecs:iam::my-ns:saml-provider/my-idp'

    def test_extract_name_from_arn(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import IamIdentityProviderInfo
        assert IamIdentityProviderInfo._extract_name_from_arn('urn:ecs:iam::ns1:saml-provider/test-idp') == 'test-idp'
        assert IamIdentityProviderInfo._extract_name_from_arn('') == ''
        assert IamIdentityProviderInfo._extract_name_from_arn(None) == ''
        assert IamIdentityProviderInfo._extract_name_from_arn('no-slash') == 'no-slash'

    def test_get_identity_provider_info_parameters(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import IamIdentityProviderInfo
        params = IamIdentityProviderInfo.get_identity_provider_info_parameters()
        assert 'provider_name' in params
        assert 'namespace' in params
        assert params['provider_name']['required'] is False


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

class TestMain:

    @patch(f'{MODULE}.IamIdentityProviderInfo')
    def test_main(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info import main
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        main()
        mock_instance.perform_module_operation.assert_called_once()

    @patch(f'{MODULE}.main')
    def test_name_main(self, mock_main):
        import importlib
        import ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info as mod
        with patch.object(mod, '__name__', '__main__'):
            exec(compile('if __name__ == "__main__": main()', '<test>', 'exec'),
                 {'__name__': '__main__', 'main': mock_main})
        mock_main.assert_called_once()


class TestImportFallback:

    def test_iam_api_import_error(self):
        """When IamApi cannot be imported, module-level fallback sets IamApi = None."""
        import sys
        import importlib

        original = sys.modules.get('ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api')
        sys.modules['ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api'] = None  # type: ignore
        try:
            import ansible_collections.dellemc.objectscale.plugins.modules.iam_identity_provider_info as mod
            importlib.reload(mod)
            assert mod.IamApi is None
        finally:
            if original is not None:
                sys.modules['ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api'] = original
            else:
                sys.modules.pop('ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api', None)
            importlib.reload(mod)
