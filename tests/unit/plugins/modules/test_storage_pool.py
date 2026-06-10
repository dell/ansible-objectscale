# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
from ansible_collections.dellemc.objectscale.tests.unit.plugins.modules.mock_storage_pool_api import (
    SAMPLE_POOL_1,
    SAMPLE_POOL_UPDATED,
    make_list_response,
    make_update_response,
    make_api_error,
    make_pool_mock,
)

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.storage_pool'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    storage_pool_name='sp_default',
    description=None,
    is_cold_storage_enabled=None,
    is_protected=None,
    warning_alert_at=None,
    error_alert_at=None,
    critical_alert_at=None,
    state='present',
)


def make_obj(params=None, has_client=True):
    """Create a StoragePool object with mocked dependencies."""
    from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.ObjectVarrayApi'), \
         patch(f'{MODULE}.ObjectVarrayServiceUpdateVirtualArrayRequest'):
        obj = StoragePool()

    obj.module = module_mock
    obj.storage_pool_api = MagicMock()
    return obj


# ===========================================================================
# Initialization tests
# ===========================================================================
class TestStoragePoolInit:

    @patch(f'{MODULE}.ObjectVarrayServiceUpdateVirtualArrayRequest')
    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_api, mock_req):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        obj = StoragePool()
        assert obj.module is module_mock
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        StoragePool()
        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'objectscale_client' in kwargs['msg']

    @patch(f'{MODULE}.ObjectVarrayApi', None)
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_api_class(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock

        StoragePool()
        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'unavailable' in kwargs['msg']

    @patch(f'{MODULE}.ObjectVarrayServiceUpdateVirtualArrayRequest')
    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am, mock_conn, mock_api, mock_req):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        module_mock = MagicMock()
        module_mock.params = BASE_PARAMS.copy()
        mock_am.return_value = module_mock
        mock_conn.side_effect = Exception('Connection failed')

        StoragePool()
        kwargs = module_mock.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'Failed to connect' in kwargs['msg']


# ===========================================================================
# Get storage pool details tests
# ===========================================================================
class TestGetStoragePoolDetails:

    def test_get_pool_found(self):
        obj = make_obj()
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])

        result = obj.get_storage_pool_details('sp_default')
        assert result is not None
        assert result['name'] == 'sp_default'

    def test_get_pool_not_found(self):
        obj = make_obj()
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([])

        result = obj.get_storage_pool_details('nonexistent')
        assert result is None

    def test_get_pool_api_error(self):
        obj = make_obj()
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.side_effect = \
            make_api_error(500, '{"description": "Internal error"}')

        obj.get_storage_pool_details('sp_default')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'failed with error' in kwargs['msg']


# ===========================================================================
# Idempotency tests
# ===========================================================================
class TestIdempotency:

    def test_no_modify_when_all_match(self):
        obj = make_obj()
        current = dict(SAMPLE_POOL_1)
        # Params match current state
        obj.module.params['description'] = current['description']
        obj.module.params['is_cold_storage_enabled'] = current['isColdStorageEnabled']
        obj.module.params['warning_alert_at'] = current['warningAlertAt']
        obj.module.params['error_alert_at'] = current['errorAlertAt']
        obj.module.params['critical_alert_at'] = current['criticalAlertAt']
        assert obj.is_modify_required(current) is False

    def test_modify_when_description_differs(self):
        obj = make_obj()
        current = dict(SAMPLE_POOL_1)
        obj.module.params['description'] = 'New description'
        assert obj.is_modify_required(current) is True

    def test_modify_when_cold_storage_differs(self):
        obj = make_obj()
        current = dict(SAMPLE_POOL_1)
        obj.module.params['is_cold_storage_enabled'] = True
        assert obj.is_modify_required(current) is True

    def test_no_modify_when_no_params_specified(self):
        obj = make_obj()
        current = dict(SAMPLE_POOL_1)
        # All optional params are None (default)
        assert obj.is_modify_required(current) is False

    def test_modify_when_warning_alert_differs(self):
        obj = make_obj()
        current = dict(SAMPLE_POOL_1)
        obj.module.params['warning_alert_at'] = 60
        assert obj.is_modify_required(current) is True


# ===========================================================================
# Update operation tests
# ===========================================================================
class TestUpdateOperations:

    def test_update_success(self):
        obj = make_obj()
        obj.module.params['description'] = 'Updated by Ansible'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])
        obj.storage_pool_api.object_varray_service_update_virtual_array.return_value = \
            make_update_response()

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert kwargs['storage_pool_details'] is not None

    def test_update_idempotent_no_change(self):
        obj = make_obj()
        # No params specified = no change needed
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_update_pool_not_found(self):
        obj = make_obj()
        obj.module.params['description'] = 'New desc'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([])

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'not found' in kwargs['msg']

    def test_update_api_error_404(self):
        obj = make_obj()
        obj.module.params['description'] = 'Updated'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])
        obj.storage_pool_api.object_varray_service_update_virtual_array.side_effect = \
            make_api_error(404)

        obj.perform_module_operation()
        # First exit_json call is the error from modify_storage_pool
        kwargs = obj.module.exit_json.call_args_list[0][1]
        assert kwargs['failed'] is True
        assert '404' in kwargs['msg']

    def test_update_api_error_403(self):
        obj = make_obj()
        obj.module.params['description'] = 'Updated'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])
        obj.storage_pool_api.object_varray_service_update_virtual_array.side_effect = \
            make_api_error(403)

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args_list[0][1]
        assert kwargs['failed'] is True
        assert 'SYSTEM_ADMIN' in kwargs['msg']

    def test_update_api_error_401(self):
        obj = make_obj()
        obj.module.params['description'] = 'Updated'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])
        obj.storage_pool_api.object_varray_service_update_virtual_array.side_effect = \
            make_api_error(401)

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args_list[0][1]
        assert kwargs['failed'] is True
        assert '401' in kwargs['msg']

    def test_update_api_error_500(self):
        obj = make_obj()
        obj.module.params['description'] = 'Updated'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])
        obj.storage_pool_api.object_varray_service_update_virtual_array.side_effect = \
            make_api_error(500, '{"description": "Internal error"}')

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args_list[0][1]
        assert kwargs['failed'] is True
        assert 'failed with error' in kwargs['msg']


# ===========================================================================
# Validation tests
# ===========================================================================
class TestValidation:

    def test_alert_threshold_out_of_range(self):
        obj = make_obj()
        obj.module.params['warning_alert_at'] = 150
        obj._validate_alert_thresholds()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'between -1 and 100' in kwargs['msg']

    def test_alert_threshold_negative_out_of_range(self):
        obj = make_obj()
        obj.module.params['warning_alert_at'] = -2
        obj._validate_alert_thresholds()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'between -1 and 100' in kwargs['msg']

    def test_warning_must_be_less_than_error(self):
        obj = make_obj()
        obj.module.params['warning_alert_at'] = 90
        obj.module.params['error_alert_at'] = 85
        obj._validate_alert_thresholds()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'less than error_alert_at' in kwargs['msg']

    def test_error_must_be_less_than_critical(self):
        obj = make_obj()
        obj.module.params['error_alert_at'] = 95
        obj.module.params['critical_alert_at'] = 90
        obj._validate_alert_thresholds()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'less than critical_alert_at' in kwargs['msg']

    def test_valid_alert_thresholds(self):
        obj = make_obj()
        obj.module.params['warning_alert_at'] = 70
        obj.module.params['error_alert_at'] = 85
        obj.module.params['critical_alert_at'] = 95
        obj._validate_alert_thresholds()
        # Should not call exit_json (no failure)
        obj.module.exit_json.assert_not_called()

    def test_minus_one_is_valid(self):
        obj = make_obj()
        obj.module.params['warning_alert_at'] = -1
        obj._validate_alert_thresholds()
        obj.module.exit_json.assert_not_called()


# ===========================================================================
# Check mode tests
# ===========================================================================
class TestCheckMode:

    def test_check_mode_reports_change(self):
        obj = make_obj()
        obj.module.check_mode = True
        obj.module.params['description'] = 'Check mode change'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert 'check mode' in kwargs.get('msg', '')

    def test_check_mode_no_api_call(self):
        obj = make_obj()
        obj.module.check_mode = True
        obj.module.params['description'] = 'Check mode change'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([SAMPLE_POOL_1])

        obj.perform_module_operation()
        obj.storage_pool_api.object_varray_service_update_virtual_array.assert_not_called()


# ===========================================================================
# Security tests
# ===========================================================================
class TestSecurity:

    def test_sanitize_sensitive_fields(self):
        data = {
            'name': 'sp_default',
            'password': 'super_secret',
            'token': 'my_token',
            'nested': {
                'secret': 'hidden',
                'safe': 'visible',
            }
        }
        result = StoragePool._sanitize_sensitive_fields(data)
        assert result['name'] == 'sp_default'
        assert result['password'] == '***'
        assert result['token'] == '***'
        assert result['nested']['secret'] == '***'
        assert result['nested']['safe'] == 'visible'

    def test_sanitize_list_data(self):
        data = [{'password': 'secret', 'name': 'test'}]
        result = StoragePool._sanitize_sensitive_fields(data)
        assert result[0]['password'] == '***'
        assert result[0]['name'] == 'test'


# ===========================================================================
# Helper method tests
# ===========================================================================
class TestHelperMethods:

    def test_to_dict_none(self):
        assert StoragePool._to_dict(None) == {}

    def test_to_dict_dict_input(self):
        d = {'key': 'value'}
        assert StoragePool._to_dict(d) == d

    def test_to_dict_model_input(self):
        mock = MagicMock()
        mock.to_dict.return_value = {'id': 'test'}
        assert StoragePool._to_dict(mock) == {'id': 'test'}

    def test_to_dict_unknown_type(self):
        assert StoragePool._to_dict(42) == {}

    def test_get_pool_by_id_not_found(self):
        obj = make_obj()
        obj.storage_pool_api.object_varray_service_get_virtual_array.side_effect = \
            make_api_error(404)
        obj._get_storage_pool_by_id('urn:storageos:VirtualArray:missing')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert '404' in kwargs['msg']

    def test_get_pool_by_id_success(self):
        obj = make_obj()
        obj.storage_pool_api.object_varray_service_get_virtual_array.return_value = \
            make_pool_mock(SAMPLE_POOL_1)
        result = obj._get_storage_pool_by_id(SAMPLE_POOL_1['id'])
        assert result['name'] == 'sp_default'

    def test_no_pool_id_present(self):
        obj = make_obj()
        pool_no_id = dict(SAMPLE_POOL_1)
        del pool_no_id['id']
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([pool_no_id])

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        # Should still work - pool found but no id means error
        assert kwargs['failed'] is True or kwargs['changed'] is False


# ===========================================================================
# Build API payload tests
# ===========================================================================
class TestBuildApiPayload:

    def test_payload_model_cls_none(self):
        """When model_cls is None, return filtered dict."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        result = StoragePool._build_api_payload(None, {'a': 1, 'b': None, 'c': 3})
        assert result == {'a': 1, 'c': 3}

    def test_payload_stub_mode(self):
        """When model inherits from _stubs.BaseModel, return filtered dict."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

        class FakeStubBase:
            __module__ = 'objectscale_client._stubs'

        class FakeModel(FakeStubBase):
            pass

        result = StoragePool._build_api_payload(FakeModel, {'name': 'test', 'empty': None})
        assert result == {'name': 'test'}

    def test_payload_pydantic_model_validate(self):
        """When model_cls has model_validate, use it."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

        class FakeBase:
            __module__ = 'some.other.module'

        class FakeModel(FakeBase):
            @classmethod
            def model_validate(cls, data):
                return {'validated': True, **data}

        result = StoragePool._build_api_payload(FakeModel, {'name': 'test'})
        assert result['validated'] is True

    def test_payload_pydantic_fallback_init(self):
        """When model_validate fails, fall back to __init__."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

        class FakeBase:
            __module__ = 'some.other.module'

        class FakeModel(FakeBase):
            def __init__(self, **kwargs):
                self.data = kwargs

            @classmethod
            def model_validate(cls, data):
                raise ValueError("not supported")

        result = StoragePool._build_api_payload(FakeModel, {'name': 'test'})
        assert result.data == {'name': 'test'}


# ===========================================================================
# Stub compatibility tests
# ===========================================================================
class TestStubCompatibility:

    def test_ensure_stub_compat_secret_str_patch(self):
        """When SecretStr is str, patch it with _CompatSecretStr."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

        mock_api_client = MagicMock()
        mock_api_client.SecretStr = str

        with patch(f'{MODULE}.objectscale_api_client', mock_api_client), \
             patch(f'{MODULE}.objectscale_client_stubs', None):
            StoragePool._ensure_client_stub_compatibility()

        # Verify it was patched
        new_cls = mock_api_client.SecretStr
        assert new_cls is not str
        assert new_cls('hello').get_secret_value() == 'hello'

    def test_ensure_stub_compat_model_dump_patch(self):
        """When BaseModel lacks model_dump, add it."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

        class FakeBaseModel:
            pass

        mock_stubs = MagicMock()
        mock_stubs.BaseModel = FakeBaseModel

        with patch(f'{MODULE}.objectscale_api_client', None), \
             patch(f'{MODULE}.objectscale_client_stubs', mock_stubs):
            StoragePool._ensure_client_stub_compatibility()

        instance = FakeBaseModel()
        instance.__dict__ = {'key': 'value'}
        assert instance.model_dump() == {'key': 'value'}

    def test_ensure_stub_compat_skips_when_model_dump_exists(self):
        """Should not patch model_dump when it already exists."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

        class FakeBaseModel:
            def model_dump(self):
                return {'existing': True}

        mock_stubs = MagicMock()
        mock_stubs.BaseModel = FakeBaseModel

        with patch(f'{MODULE}.objectscale_api_client', None), \
             patch(f'{MODULE}.objectscale_client_stubs', mock_stubs):
            StoragePool._ensure_client_stub_compatibility()

        instance = FakeBaseModel()
        assert instance.model_dump() == {'existing': True}


# ===========================================================================
# Modify storage pool edge cases
# ===========================================================================
class TestModifyEdgeCases:

    def test_modify_request_model_unavailable(self):
        obj = make_obj()
        with patch(f'{MODULE}.ObjectVarrayServiceUpdateVirtualArrayRequest', None):
            obj.modify_storage_pool('pool-id', {'name': 'test'})

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'unavailable' in kwargs['msg']

    def test_get_pool_by_id_generic_error(self):
        obj = make_obj()
        obj.storage_pool_api.object_varray_service_get_virtual_array.side_effect = \
            make_api_error(500, '{"description": "Server error"}')
        obj._get_storage_pool_by_id('urn:storageos:VirtualArray:test')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'failed with error' in kwargs['msg']

    def test_pool_with_no_id_field(self):
        """Pool found by name but has no 'id' field."""
        obj = make_obj()
        pool_no_id = dict(SAMPLE_POOL_1)
        pool_no_id.pop('id')
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.return_value = \
            make_list_response([pool_no_id])

        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'no valid identifier' in kwargs['msg']


# ===========================================================================
# Main entry point test
# ===========================================================================
class TestMain:

    @patch(f'{MODULE}.StoragePool')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import main
        main()
        mock_cls.return_value.perform_module_operation.assert_called_once()
