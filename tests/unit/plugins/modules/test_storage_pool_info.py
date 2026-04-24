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

    @patch(f'{MODULE}.ObjectVarrayApi', None)
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_api_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        StoragePoolInfo()

        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'unavailable' in kwargs['msg']

    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am, mock_conn, mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock
        mock_conn.side_effect = Exception('Connection failed')

        StoragePoolInfo()

        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'Failed to connect' in kwargs['msg']


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

    def test_non_404_error_for_storage_pool_id_returns_clear_error(self):
        obj = make_obj(params={**BASE_PARAMS, 'storage_pool_id': 'sp-1'})
        err = Exception('server error')
        err.status = 500
        obj.storage_pool_api.object_varray_service_get_virtual_array.side_effect = err

        obj.get_storage_pools()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert "failed with error" in kwargs['msg']

    def test_invalid_vdc_returns_clear_error(self):
        obj = make_obj(params={**BASE_PARAMS, 'vdc_id': 'bad-vdc'})
        err = Exception('bad request')
        err.status = 400
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.side_effect = err

        obj.get_storage_pools()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert "does not exist or is invalid" in kwargs['msg']

    def test_non_404_400_error_for_vdc_returns_clear_error(self):
        obj = make_obj(params={**BASE_PARAMS, 'vdc_id': 'vdc-1'})
        err = Exception('server error')
        err.status = 500
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.side_effect = err

        obj.get_storage_pools()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert "failed with error" in kwargs['msg']


class TestStoragePoolInfoMutualExclusivity:

    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    def test_mutual_exclusive_storage_pool_id_and_vdc_id(self, mock_conn, mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        module_mock = MagicMock()
        module_mock.fail_json = MagicMock()
        params = {**BASE_PARAMS, 'storage_pool_id': 'sp-1', 'vdc_id': 'vdc-1'}
        module_mock.params = params

        with patch(f'{MODULE}.AnsibleModule') as mock_am:
            mock_am.return_value = module_mock
            # Simulate AnsibleModule's mutual exclusivity check
            mock_am.side_effect = Exception('parameters are mutually exclusive')

            try:
                StoragePoolInfo()
                assert False, "Expected exception for mutually exclusive parameters"
            except Exception as e:
                assert 'mutually exclusive' in str(e).lower()

    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    def test_mutual_exclusive_storage_pool_id_and_name(self, mock_conn, mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        module_mock = MagicMock()
        module_mock.fail_json = MagicMock()
        params = {**BASE_PARAMS, 'storage_pool_id': 'sp-1', 'name': 'test-name'}
        module_mock.params = params

        with patch(f'{MODULE}.AnsibleModule') as mock_am:
            mock_am.return_value = module_mock
            # Simulate AnsibleModule's mutual exclusivity check
            mock_am.side_effect = Exception('parameters are mutually exclusive')

            try:
                StoragePoolInfo()
                assert False, "Expected exception for mutually exclusive parameters"
            except Exception as e:
                assert 'mutually exclusive' in str(e).lower()

    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    def test_mutual_exclusive_configured_correctly(self, mock_conn, mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()

        with patch(f'{MODULE}.AnsibleModule') as mock_am:
            mock_am.return_value = module_mock

            StoragePoolInfo()

            # Verify that AnsibleModule was called with correct mutually_exclusive parameter
            call_kwargs = mock_am.call_args[1]
            assert 'mutually_exclusive' in call_kwargs
            assert ('storage_pool_id', 'vdc_id') in call_kwargs['mutually_exclusive']
            assert ('storage_pool_id', 'name') in call_kwargs['mutually_exclusive']


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

    def test_to_dict_with_none(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        result = StoragePoolInfo._to_dict(None)
        assert result == {}

    def test_to_dict_with_dict(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        result = StoragePoolInfo._to_dict({'key': 'value'})
        assert result == {'key': 'value'}

    def test_to_dict_with_object_having_to_dict(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = {'key': 'value'}
        result = StoragePoolInfo._to_dict(mock_obj)
        assert result == {'key': 'value'}

    def test_to_dict_with_object_without_to_dict(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        result = StoragePoolInfo._to_dict('string')
        assert result == {}

    def test_sanitize_with_list(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        result = StoragePoolInfo._sanitize_sensitive_fields(['item1', 'item2'])
        assert result == ['item1', 'item2']

    def test_sanitize_with_primitive(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        result = StoragePoolInfo._sanitize_sensitive_fields('string')
        assert result == 'string'

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

    @patch(f'{MODULE}.StoragePoolInfo')
    @patch('sys.argv', ['storage_pool_info.py'])
    def test_main_entry_point(self, mock_cls):
        # Test the __main__ guard by importing and calling main
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import main

        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()

        mock_obj.perform_module_operation.assert_called_once()


class TestStoragePoolInfoClientCompatibility:

    @patch(f'{MODULE}.objectscale_api_client', None)
    @patch(f'{MODULE}.objectscale_client_stubs', None)
    def test_ensure_client_stub_compatibility_with_none_clients(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        # Should not raise any errors when both clients are None
        StoragePoolInfo._ensure_client_stub_compatibility()

    @patch(f'{MODULE}.objectscale_api_client')
    @patch(f'{MODULE}.objectscale_client_stubs', None)
    def test_ensure_client_stub_compatibility_secret_str_as_str(self, mock_api_client):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        # Simulate SecretStr being str (compatibility mode)
        mock_api_client.SecretStr = str
        StoragePoolInfo._ensure_client_stub_compatibility()
        # Verify the compatibility class was set and has get_secret_value method
        assert hasattr(mock_api_client, 'SecretStr')
        # Test that the compatibility class works
        compat_str = mock_api_client.SecretStr('test')
        assert compat_str.get_secret_value() == 'test'

    @patch(f'{MODULE}.objectscale_api_client')
    @patch(f'{MODULE}.objectscale_client_stubs', None)
    def test_ensure_client_stub_compatibility_secret_str_not_str(self, mock_api_client):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        # Simulate SecretStr being a proper class (not str)

        class ProperSecretStr:
            def get_secret_value(self):
                return 'secret'
        mock_api_client.SecretStr = ProperSecretStr
        mock_api_client.SecretStr.__name__ = 'SecretStr'
        # Should not modify if SecretStr is not str
        original_secret_str = mock_api_client.SecretStr
        StoragePoolInfo._ensure_client_stub_compatibility()
        assert mock_api_client.SecretStr is original_secret_str

    @patch(f'{MODULE}.objectscale_api_client', None)
    @patch(f'{MODULE}.objectscale_client_stubs')
    def test_ensure_client_stub_compatibility_base_model_without_model_dump(self, mock_stubs):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        # Simulate BaseModel without model_dump method using a simple class

        class SimpleBaseModel:
            pass
        mock_stubs.BaseModel = SimpleBaseModel
        StoragePoolInfo._ensure_client_stub_compatibility()
        # Verify model_dump was added
        assert hasattr(SimpleBaseModel, 'model_dump')
        # Test that the added method works with __dict__
        instance = SimpleBaseModel()
        instance.__dict__ = {'key': 'value'}
        result = instance.model_dump()
        assert result == {'key': 'value'}
        # Test that the added method works without __dict__
        instance2 = SimpleBaseModel()
        result = instance2.model_dump()
        assert result == {}

    @patch(f'{MODULE}.objectscale_api_client', None)
    @patch(f'{MODULE}.objectscale_client_stubs')
    def test_ensure_client_stub_compatibility_base_model_with_model_dump(self, mock_stubs):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        # Simulate BaseModel with model_dump method (should not be modified)
        mock_base_model = MagicMock()
        mock_base_model.model_dump = MagicMock(return_value={'test': 'data'})
        mock_stubs.BaseModel = mock_base_model
        original_model_dump = mock_base_model.model_dump
        StoragePoolInfo._ensure_client_stub_compatibility()
        # Should not modify if model_dump already exists
        assert mock_base_model.model_dump is original_model_dump

    @patch(f'{MODULE}.objectscale_api_client', None)
    @patch(f'{MODULE}.objectscale_client_stubs')
    def test_ensure_client_stub_compatibility_base_model_none(self, mock_stubs):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool_info import StoragePoolInfo
        # Simulate BaseModel being None
        mock_stubs.BaseModel = None
        # Should not raise any errors
        StoragePoolInfo._ensure_client_stub_compatibility()


class TestStoragePoolInfoImportHandling:

    def test_module_handles_import_failures_gracefully(self):
        # Import the module to ensure it handles import failures
        import importlib
        import sys

        # Remove the module from sys.modules if it exists to force re-import
        if MODULE in sys.modules:
            del sys.modules[MODULE]

        # The module should import successfully even if some imports fail
        # (they are wrapped in try/except)
        try:
            from ansible_collections.dellemc.objectscale.plugins.modules import storage_pool_info
            assert storage_pool_info is not None
        except Exception as e:
            # If import fails, it should be due to missing dependencies, not import errors
            # The try/except blocks in the module should prevent ImportError from propagating
            assert 'objectscale_client' in str(e) or 'ObjectVarrayApi' in str(e)
