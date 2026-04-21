# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.object_user_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    user=None,
    namespace=None,
    include_secret_keys=False,
)


def make_obj(params=None, has_client=True):
    from ansible_collections.dellemc.objectscale.plugins.modules.object_user_info import ObjectUserInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.UserManagementApi'), \
         patch(f'{MODULE}.UserSecretKeyApi'):
        obj = ObjectUserInfo()

    obj.module = module_mock
    obj.user_mgmt_api = MagicMock()
    obj.secret_key_api = MagicMock()
    return obj


class TestInit:
    @patch(f'{MODULE}.UserSecretKeyApi')
    @patch(f'{MODULE}.UserManagementApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_success(self, mock_am, mock_conn, *_):
        from ansible_collections.dellemc.objectscale.plugins.modules.object_user_info import ObjectUserInfo
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        ObjectUserInfo()
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_no_client(self, mock_am, _mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.object_user_info import ObjectUserInfo
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        ObjectUserInfo()
        assert m.exit_json.call_args[1].get('failed') is True


class TestGetList:
    def test_get_user(self):
        obj = make_obj(params={**BASE_PARAMS, 'user': 'alice', 'namespace': 'ns1'})
        resp = MagicMock()
        resp.to_dict.return_value = {'name': 'alice', 'namespace': 'ns1'}
        obj.user_mgmt_api.user_management_service_get_user_info.return_value = resp
        assert obj.get_user('alice', 'ns1') == {'name': 'alice', 'namespace': 'ns1'}

    def test_get_user_404_fails(self):
        obj = make_obj(params={**BASE_PARAMS, 'user': 'alice', 'namespace': 'ns1'})
        err = Exception('nf')
        err.status = 404
        obj.user_mgmt_api.user_management_service_get_user_info.side_effect = err
        with patch(f'{UTILS}.determine_error', return_value='nf'):
            obj.get_user('alice', 'ns1')
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_list_users_for_namespace(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'blobuser': [{'userid': 'alice'}, {'userid': 'bob'}]}
        obj.user_mgmt_api.user_management_service_get_users_for_namespace.return_value = resp
        result = obj.list_users_in_namespace('ns1')
        assert len(result) == 2

    def test_list_all_users(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'blobuser': [{'userid': 'alice'}]}
        obj.user_mgmt_api.user_management_service_get_all_users.return_value = resp
        result = obj.list_all_users()
        assert len(result) == 1


class TestEnrich:
    def test_enrich_with_secret_keys(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {
            'secret_key_1_exist': True,
            'secret_key_1_id': 'k1',
            'key_timestamp_1': 't1',
            'secret_key_1': 'REDACT_ME',
            'secret_key_2_exist': False,
        }
        obj.secret_key_api.user_secret_key_service_get_keys_for_user.return_value = resp
        metadata = obj.get_secret_key_metadata('alice', None)
        assert isinstance(metadata, list)
        assert any(item.get('secret_key_id') == 'k1' for item in metadata)
        for item in metadata:
            assert 'secret_key' not in item or item.get('secret_key') != 'REDACT_ME'


class TestPerform:
    def test_single_user(self):
        obj = make_obj(params={**BASE_PARAMS, 'user': 'alice', 'namespace': 'ns1'})
        obj.get_user = MagicMock(return_value={'name': 'alice'})
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('changed') is False
        assert kwargs.get('object_user') == {'name': 'alice'}

    def test_namespace_list(self):
        obj = make_obj(params={**BASE_PARAMS, 'namespace': 'ns1'})
        obj.list_users_in_namespace = MagicMock(return_value=[{'userid': 'a'}])
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('object_users') == [{'userid': 'a'}]

    def test_list_all(self):
        obj = make_obj()
        obj.list_all_users = MagicMock(return_value=[{'userid': 'a'}])
        obj.perform_module_operation()
        assert obj.module.exit_json.call_args[1].get('object_users') == [{'userid': 'a'}]

    def test_include_secret_keys(self):
        obj = make_obj(params={**BASE_PARAMS, 'user': 'alice', 'namespace': 'ns1', 'include_secret_keys': True})
        obj.get_user = MagicMock(return_value={'name': 'alice'})
        obj.get_secret_key_metadata = MagicMock(return_value=[{'secret_key_id': 'k1'}])
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        user = kwargs.get('object_user')
        assert user.get('secret_key_metadata') == [{'secret_key_id': 'k1'}]
