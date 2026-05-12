# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.tests.unit.plugins.module_utils.mock_storage_pool_api import (
    BASE_PARAMS,
    SAMPLE_POOL,
    SAMPLE_POOL_UPDATED,
)

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.storage_pool'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'


def make_sp_obj(params=None, has_client=True, check_mode=False, diff_mode=False):
    """Helper: return a StoragePool instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = check_mode
    module_mock._diff = diff_mode
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.ObjectVarrayApi'):
        obj = StoragePool()

    obj.module = module_mock
    obj.storage_pool_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# TC-SP-001 to TC-SP-004: Init tests
# ---------------------------------------------------------------------------
class TestStoragePoolInit:

    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_api):
        """TC-SP-001: Successful initialization."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        obj = StoragePool()

        assert obj.module is mock_module
        mock_conn.assert_called_once()
        mock_api.assert_called_once()

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_missing_client(self, mock_am):
        """TC-SP-002: Missing objectscale_client."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        StoragePool()

        mock_module.exit_json.assert_called_once()
        assert 'objectscale_client' in mock_module.exit_json.call_args[1]['msg']

    @patch(f'{MODULE}.ObjectVarrayApi', None)
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_api_unavailable(self, mock_am, mock_conn):
        """TC-SP-003: ObjectVarrayApi unavailable."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        StoragePool()

        kwargs = mock_module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'unavailable' in kwargs['msg']

    @patch(f'{MODULE}.ObjectVarrayApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am, mock_conn, mock_api):
        """TC-SP-004: Connection failure."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        mock_conn.side_effect = Exception('Connection refused')

        StoragePool()

        kwargs = mock_module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'Failed to connect' in kwargs['msg']


# ---------------------------------------------------------------------------
# TC-SP-005 to TC-SP-008: Create tests
# ---------------------------------------------------------------------------
class TestStoragePoolCreate:

    def test_create_success(self):
        """TC-SP-005: Create pool — success."""
        obj = make_sp_obj()
        # First call to get_storage_pool_details returns None (not found)
        obj.get_storage_pool_details = MagicMock(side_effect=[None, SAMPLE_POOL.copy()])
        obj.create_storage_pool = MagicMock()
        obj.is_modify_required = MagicMock(return_value=False)

        obj.perform_module_operation()

        obj.create_storage_pool.assert_called_once()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True
        assert result['storage_pool_details']['name'] == 'sp_ansible_test'

    def test_create_check_mode(self):
        """TC-SP-006: Create pool — check mode."""
        obj = make_sp_obj(check_mode=True)
        obj.get_storage_pool_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True
        # No actual API call should be made in check mode
        obj.storage_pool_api.object_varray_service_create_virtual_array.assert_not_called()

    def test_create_already_exists_idempotent(self):
        """TC-SP-007: Create pool — already exists (idempotent, no change needed)."""
        obj = make_sp_obj()
        obj.get_storage_pool_details = MagicMock(return_value=SAMPLE_POOL.copy())
        obj.is_modify_required = MagicMock(return_value=False)

        obj.perform_module_operation()

        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is False
        assert result['storage_pool_details']['name'] == 'sp_ansible_test'

    def test_create_conflict_409(self):
        """TC-SP-008: Create pool — HTTP 409 conflict."""
        obj = make_sp_obj()
        obj.get_storage_pool_details = MagicMock(return_value=None)

        err = Exception('conflict')
        err.status = 409
        err.body = '{"description": "Resource already exists"}'
        obj.storage_pool_api.object_varray_service_create_virtual_array.side_effect = err

        obj.perform_module_operation()

        # create_storage_pool catches the exception and calls exit_json(failed=True) first
        first_call = obj.module.exit_json.call_args_list[0][1]
        assert first_call['failed'] is True
        assert 'Resource already exists' in first_call['msg']

    def test_create_with_all_optional_fields(self):
        """TC-SP-030: Create with all optional fields."""
        params = BASE_PARAMS.copy()
        params['description'] = 'Full featured pool'
        params['is_cold_storage_enabled'] = True
        params['warning_alert_at'] = 60
        params['error_alert_at'] = 80
        obj = make_sp_obj(params=params)
        obj.get_storage_pool_details = MagicMock(side_effect=[None, SAMPLE_POOL.copy()])
        obj.create_storage_pool = MagicMock()
        obj.is_modify_required = MagicMock(return_value=False)

        obj.perform_module_operation()

        obj.create_storage_pool.assert_called_once()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True


# ---------------------------------------------------------------------------
# TC-SP-009 to TC-SP-015: Modify tests
# ---------------------------------------------------------------------------
class TestStoragePoolModify:

    def test_modify_description(self):
        """TC-SP-009: Modify description — success."""
        params = BASE_PARAMS.copy()
        params['description'] = 'Updated description'
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()
        obj.get_storage_pool_details = MagicMock(side_effect=[current, SAMPLE_POOL_UPDATED.copy()])
        obj.is_modify_required = MagicMock(return_value=True)
        obj.modify_storage_pool = MagicMock()

        obj.perform_module_operation()

        obj.modify_storage_pool.assert_called_once()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True

    def test_modify_warning_alert(self):
        """TC-SP-010: Modify warningAlertAt — success."""
        params = BASE_PARAMS.copy()
        params['warning_alert_at'] = 60
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()
        obj.get_storage_pool_details = MagicMock(side_effect=[current, SAMPLE_POOL_UPDATED.copy()])
        obj.is_modify_required = MagicMock(return_value=True)
        obj.modify_storage_pool = MagicMock()

        obj.perform_module_operation()

        obj.modify_storage_pool.assert_called_once()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True

    def test_modify_error_alert(self):
        """TC-SP-011: Modify errorAlertAt — success."""
        params = BASE_PARAMS.copy()
        params['error_alert_at'] = 90
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()
        obj.get_storage_pool_details = MagicMock(side_effect=[current, SAMPLE_POOL_UPDATED.copy()])
        obj.is_modify_required = MagicMock(return_value=True)
        obj.modify_storage_pool = MagicMock()

        obj.perform_module_operation()

        obj.modify_storage_pool.assert_called_once()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True

    def test_modify_cold_storage(self):
        """TC-SP-012: Modify isColdStorageEnabled — success."""
        params = BASE_PARAMS.copy()
        params['is_cold_storage_enabled'] = True
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()
        obj.get_storage_pool_details = MagicMock(side_effect=[current, SAMPLE_POOL_UPDATED.copy()])
        obj.is_modify_required = MagicMock(return_value=True)
        obj.modify_storage_pool = MagicMock()

        obj.perform_module_operation()

        obj.modify_storage_pool.assert_called_once()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True

    def test_modify_check_mode(self):
        """TC-SP-013: Modify — check mode."""
        params = BASE_PARAMS.copy()
        params['description'] = 'Updated in check mode'
        obj = make_sp_obj(params=params, check_mode=True)
        current = SAMPLE_POOL.copy()
        obj.get_storage_pool_details = MagicMock(return_value=current)
        obj.is_modify_required = MagicMock(return_value=True)

        obj.perform_module_operation()

        # No PUT call should be made
        obj.storage_pool_api.object_varray_service_update_virtual_array.assert_not_called()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True

    def test_modify_diff_mode(self):
        """TC-SP-014: Modify — diff mode output."""
        params = BASE_PARAMS.copy()
        params['description'] = 'Updated description'
        obj = make_sp_obj(params=params, diff_mode=True)
        current = SAMPLE_POOL.copy()
        updated = SAMPLE_POOL_UPDATED.copy()
        obj.get_storage_pool_details = MagicMock(side_effect=[current, updated])
        obj.is_modify_required = MagicMock(return_value=True)
        obj.modify_storage_pool = MagicMock()

        obj.perform_module_operation()

        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True
        assert 'diff' in result
        assert 'before' in result['diff']
        assert 'after' in result['diff']

    def test_no_op_all_fields_match(self):
        """TC-SP-015: No-op — all fields already match."""
        obj = make_sp_obj()
        obj.get_storage_pool_details = MagicMock(return_value=SAMPLE_POOL.copy())
        obj.is_modify_required = MagicMock(return_value=False)

        obj.perform_module_operation()

        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is False


# ---------------------------------------------------------------------------
# TC-SP-016 to TC-SP-018: Delete tests
# ---------------------------------------------------------------------------
class TestStoragePoolDelete:

    def test_delete_existing_pool(self):
        """TC-SP-016: Delete existing pool — success."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_sp_obj(params=params)
        obj.get_storage_pool_details = MagicMock(return_value=SAMPLE_POOL.copy())
        obj.delete_storage_pool = MagicMock()

        obj.perform_module_operation()

        obj.delete_storage_pool.assert_called_once()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True

    def test_delete_non_existent_pool_idempotent(self):
        """TC-SP-017: Delete non-existent pool — idempotent."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_sp_obj(params=params)
        obj.get_storage_pool_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is False

    def test_delete_check_mode(self):
        """TC-SP-018: Delete — check mode."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_sp_obj(params=params, check_mode=True)
        obj.get_storage_pool_details = MagicMock(return_value=SAMPLE_POOL.copy())

        obj.perform_module_operation()

        # No actual delete call
        obj.storage_pool_api.object_varray_service_delete_virtual_array.assert_not_called()
        result = obj.module.exit_json.call_args[1]
        assert result['changed'] is True


# ---------------------------------------------------------------------------
# TC-SP-019 to TC-SP-022: Exception tests
# ---------------------------------------------------------------------------
class TestStoragePoolExceptions:

    def _assert_any_failed_call(self, obj, expected_msg_fragment):
        """Verify at least one exit_json call has failed=True with expected message."""
        failed_calls = [
            c for c in obj.module.exit_json.call_args_list
            if c[1].get('failed') is True
        ]
        assert len(failed_calls) >= 1, "Expected at least one exit_json(failed=True) call"
        assert expected_msg_fragment in failed_calls[0][1]['msg']

    def test_auth_failure_401(self):
        """TC-SP-019: Authentication failure HTTP 401."""
        obj = make_sp_obj()
        err = Exception('Unauthorized')
        err.status = 401
        err.body = '{"description": "Authentication failed"}'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.side_effect = err

        obj.perform_module_operation()

        self._assert_any_failed_call(obj, 'Authentication failed')

    def test_insufficient_permissions_403(self):
        """TC-SP-020: Insufficient permissions HTTP 403."""
        obj = make_sp_obj()
        err = Exception('Forbidden')
        err.status = 403
        err.body = '{"description": "Insufficient permissions"}'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.side_effect = err

        obj.perform_module_operation()

        self._assert_any_failed_call(obj, 'Insufficient permissions')

    def test_pool_not_found_404_on_modify(self):
        """TC-SP-021: Pool not found HTTP 404 on modify."""
        params = BASE_PARAMS.copy()
        params['description'] = 'Changed description to trigger modify'
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()
        obj.get_storage_pool_details = MagicMock(return_value=current)
        obj.is_modify_required = MagicMock(return_value=True)

        err = Exception('Not Found')
        err.status = 404
        err.body = '{"description": "Storage pool not found"}'
        obj.storage_pool_api.object_varray_service_update_virtual_array.side_effect = err

        obj.perform_module_operation()

        self._assert_any_failed_call(obj, 'Storage pool not found')

    def test_api_error_500(self):
        """TC-SP-022: API error HTTP 500."""
        obj = make_sp_obj()
        err = Exception('Internal Server Error')
        err.status = 500
        err.body = '{"description": "Internal error"}'
        obj.storage_pool_api.object_varray_service_get_virtual_arrays.side_effect = err

        obj.perform_module_operation()

        self._assert_any_failed_call(obj, 'Internal error')


# ---------------------------------------------------------------------------
# TC-SP-023 to TC-SP-025: Validation tests
# ---------------------------------------------------------------------------
class TestStoragePoolValidation:

    def test_warning_ge_error_alert_rejected(self):
        """TC-SP-023: warning_alert_at >= error_alert_at rejected."""
        params = BASE_PARAMS.copy()
        params['warning_alert_at'] = 90
        params['error_alert_at'] = 85
        obj = make_sp_obj(params=params)
        obj.get_storage_pool_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        obj.module.fail_json.assert_called_once()
        assert 'warning_alert_at' in obj.module.fail_json.call_args[1]['msg']

    def test_state_required_parameter(self):
        """TC-SP-024: state is a required parameter."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        sp = StoragePool.__new__(StoragePool)
        params = sp.get_storage_pool_parameters()
        assert params['state']['required'] is True

    def test_storage_pool_name_required_parameter(self):
        """TC-SP-025: storage_pool_name is a required parameter."""
        from ansible_collections.dellemc.objectscale.plugins.modules.storage_pool import StoragePool
        sp = StoragePool.__new__(StoragePool)
        params = sp.get_storage_pool_parameters()
        assert params['storage_pool_name']['required'] is True


# ---------------------------------------------------------------------------
# TC-SP-026 to TC-SP-027: Security tests
# ---------------------------------------------------------------------------
class TestStoragePoolSecurity:

    def test_password_no_log(self):
        """TC-SP-026: Password param marked no_log."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_management_host_parameters,
        )
        params = get_objectscale_management_host_parameters()
        assert params['objectscale_password']['no_log'] is True

    def test_sensitive_fields_sanitized(self):
        """TC-SP-027: Sensitive fields sanitized in output."""
        obj = make_sp_obj()
        test_data = {
            'name': 'sp_test',
            'password': 'super_secret',
            'nested': {
                'token': 'abc123',
                'value': 'visible',
            }
        }

        sanitized = obj._sanitize_sensitive_fields(test_data)

        assert sanitized['name'] == 'sp_test'
        assert sanitized['password'] == '***'
        assert sanitized['nested']['token'] == '***'
        assert sanitized['nested']['value'] == 'visible'


# ---------------------------------------------------------------------------
# TC-SP-028 to TC-SP-029: Helper tests
# ---------------------------------------------------------------------------
class TestStoragePoolHelpers:

    def test_to_dict_none(self):
        """TC-SP-028: _to_dict handles None."""
        obj = make_sp_obj()
        assert obj._to_dict(None) == {}

    def test_to_dict_with_to_dict_method(self):
        """TC-SP-029: _to_dict handles .to_dict() objects."""
        obj = make_sp_obj()
        mock_model = MagicMock()
        mock_model.to_dict.return_value = {'id': 'sp1', 'name': 'pool1'}

        result = obj._to_dict(mock_model)

        assert result == {'id': 'sp1', 'name': 'pool1'}


# ---------------------------------------------------------------------------
# TC-SP-IS_MODIFY: is_modify_required logic tests
# ---------------------------------------------------------------------------
class TestStoragePoolIsModifyRequired:

    def test_no_modify_when_all_match(self):
        """Verify is_modify_required returns False when all fields match."""
        obj = make_sp_obj()
        current = SAMPLE_POOL.copy()

        result = obj.is_modify_required(obj.module.params, current)

        assert result is False

    def test_modify_when_description_differs(self):
        """Verify is_modify_required returns True when description differs."""
        params = BASE_PARAMS.copy()
        params['description'] = 'New description'
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()

        result = obj.is_modify_required(obj.module.params, current)

        assert result is True

    def test_modify_when_cold_storage_differs(self):
        """Verify is_modify_required returns True when cold storage differs."""
        params = BASE_PARAMS.copy()
        params['is_cold_storage_enabled'] = True
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()

        result = obj.is_modify_required(obj.module.params, current)

        assert result is True

    def test_modify_when_warning_alert_differs(self):
        """Verify is_modify_required returns True when warning alert differs."""
        params = BASE_PARAMS.copy()
        params['warning_alert_at'] = 60
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()

        result = obj.is_modify_required(obj.module.params, current)

        assert result is True

    def test_modify_when_error_alert_differs(self):
        """Verify is_modify_required returns True when error alert differs."""
        params = BASE_PARAMS.copy()
        params['error_alert_at'] = 95
        obj = make_sp_obj(params=params)
        current = SAMPLE_POOL.copy()

        result = obj.is_modify_required(obj.module.params, current)

        assert result is True
