# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.object_user'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    user='alice',
    namespace='ns1',
    tags=None,
    purge_tags=True,
    locked=None,
    secret_keys=None,
    state='present',
)


def make_obj(params=None, has_client=True, check_mode=False):
    from ansible_collections.dellemc.objectscale.plugins.modules.object_user import ObjectUser

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = check_mode
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.UserManagementApi'), \
         patch(f'{MODULE}.UserSecretKeyApi'):
        obj = ObjectUser()

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
        from ansible_collections.dellemc.objectscale.plugins.modules.object_user import ObjectUser
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        ObjectUser()
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_no_client(self, mock_am, _mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.object_user import ObjectUser
        m = MagicMock()
        m.params = BASE_PARAMS.copy()
        mock_am.return_value = m
        ObjectUser()
        assert m.exit_json.call_args[1].get('failed') is True


class TestGetUserDetails:
    def test_success(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'name': 'alice', 'namespace': 'ns1', 'locked': False}
        obj.user_mgmt_api.user_management_service_get_user_info.return_value = resp
        assert obj.get_user_details('alice', 'ns1') == {'name': 'alice', 'namespace': 'ns1', 'locked': False}

    def test_404_returns_none(self):
        obj = make_obj()
        err = Exception('nf')
        err.status = 404
        obj.user_mgmt_api.user_management_service_get_user_info.side_effect = err
        assert obj.get_user_details('alice', 'ns1') is None

    def test_500_fails(self):
        obj = make_obj()
        err = Exception('srv')
        err.status = 500
        obj.user_mgmt_api.user_management_service_get_user_info.side_effect = err
        with patch(f'{UTILS}.determine_error', return_value='srv'):
            obj.get_user_details('alice', 'ns1')
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestCreateUser:
    def test_success(self):
        obj = make_obj()
        obj.create_user('alice', 'ns1', [{'name': 'env', 'value': 'prod'}])
        obj.user_mgmt_api.user_management_service_add_user.assert_called_once()

    def test_api_error_fails(self):
        obj = make_obj()
        obj.user_mgmt_api.user_management_service_add_user.side_effect = Exception('add err')
        with patch(f'{UTILS}.determine_error', return_value='add err'):
            obj.create_user('alice', 'ns1', None)
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestDeleteUser:
    def test_success(self):
        obj = make_obj()
        result = obj.delete_user('alice', 'ns1')
        assert result is True
        obj.user_mgmt_api.user_management_service_remove_user.assert_called_once()

    def test_api_error_fails(self):
        obj = make_obj()
        obj.user_mgmt_api.user_management_service_remove_user.side_effect = Exception('x')
        with patch(f'{UTILS}.determine_error', return_value='x'):
            obj.delete_user('alice', 'ns1')
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestSyncTags:
    def test_add_and_remove_with_purge(self):
        obj = make_obj()
        current = [{'name': 'env', 'value': 'dev'}, {'name': 'old', 'value': 'x'}]
        desired = [{'name': 'env', 'value': 'prod'}, {'name': 'new', 'value': 'y'}]
        changed = obj.sync_tags('alice', 'ns1', current, desired, purge_tags=True)
        assert changed is True

    def test_add_tags_uses_correct_payload_structure(self):
        obj = make_obj()
        current = []
        desired = [{'name': 'env', 'value': 'prod'}]
        changed = obj.sync_tags('alice', 'ns1', current, desired, purge_tags=True)
        assert changed is True
        # Verify the payload uses 'tags' field
        call_args = obj.user_mgmt_api.user_management_service_add_user_tag.call_args
        assert call_args[1]['namespace'] == 'ns1'  # namespace as method parameter
        payload = call_args[1]['user_management_service_add_user_tag_request']
        # Check for 'tags' in either dict or object
        assert hasattr(payload, 'tags') or 'tags' in payload

    def test_update_tags_uses_correct_payload_structure(self):
        obj = make_obj()
        current = [{'name': 'env', 'value': 'dev'}]
        desired = [{'name': 'env', 'value': 'prod'}]
        changed = obj.sync_tags('alice', 'ns1', current, desired, purge_tags=True)
        assert changed is True
        # Verify the payload uses 'tags' field
        call_args = obj.user_mgmt_api.user_management_service_update_user_tag.call_args
        assert call_args[1]['namespace'] == 'ns1'  # namespace as method parameter
        payload = call_args[1]['user_management_service_update_user_tag_request']
        # Check for 'tags' in either dict or object
        assert hasattr(payload, 'tags') or 'tags' in payload

    def test_remove_tags_uses_correct_payload_structure(self):
        obj = make_obj()
        current = [{'name': 'env', 'value': 'dev'}, {'name': 'old', 'value': 'x'}]
        desired = []
        changed = obj.sync_tags('alice', 'ns1', current, desired, purge_tags=True)
        assert changed is True
        # Verify the payload uses 'tags' field
        call_args = obj.user_mgmt_api.user_management_service_remove_user_tags.call_args
        assert call_args[1]['namespace'] == 'ns1'  # namespace as method parameter
        payload = call_args[1]['user_management_service_remove_user_tags_request']
        # Check for 'tags' in either dict or object
        assert hasattr(payload, 'tags') or 'tags' in payload

    def test_noop_when_equal(self):
        obj = make_obj()
        current = [{'name': 'env', 'value': 'prod'}]
        desired = [{'name': 'env', 'value': 'prod'}]
        changed = obj.sync_tags('alice', 'ns1', current, desired, purge_tags=True)
        assert changed is False

    def test_merge_without_purge(self):
        obj = make_obj()
        current = [{'name': 'env', 'value': 'dev'}]
        desired = [{'name': 'new', 'value': 'y'}]
        changed = obj.sync_tags('alice', 'ns1', current, desired, purge_tags=False)
        assert changed is True

    def test_api_error_on_add_fails(self):
        obj = make_obj()
        obj.user_mgmt_api.user_management_service_add_user_tag.side_effect = Exception('add err')
        with patch(f'{UTILS}.determine_error', return_value='add err'):
            obj.sync_tags('alice', 'ns1', [], [{'name': 'env', 'value': 'prod'}], purge_tags=True)
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_api_error_on_update_fails(self):
        obj = make_obj()
        obj.user_mgmt_api.user_management_service_update_user_tag.side_effect = Exception('upd err')
        with patch(f'{UTILS}.determine_error', return_value='upd err'):
            obj.sync_tags('alice', 'ns1', [{'name': 'env', 'value': 'dev'}], [{'name': 'env', 'value': 'prod'}], purge_tags=True)
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_api_error_on_remove_fails(self):
        obj = make_obj()
        obj.user_mgmt_api.user_management_service_remove_user_tags.side_effect = Exception('rm err')
        with patch(f'{UTILS}.determine_error', return_value='rm err'):
            obj.sync_tags('alice', 'ns1', [{'name': 'env', 'value': 'dev'}], [], purge_tags=True)
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestSyncLock:
    def test_toggle_when_drift(self):
        obj = make_obj()
        changed = obj.sync_lock('alice', 'ns1', current_locked=False, desired_locked=True)
        assert changed is True
        obj.user_mgmt_api.user_management_service_set_user_lock.assert_called_once()

    def test_noop_when_same(self):
        obj = make_obj()
        changed = obj.sync_lock('alice', 'ns1', current_locked=False, desired_locked=False)
        assert changed is False
        obj.user_mgmt_api.user_management_service_set_user_lock.assert_not_called()

    def test_none_desired_noop(self):
        obj = make_obj()
        changed = obj.sync_lock('alice', 'ns1', current_locked=False, desired_locked=None)
        assert changed is False

    def test_api_error_fails(self):
        obj = make_obj()
        obj.user_mgmt_api.user_management_service_set_user_lock.side_effect = Exception('lock err')
        with patch(f'{UTILS}.determine_error', return_value='lock err'):
            obj.sync_lock('alice', 'ns1', current_locked=False, desired_locked=True)
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestSyncSecretKeys:
    def test_returns_false_when_desired_is_none(self):
        obj = make_obj()
        changed, created = obj.sync_secret_keys('alice', 'ns1', None)
        assert changed is False
        assert len(created) == 0

    def test_returns_false_when_desired_is_empty(self):
        obj = make_obj()
        changed, created = obj.sync_secret_keys('alice', 'ns1', [])
        assert changed is False
        assert len(created) == 0

    def test_create_when_none_exist(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[])
        resp = MagicMock()
        resp.to_dict.return_value = {'secret_key': 's3cr3t', 'secret_key_id': 'abc', 'key_timestamp': '2026'}
        obj.secret_key_api.user_secret_key_service_create_new_key_for_user.return_value = resp

        changed, created = obj.sync_secret_keys(
            'alice', 'ns1', [{'state': 'present'}]
        )
        assert changed is True
        assert len(created) == 1
        assert created[0]['secret_key_id'] == 'abc'

    def test_create_with_expiry_time(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[])
        resp = MagicMock()
        resp.to_dict.return_value = {'secret_key': 's3cr3t', 'secret_key_id': 'abc', 'key_timestamp': '2026'}
        obj.secret_key_api.user_secret_key_service_create_new_key_for_user.return_value = resp

        changed, created = obj.sync_secret_keys(
            'alice', 'ns1', [{'state': 'present', 'existing_key_expiry_time_mins': '60'}]
        )
        assert changed is True
        assert len(created) == 1
        obj.secret_key_api.user_secret_key_service_create_new_key_for_user.assert_called_once()
        # Verify expiry time was passed in the payload
        call_args = obj.secret_key_api.user_secret_key_service_create_new_key_for_user.call_args
        payload = call_args[1]['user_secret_key_service_create_new_key_for_user_request']
        # Check for expiry time in either dict or object
        if hasattr(payload, 'existing_key_expiry_time_mins'):
            assert payload.existing_key_expiry_time_mins == '60'
        else:
            assert payload.get('existing_key_expiry_time_mins') == '60'

    def test_create_api_error_fails(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[])
        obj.secret_key_api.user_secret_key_service_create_new_key_for_user.side_effect = Exception('create err')
        with patch(f'{UTILS}.determine_error', return_value='create err'):
            changed, created = obj.sync_secret_keys(
                'alice', 'ns1', [{'state': 'present'}]
            )
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_delete_by_id_only_fails_validation(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[{'secret_key_id': 'abc'}])
        changed, created = obj.sync_secret_keys(
            'alice', 'ns1', [{'state': 'absent', 'secret_key_id': 'abc'}]
        )
        # Should fail with validation error
        assert obj.module.fail_json.called
        assert 'secret_key' in obj.module.fail_json.call_args[1]['msg']

    def test_delete_by_id_and_secret(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[{'secret_key_id': 'abc'}])
        changed, created = obj.sync_secret_keys(
            'alice', 'ns1', [{'state': 'absent', 'secret_key_id': 'abc', 'secret_key': 's3cr3t'}]
        )
        assert changed is True
        obj.secret_key_api.user_secret_key_service_delete_key_for_user.assert_called_once()

    def test_delete_by_secret_only(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[{'secret_key_id': 'abc'}])
        changed, created = obj.sync_secret_keys(
            'alice', 'ns1', [{'state': 'absent', 'secret_key': 's3cr3t'}]
        )
        assert changed is True
        obj.secret_key_api.user_secret_key_service_delete_key_for_user.assert_called_once()

    def test_delete_skip_when_key_already_gone(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[])  # No keys exist
        changed, created = obj.sync_secret_keys(
            'alice', 'ns1', [{'state': 'absent', 'secret_key_id': 'abc', 'secret_key': 's3cr3t'}]
        )
        assert changed is False
        obj.secret_key_api.user_secret_key_service_delete_key_for_user.assert_not_called()

    def test_noop_when_key_present_and_desired_present(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[{'secret_key_id': 'abc'}])
        changed, created = obj.sync_secret_keys(
            'alice', 'ns1', [{'state': 'present', 'secret_key_id': 'abc'}]
        )
        assert changed is False

    def test_delete_api_error_fails(self):
        obj = make_obj()
        obj._list_existing_secret_keys = MagicMock(return_value=[{'secret_key_id': 'abc'}])
        obj.secret_key_api.user_secret_key_service_delete_key_for_user.side_effect = Exception('del err')
        with patch(f'{UTILS}.determine_error', return_value='del err'):
            changed, created = obj.sync_secret_keys(
                'alice', 'ns1', [{'state': 'absent', 'secret_key_id': 'abc', 'secret_key': 's3cr3t'}]
            )
        assert obj.module.exit_json.call_args[1]['failed'] is True


class TestPerformModuleOperation:
    def test_create_when_absent(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'present'})
        obj.get_user_details = MagicMock(side_effect=[None, {'name': 'alice', 'namespace': 'ns1', 'locked': False, 'tag': []}])
        obj.create_user = MagicMock()
        obj.perform_module_operation()
        obj.create_user.assert_called_once()
        assert obj.module.exit_json.call_args[1].get('changed') is True

    def test_update_existing_user_with_tags(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'present', 'tags': [{'name': 'env', 'value': 'prod'}]})
        obj.get_user_details = MagicMock(return_value={'name': 'alice', 'namespace': 'ns1', 'locked': False, 'tag': []})
        obj.sync_tags = MagicMock(return_value=True)
        obj.perform_module_operation()
        obj.sync_tags.assert_called_once()
        assert obj.module.exit_json.call_args[1].get('changed') is True

    def test_update_existing_user_with_lock(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'present', 'locked': True})
        obj.get_user_details = MagicMock(return_value={'name': 'alice', 'namespace': 'ns1', 'locked': False, 'tag': []})
        obj.sync_lock = MagicMock(return_value=True)
        obj.perform_module_operation()
        obj.sync_lock.assert_called_once()
        assert obj.module.exit_json.call_args[1].get('changed') is True

    def test_update_existing_user_with_secret_keys(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'present', 'secret_keys': [{'state': 'present'}]})
        obj.get_user_details = MagicMock(return_value={'name': 'alice', 'namespace': 'ns1', 'locked': False, 'tag': []})
        obj.sync_secret_keys = MagicMock(return_value=(True, [{'secret_key': 's3cr3t', 'secret_key_id': 'abc'}]))
        obj.perform_module_operation()
        obj.sync_secret_keys.assert_called_once()
        assert obj.module.exit_json.call_args[1].get('changed') is True
        assert obj.module.exit_json.call_args[1].get('created_secret_keys') is not None

    def test_absent_existing(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'absent'})
        obj.get_user_details = MagicMock(return_value={'name': 'alice', 'namespace': 'ns1'})
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
        obj = make_obj(params={**BASE_PARAMS, 'state': 'present'}, check_mode=True)
        obj.get_user_details = MagicMock(return_value=None)
        obj.create_user = MagicMock()
        obj.perform_module_operation()
        obj.create_user.assert_not_called()
        assert obj.module.exit_json.call_args[1].get('changed') is True

    def test_check_mode_secret_keys(self):
        obj = make_obj(params={**BASE_PARAMS, 'state': 'present', 'secret_keys': [{'state': 'present'}]}, check_mode=True)
        obj.get_user_details = MagicMock(return_value={'name': 'alice', 'namespace': 'ns1', 'locked': False, 'tag': []})
        obj.sync_secret_keys = MagicMock()
        obj.perform_module_operation()
        obj.sync_secret_keys.assert_not_called()
        assert obj.module.exit_json.call_args[1].get('changed') is False
