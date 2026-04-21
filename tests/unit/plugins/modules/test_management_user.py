# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.management_user'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    user_id='mgmt1',
    password=None,
    is_system_admin=None,
    is_system_monitor=None,
    is_security_admin=None,
    is_external_group=None,
    state='present',
)


def make_obj(params=None, has_client=True, check_mode=False):
    from ansible_collections.dellemc.objectscale.plugins.modules.management_user import ManagementUser

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = check_mode
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.MgmtUserInfoApi'):
        obj = ManagementUser()

    obj.module = module_mock
    obj.mgmt_api = MagicMock()
    return obj


class TestInit:
    @patch(f'{MODULE}.MgmtUserInfoApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_success(self, mock_am, mock_conn, mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.management_user import ManagementUser
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        obj = ManagementUser()
        assert obj.module is m
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_no_client(self, mock_am, _mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.management_user import ManagementUser
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        ManagementUser()
        kwargs = m.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'objectscale_client' in kwargs.get('msg', '')

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.management_user import ManagementUser
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        with patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('boom')):
            ManagementUser()
        kwargs = m.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'boom' in kwargs.get('msg', '')


class TestGetUserDetails:
    def test_success(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'userId': 'mgmt1', 'isSystemAdmin': False}
        obj.mgmt_api.mgmt_user_info_service_get_local_user_info.return_value = resp
        result = obj.get_user_details('mgmt1')
        assert result == {'userId': 'mgmt1', 'isSystemAdmin': False}

    def test_404_returns_none(self):
        obj = make_obj()
        err = Exception('not found')
        err.status = 404
        obj.mgmt_api.mgmt_user_info_service_get_local_user_info.side_effect = err
        assert obj.get_user_details('mgmt1') is None

    def test_400_returns_none(self):
        obj = make_obj()
        err = Exception('bad request')
        err.status = 400
        obj.mgmt_api.mgmt_user_info_service_get_local_user_info.side_effect = err
        assert obj.get_user_details('mgmt1') is None

    def test_500_fails(self):
        obj = make_obj()
        err = Exception('server err')
        err.status = 500
        obj.mgmt_api.mgmt_user_info_service_get_local_user_info.side_effect = err
        with patch(f'{UTILS}.determine_error', return_value='server err'):
            obj.get_user_details('mgmt1')
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestCreateUser:
    def test_success(self):
        obj = make_obj()
        params = {**BASE_PARAMS, 'password': 'pwd', 'is_system_monitor': True}
        obj.create_user('mgmt1', params)
        obj.mgmt_api.mgmt_user_info_service_create_local_user_info.assert_called_once()

    def test_missing_password_fails(self):
        obj = make_obj()
        params = {**BASE_PARAMS, 'password': None}
        obj.create_user('mgmt1', params)
        assert obj.module.exit_json.call_args[1]['failed'] is True
        assert 'password' in obj.module.exit_json.call_args[1]['msg'].lower()

    def test_api_error_fails(self):
        obj = make_obj()
        obj.mgmt_api.mgmt_user_info_service_create_local_user_info.side_effect = Exception('api err')
        with patch(f'{UTILS}.determine_error', return_value='api err'):
            obj.create_user('mgmt1', {**BASE_PARAMS, 'password': 'pwd'})
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestModifyUser:
    def test_success(self):
        obj = make_obj()
        result = obj.modify_user('mgmt1', {'is_system_admin': True})
        assert result is True
        obj.mgmt_api.mgmt_user_info_service_modify_local_user_info.assert_called_once()

    def test_no_fields_noop(self):
        obj = make_obj()
        result = obj.modify_user('mgmt1', {})
        assert result is False
        obj.mgmt_api.mgmt_user_info_service_modify_local_user_info.assert_not_called()

    def test_api_error_fails(self):
        obj = make_obj()
        obj.mgmt_api.mgmt_user_info_service_modify_local_user_info.side_effect = Exception('mod err')
        with patch(f'{UTILS}.determine_error', return_value='mod err'):
            obj.modify_user('mgmt1', {'is_system_admin': True})
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestDeleteUser:
    def test_success(self):
        obj = make_obj()
        result = obj.delete_user('mgmt1')
        assert result is True
        obj.mgmt_api.mgmt_user_info_service_delete_local_user_info.assert_called_once()

    def test_api_error_fails(self):
        obj = make_obj()
        obj.mgmt_api.mgmt_user_info_service_delete_local_user_info.side_effect = Exception('del err')
        with patch(f'{UTILS}.determine_error', return_value='del err'):
            obj.delete_user('mgmt1')
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestIsModified:
    def test_no_drift(self):
        obj = make_obj()
        details = {'userId': 'mgmt1', 'isSystemAdmin': True, 'isSystemMonitor': False}
        modify = obj.is_user_modified(details, {**BASE_PARAMS, 'is_system_admin': True})
        assert modify == {}

    def test_role_drift(self):
        obj = make_obj()
        details = {'userId': 'mgmt1', 'isSystemAdmin': False}
        modify = obj.is_user_modified(details, {**BASE_PARAMS, 'is_system_admin': True})
        assert modify.get('is_system_admin') is True

    def test_password_always_modifies(self):
        obj = make_obj()
        details = {'userId': 'mgmt1'}
        modify = obj.is_user_modified(details, {**BASE_PARAMS, 'password': 'new'})
        assert modify.get('password') == 'new'


class TestPerformModuleOperation:
    def test_create_when_absent(self):
        obj = make_obj(params={**BASE_PARAMS, 'password': 'p', 'state': 'present'})
        # first call returns None (missing), subsequent returns the created user
        obj.get_user_details = MagicMock(side_effect=[None, {'userId': 'mgmt1'}])
        obj.create_user = MagicMock(return_value=True)
        obj.perform_module_operation()
        obj.create_user.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('changed') is True

    def test_present_no_drift(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'present'})
        obj.get_user_details = MagicMock(return_value={'userId': 'mgmt1', 'isSystemAdmin': False})
        obj.perform_module_operation()
        assert obj.module.exit_json.call_args[1].get('changed') is False

    def test_present_with_drift(self):
        obj = make_obj(params={**BASE_PARAMS, 'is_system_admin': True, 'state': 'present'})
        obj.get_user_details = MagicMock(
            side_effect=[{'userId': 'mgmt1', 'isSystemAdmin': False}, {'userId': 'mgmt1', 'isSystemAdmin': True}]
        )
        obj.modify_user = MagicMock(return_value=True)
        obj.perform_module_operation()
        obj.modify_user.assert_called_once()
        assert obj.module.exit_json.call_args[1].get('changed') is True

    def test_absent_existing(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'absent'})
        obj.get_user_details = MagicMock(return_value={'userId': 'mgmt1'})
        obj.delete_user = MagicMock(return_value=True)
        obj.perform_module_operation()
        obj.delete_user.assert_called_once()
        assert obj.module.exit_json.call_args[1].get('changed') is True

    def test_absent_missing(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'absent'})
        obj.get_user_details = MagicMock(return_value=None)
        obj.perform_module_operation()
        assert obj.module.exit_json.call_args[1].get('changed') is False

    def test_check_mode_create(self):
        obj = make_obj(params={**BASE_PARAMS, 'password': 'p', 'state': 'present'}, check_mode=True)
        obj.get_user_details = MagicMock(return_value=None)
        obj.create_user = MagicMock()
        obj.perform_module_operation()
        obj.create_user.assert_not_called()
        assert obj.module.exit_json.call_args[1].get('changed') is True
