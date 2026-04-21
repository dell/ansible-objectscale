# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.management_user_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    user_id=None,
)


def make_obj(params=None, has_client=True):
    from ansible_collections.dellemc.objectscale.plugins.modules.management_user_info import ManagementUserInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.MgmtUserInfoApi'):
        obj = ManagementUserInfo()

    obj.module = module_mock
    obj.mgmt_api = MagicMock()
    return obj


class TestInit:
    @patch(f'{MODULE}.MgmtUserInfoApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_success(self, mock_am, mock_conn, _mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.management_user_info import ManagementUserInfo
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        ManagementUserInfo()
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_no_client(self, mock_am, _mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.management_user_info import ManagementUserInfo
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        ManagementUserInfo()
        assert m.exit_json.call_args[1].get('failed') is True


class TestGetAndList:
    def test_get_user_success(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'userId': 'mgmt1'}
        obj.mgmt_api.mgmt_user_info_service_get_local_user_info.return_value = resp
        assert obj.get_user('mgmt1') == {'userId': 'mgmt1'}

    def test_get_user_404_fails(self):
        obj = make_obj()
        err = Exception('nf')
        err.status = 404
        obj.mgmt_api.mgmt_user_info_service_get_local_user_info.side_effect = err
        with patch(f'{UTILS}.determine_error', return_value='nf'):
            obj.get_user('mgmt1')
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_list_users_success(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'mgmt_user_info': [{'userId': 'a'}, {'userId': 'b'}]}
        obj.mgmt_api.mgmt_user_info_service_get_local_user_infos.return_value = resp
        result = obj.list_users()
        assert isinstance(result, list) and len(result) == 2

    def test_list_users_error_fails(self):
        obj = make_obj()
        obj.mgmt_api.mgmt_user_info_service_get_local_user_infos.side_effect = Exception('boom')
        with patch(f'{UTILS}.determine_error', return_value='boom'):
            obj.list_users()
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestPerform:
    def test_single_user(self):
        obj = make_obj(params={**BASE_PARAMS, 'user_id': 'mgmt1'})
        obj.get_user = MagicMock(return_value={'userId': 'mgmt1'})
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('changed') is False
        assert kwargs.get('management_user') == {'userId': 'mgmt1'}

    def test_list(self):
        obj = make_obj()
        obj.list_users = MagicMock(return_value=[{'userId': 'a'}])
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('changed') is False
        assert kwargs.get('management_users') == [{'userId': 'a'}]
