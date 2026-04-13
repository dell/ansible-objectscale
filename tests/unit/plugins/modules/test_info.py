# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    gather_subset=['namespace'],
)


def make_info_obj(params=None, has_client=True, conn_raises=None):
    """Helper: return an ObjectScaleInfo instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.info import ObjectScaleInfo

    module_mock = MagicMock()
    module_mock.params = params or PARAMS.copy()

    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection',
               side_effect=conn_raises if conn_raises else None,
               return_value=api_client_mock), \
         patch(f'{MODULE}.NamespaceApi'):
        obj = ObjectScaleInfo()

    obj.module = module_mock
    obj.namespace_api = MagicMock()
    return obj


class TestObjectScaleInfoInit:

    @patch(f'{MODULE}.NamespaceApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_ns_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.info import ObjectScaleInfo
        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module
        obj = ObjectScaleInfo()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.info import ObjectScaleInfo
        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module
        ObjectScaleInfo()
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.info import ObjectScaleInfo
        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn error")):
            ObjectScaleInfo()
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn error' in call_kwargs['msg']


class TestObjectScaleInfoGetNamespaces:

    def test_get_namespaces_success(self):
        obj = make_info_obj()
        ns1 = MagicMock()
        ns1.to_dict.return_value = {'id': 'ns1', 'name': 'ns1'}
        ns2 = MagicMock()
        ns2.to_dict.return_value = {'id': 'ns2', 'name': 'ns2'}
        response = MagicMock()
        response.namespace = [ns1, ns2]
        obj.namespace_api.namespace_service_get_namespaces.return_value = response

        result = obj.get_namespaces()

        assert result == [{'id': 'ns1', 'name': 'ns1'}, {'id': 'ns2', 'name': 'ns2'}]

    def test_get_namespaces_empty(self):
        obj = make_info_obj()
        response = MagicMock()
        response.namespace = None
        obj.namespace_api.namespace_service_get_namespaces.return_value = response

        result = obj.get_namespaces()

        assert result == []

    def test_get_namespaces_api_error(self):
        obj = make_info_obj()
        obj.namespace_api.namespace_service_get_namespaces.side_effect = Exception("API error")

        with patch(f'{UTILS}.determine_error', return_value='API error'):
            obj.get_namespaces()

        obj.module.exit_json.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'API error' in kwargs['msg']


class TestObjectScaleInfoPerformModuleOperation:

    def test_perform_with_namespace_subset(self):
        obj = make_info_obj()
        obj.module.params = {**PARAMS, 'gather_subset': ['namespace']}
        obj.get_namespaces = MagicMock(return_value=[{'id': 'ns1'}])

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(
            changed=False, Namespaces=[{'id': 'ns1'}]
        )

    def test_perform_without_namespace_subset(self):
        obj = make_info_obj()
        obj.module.params = {**PARAMS, 'gather_subset': []}
        obj.get_namespaces = MagicMock()

        obj.perform_module_operation()

        obj.get_namespaces.assert_not_called()
        obj.module.exit_json.assert_called_once_with(changed=False)


class TestInfoMain:

    @patch(f'{MODULE}.ObjectScaleInfo')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.info import main
        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()
        mock_obj.perform_module_operation.assert_called_once()
