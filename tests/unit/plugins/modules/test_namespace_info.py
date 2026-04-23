# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.namespace_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    namespace_name=None,
    match=None,
)


def make_obj(params=None, has_client=True):
    from ansible_collections.dellemc.objectscale.plugins.modules.namespace_info import NamespaceInfo

    module_mock = MagicMock()
    module_mock.params = params or PARAMS.copy()

    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.NamespaceApi'):
        obj = NamespaceInfo()

    obj.module = module_mock
    obj.namespace_api = MagicMock()
    return obj


class TestNamespaceInfoInit:

    @patch(f'{MODULE}.NamespaceApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_ns_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace_info import NamespaceInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        obj = NamespaceInfo()

        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace_info import NamespaceInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        NamespaceInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.NamespaceApi', None)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_namespace_api_unavailable(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace_info import NamespaceInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        NamespaceInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'namespace API client is unavailable' in kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace_info import NamespaceInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        with patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('conn failed')):
            NamespaceInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'Failed to connect to ObjectScale' in kwargs['msg']


class TestNamespaceInfoCompatibilityShim:

    def test_ensure_secretstr_compatibility_updates_secretstr_and_model_dump(self):
        obj = make_obj()

        fake_api_client = type('ApiClientStub', (), {'SecretStr': str})
        fake_base_model = type('BaseModelStub', (), {})
        fake_stubs = type('StubsStub', (), {'BaseModel': fake_base_model})

        with patch(f'{MODULE}.objectscale_api_client', fake_api_client), \
             patch(f'{MODULE}.objectscale_client_stubs', fake_stubs):
            obj._ensure_secretstr_compatibility()

            compat_secret = fake_api_client.SecretStr('secret')
            assert hasattr(compat_secret, 'get_secret_value')
            assert compat_secret.get_secret_value() == 'secret'

            model = fake_base_model()
            model.foo = 'bar'
            assert model.model_dump() == {'foo': 'bar'}


class TestNamespaceInfoReadOperations:

    def test_list_namespaces_success(self):
        obj = make_obj()
        ns1 = MagicMock()
        ns1.to_dict.return_value = {'id': 'ns1', 'name': 'ns1'}
        ns2 = MagicMock()
        ns2.to_dict.return_value = {'id': 'ns2', 'name': 'ns2'}
        response = MagicMock()
        response.to_dict.return_value = {'namespace': [ns1, ns2], 'NextMarker': None}
        obj.namespace_api.namespace_service_get_namespaces.return_value = response

        result = obj.list_namespaces()

        assert result == [{'id': 'ns1', 'name': 'ns1'}, {'id': 'ns2', 'name': 'ns2'}]

    def test_list_namespaces_with_match(self):
        obj = make_obj(params={
            **PARAMS,
            'match': 'team-*',
        })
        response = MagicMock()
        ns = MagicMock()
        ns.to_dict.return_value = {'id': 'team-a'}
        response.to_dict.return_value = {'namespace': [ns], 'NextMarker': None}
        obj.namespace_api.namespace_service_get_namespaces.return_value = response

        result = obj.list_namespaces()

        obj.namespace_api.namespace_service_get_namespaces.assert_called_once_with(
            name='team-*',
        )
        assert result == [{'id': 'team-a'}]

    def test_list_namespaces_error(self):
        obj = make_obj()
        obj.namespace_api.namespace_service_get_namespaces.side_effect = Exception('API error')

        with patch(f'{UTILS}.determine_error', return_value='API error'):
            obj.list_namespaces()

        obj.module.fail_json.assert_called_once()
        kwargs = obj.module.fail_json.call_args[1]
        assert 'API error' in kwargs['msg']

    def test_get_namespace_details_success(self):
        obj = make_obj()
        response = MagicMock()
        response.to_dict.return_value = {'id': 'ns1', 'name': 'ns1'}
        obj.namespace_api.namespace_service_get_namespace.return_value = response

        result = obj.get_namespace_details('ns1')

        assert result == {'id': 'ns1', 'name': 'ns1'}

    def test_get_namespace_details_not_found(self):
        obj = make_obj()
        err = Exception('not found')
        err.status = 404
        obj.namespace_api.namespace_service_get_namespace.side_effect = err

        result = obj.get_namespace_details('ns1')

        assert result is None

    def test_get_namespace_details_error(self):
        obj = make_obj()
        err = Exception('server error')
        err.status = 500
        obj.namespace_api.namespace_service_get_namespace.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_namespace_details('ns1')

        obj.module.fail_json.assert_called_once()
        kwargs = obj.module.fail_json.call_args[1]
        assert 'server error' in kwargs['msg']


class TestNamespaceInfoPerform:

    def test_perform_list(self):
        obj = make_obj()
        obj.module.params = PARAMS.copy()
        obj.list_namespaces = MagicMock(return_value=[{'id': 'ns1'}])

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(changed=False, namespaces=[{'id': 'ns1'}])

    def test_perform_get_by_name(self):
        obj = make_obj(params={**PARAMS, 'namespace_name': 'ns1'})
        obj.get_namespace_details = MagicMock(return_value={'id': 'ns1'})

        obj.perform_module_operation()

        obj.get_namespace_details.assert_called_once_with('ns1')
        obj.module.exit_json.assert_called_once_with(changed=False, namespaces=[{'id': 'ns1'}])

    def test_perform_get_by_name_not_found(self):
        obj = make_obj(params={**PARAMS, 'namespace_name': 'missing'})
        obj.get_namespace_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(changed=False, namespaces=[])


class TestNamespaceInfoMain:

    @patch(f'{MODULE}.NamespaceInfo')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace_info import main

        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj

        main()

        mock_obj.perform_module_operation.assert_called_once()
