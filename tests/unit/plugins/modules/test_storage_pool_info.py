# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    vdc_id=None,
    storage_pool_id=None,
    name=None,
)


def make_obj(params=None, has_client=True):
    from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.ObjectVarrayApi'):
        obj = StoragePoolInfo()

    obj.module = module_mock
    obj.storage_pool_api = MagicMock()
    return obj


class TestStoragePoolInfoInit:

    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        obj = StoragePoolInfo()

        assert obj.module is module_mock
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        StoragePoolInfo()

        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'objectscale_client' in kwargs['msg']


class TestStoragePoolInfoQueryModes:

    def test_list_all_storage_pools(self):
        obj = make_obj()
        response = MagicMock()
        p1 = MagicMock()
        p1.to_dict.return_value = {'id': 'sp1', 'name': 'sp1'}
        response.varray = [p1]
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = response

        result = obj.get_storage_pools()

        obj.storage_pool_api.object_varray_service_get_virtual_arrays.assert_called_once_with()
        assert result == [{'id': 'sp1', 'name': 'sp1'}]

    def test_list_storage_pools_for_vdc(self):
        obj = make_obj(params={**BASE_PARAMS, 'vdc_id': 'vdc-1'})
        response = MagicMock()
        p1 = MagicMock()
        p1.to_dict.return_value = {'id': 'sp1', 'name': 'sp1'}
        response.varray = [p1]
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = response

        result = obj.get_storage_pools()

        obj.storage_pool_api.object_varray_service_get_virtual_arrays.assert_called_once_with(vdc_id='vdc-1')
        assert result == [{'id': 'sp1', 'name': 'sp1'}]

    def test_get_storage_pool_by_id(self):
        obj = make_obj(params={**BASE_PARAMS, 'storage_pool_id': 'sp-1'})
        response = MagicMock()
        response.to_dict.return_value = {'id': 'sp-1', 'name': 'sp1'}
        obj.storage_pool_api.object_varray_service_get_virtual_array.return_value = response

        result = obj.get_storage_pools()

        obj.storage_pool_api.object_varray_service_get_virtual_array.assert_called_once_with(id='sp-1')
        assert result == [{'id': 'sp-1', 'name': 'sp1'}]

    def test_name_filter_client_side(self):
        obj = make_obj(params={**BASE_PARAMS, 'name': 'sp2'})
        response = MagicMock()
        p1 = MagicMock()
        p1.to_dict.return_value = {'id': 'sp1', 'name': 'sp1'}
        p2 = MagicMock()
        p2.to_dict.return_value = {'id': 'sp2', 'name': 'sp2'}
        response.varray = [p1, p2]
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = response

        result = obj.get_storage_pools()

        assert result == [{'id': 'sp2', 'name': 'sp2'}]

    def test_name_filter_no_match_returns_empty_list(self):
        obj = make_obj(params={**BASE_PARAMS, 'name': 'missing'})
        response = MagicMock()
        p1 = MagicMock()
        p1.to_dict.return_value = {'id': 'sp1', 'name': 'sp1'}
        response.varray = [p1]
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = response

        result = obj.get_storage_pools()

        assert result == []


class TestStoragePoolInfoErrors:

    def test_404_for_storage_pool_id_returns_clear_error(self):
        obj = make_obj(params={**BASE_PARAMS, 'storage_pool_id': 'missing'})
        err = Exception('not found')
        err.status = 404
        obj.storage_pool_api.object_varray_service_get_virtual_array.side_effect = err

        obj.get_storage_pools()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert "HTTP 404" in kwargs['msg']

    def test_invalid_vdc_returns_clear_error(self):
        obj = make_obj(params={**BASE_PARAMS, 'vdc_id': 'bad-vdc'})
        err = Exception('bad request')
        err.status = 400
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.side_effect = err

        obj.get_storage_pools()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert "does not exist or is invalid" in kwargs['msg']


class TestStoragePoolInfoSanitizationAndOutput:

    def test_sensitive_fields_are_masked(self):
        obj = make_obj()
        response = MagicMock()
        p1 = MagicMock()
        p1.to_dict.return_value = {
            'id': 'sp1',
            'name': 'sp1',
            'token': 'abc',
            'nested': {'password': 'secret'},
        }
        response.varray = [p1]
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = response

        result = obj.get_storage_pools()

        assert result[0]['token'] == '***'
        assert result[0]['nested']['password'] == '***'

    def test_perform_operation_always_changed_false(self):
        obj = make_obj()
        obj.get_storage_pools = MagicMock(return_value=[{'id': 'sp1'}])

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(changed=False, storage_pools=[{'id': 'sp1'}])

    def test_check_mode_supported(self):
        obj = make_obj()
        obj.module.check_mode = True
        obj.get_storage_pools = MagicMock(return_value=[])

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(changed=False, storage_pools=[])


class TestStoragePoolInfoMain:

    @patch(f'{MODULE}.StoragePoolInfo')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import main

        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()

        mock_obj.perform_module_operation.assert_called_once()
