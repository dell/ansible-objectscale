# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.namespace'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    namespace_name='testns',
    default_data_services_vpool='urn:storageos:ReplicationGroupInfo:abc:global',
    namespace_admins=None,
    is_compliance_enabled=None,
    is_encryption_enabled=None,
    is_stale_allowed=None,
    allowed_protocols=None,
    default_replication_factor=None,
    quota_enabled=None,
    blocked_quota_size=None,
    notification_quota_size=None,
    soft_quota_size=None,
    hard_quota_size=None,
    state='present',
)


def make_ns_obj(params=None, has_client=True):
    """Helper: return a Namespace instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.namespace import Namespace

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.NamespaceApi'):
        obj = Namespace()

    obj.module = module_mock
    obj.namespace_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestNamespaceInit:

    @patch(f'{MODULE}.NamespaceApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_ns_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace import Namespace
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = Namespace()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace import Namespace
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        Namespace()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace import Namespace
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            Namespace()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# get_namespace_details
# ---------------------------------------------------------------------------

class TestGetNamespaceDetails:

    def test_success(self):
        obj = make_ns_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'id': 'testns', 'name': 'testns'}
        obj.namespace_api.namespace_service_get_namespace.return_value = resp

        result = obj.get_namespace_details('testns')

        assert result == {'id': 'testns', 'name': 'testns'}

    def test_404_returns_none(self):
        obj = make_ns_obj()
        err = Exception("not found")
        err.status = 404
        obj.namespace_api.namespace_service_get_namespace.side_effect = err

        result = obj.get_namespace_details('testns')

        assert result is None

    def test_400_returns_none(self):
        obj = make_ns_obj()
        err = Exception("bad request")
        err.status = 400
        obj.namespace_api.namespace_service_get_namespace.side_effect = err

        result = obj.get_namespace_details('testns')

        assert result is None

    def test_other_exception_calls_exit_json(self):
        obj = make_ns_obj()
        err = Exception("server error")
        err.status = 500
        obj.namespace_api.namespace_service_get_namespace.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_namespace_details('testns')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# create_namespace
# ---------------------------------------------------------------------------

class TestCreateNamespace:

    def test_success(self):
        obj = make_ns_obj()
        params = {**BASE_PARAMS, 'namespace_admins': ['admin@x.com']}

        result = obj.create_namespace('testns', params)

        assert result is True
        obj.namespace_api.namespace_service_create_namespace.assert_called_once()

    def test_success_no_admins(self):
        obj = make_ns_obj()
        params = BASE_PARAMS.copy()

        result = obj.create_namespace('testns', params)

        assert result is True

    def test_missing_vpool_fails(self):
        obj = make_ns_obj()
        params = {**BASE_PARAMS, 'default_data_services_vpool': None}

        obj.create_namespace('testns', params)

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'default_data_services_vpool' in kwargs['msg']

    def test_api_error_fails(self):
        obj = make_ns_obj()
        obj.namespace_api.namespace_service_create_namespace.side_effect = Exception("create err")

        with patch(f'{UTILS}.determine_error', return_value='create err'):
            obj.create_namespace('testns', BASE_PARAMS.copy())

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# modify_namespace
# ---------------------------------------------------------------------------

class TestModifyNamespaceAdvanced:

    def test_success(self):
        obj = make_ns_obj()
        result = obj.modify_namespace('testns', {'is_encryption_enabled': True})
        assert result is True
        obj.namespace_api.namespace_service_update_namespace.assert_called_once()

    def test_api_error_fails(self):
        obj = make_ns_obj()
        obj.namespace_api.namespace_service_update_namespace.side_effect = Exception("mod err")

        with patch(f'{UTILS}.determine_error', return_value='mod err'):
            obj.modify_namespace('testns', {})

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# delete_namespace
# ---------------------------------------------------------------------------

class TestDeleteNamespace:

    def test_success(self):
        obj = make_ns_obj()
        result = obj.delete_namespace('testns')
        assert result is True
        obj.namespace_api.namespace_service_deactivate_namespace.assert_called_once()

    def test_api_error_fails(self):
        obj = make_ns_obj()
        obj.namespace_api.namespace_service_deactivate_namespace.side_effect = Exception("del err")

        with patch(f'{UTILS}.determine_error', return_value='del err'):
            obj.delete_namespace('testns')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# get_quota_details
# ---------------------------------------------------------------------------

class TestGetQuotaDetails:

    def test_success(self):
        obj = make_ns_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'block_size': 1024}
        obj.namespace_api.namespace_service_get_namespace_quota.return_value = resp

        result = obj.get_quota_details('testns')

        assert result == {'block_size': 1024}

    def test_exception_warns_and_returns_none(self):
        obj = make_ns_obj()
        obj.namespace_api.namespace_service_get_namespace_quota.side_effect = Exception("quota err")

        result = obj.get_quota_details('testns')

        assert result is None
        obj.module.warn.assert_called_once()


class TestNormalizeHelpers:

    def test_normalize_string_list(self):
        obj = make_ns_obj()
        assert obj._normalize_string_list('a, b , ,c') == ['a', 'b', 'c']
        assert obj._normalize_string_list(['a', ' ', 'b']) == ['a', 'b']
        assert obj._normalize_string_list(42) == []

    def test_normalize_user_mapping(self):
        obj = make_ns_obj()
        with_to_dict = MagicMock()
        with_to_dict.to_dict.return_value = {'domain': 'example.com'}

        result = obj._normalize_user_mapping([
            {'domain': 'example.com', 'groups': ['ops']},
            with_to_dict,
        ])

        assert len(result) == 2

    def test_normalize_retention_classes_success(self):
        obj = make_ns_obj()
        result = obj._normalize_retention_classes([
            {'name': 'gold', 'period': 86400},
            {'name': 'silver', 'period': '3600'},
        ])
        assert result == {'gold': 86400, 'silver': 3600}

    def test_normalize_retention_classes_validation_errors(self):
        obj = make_ns_obj()

        obj._normalize_retention_classes('invalid')
        assert obj.module.exit_json.call_args[1]['failed'] is True

        obj.module.exit_json.reset_mock()
        obj._normalize_retention_classes([{'name': 'gold'}])
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_normalize_retention_classes_non_dict_entry(self):
        obj = make_ns_obj()
        obj._normalize_retention_classes(['not-a-dict'])
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_normalize_retention_classes_bad_period(self):
        obj = make_ns_obj()
        obj._normalize_retention_classes([{'name': 'gold', 'period': 'abc'}])
        assert obj.module.exit_json.call_args[1]['failed'] is True

    def test_normalize_string_list_none(self):
        obj = make_ns_obj()
        assert obj._normalize_string_list(None) == []

    def test_normalize_user_mapping_non_list(self):
        obj = make_ns_obj()
        assert obj._normalize_user_mapping('not-a-list') == []

    def test_normalize_user_mapping_none(self):
        obj = make_ns_obj()
        assert obj._normalize_user_mapping(None) == []


class TestRetentionClasses:

    def test_get_retention_classes_success(self):
        obj = make_ns_obj()
        c1 = MagicMock()
        c1.name = 'gold'
        c1.period = 86400
        c2 = MagicMock()
        c2.name = 'silver'
        c2.period = 3600
        response = MagicMock()
        response.retention_class = [c1, c2]
        obj.namespace_api.namespace_service_get_retention_classes.return_value = response

        result = obj.get_retention_classes('testns')

        assert result == {'gold': 86400, 'silver': 3600}

    def test_get_retention_classes_not_found(self):
        obj = make_ns_obj()
        err = Exception('not found')
        err.status = 404
        obj.namespace_api.namespace_service_get_retention_classes.side_effect = err

        result = obj.get_retention_classes('testns')

        assert result == {}

    def test_sync_retention_classes_create_and_update(self):
        obj = make_ns_obj()
        obj.get_retention_classes = MagicMock(return_value={'gold': 100})

        changed = obj.sync_retention_classes('testns', [
            {'name': 'gold', 'period': 200},
            {'name': 'silver', 'period': 300},
        ])

        assert changed is True
        obj.namespace_api.namespace_service_create_retention_class.assert_called_once()
        obj.namespace_api.namespace_service_update_retention_class.assert_called_once()

    def test_sync_retention_classes_no_change(self):
        obj = make_ns_obj()
        obj.get_retention_classes = MagicMock(return_value={'gold': 100})

        changed = obj.sync_retention_classes('testns', [
            {'name': 'gold', 'period': 100},
        ])

        assert changed is False
        obj.namespace_api.namespace_service_create_retention_class.assert_not_called()
        obj.namespace_api.namespace_service_update_retention_class.assert_not_called()


# ---------------------------------------------------------------------------
# modify_quota
# ---------------------------------------------------------------------------

class TestModifyQuota:

    def test_returns_false_if_no_quota_fields(self):
        obj = make_ns_obj()
        params = {k: None for k in ['blocked_quota_size', 'notification_quota_size',
                                    'hard_quota_size', 'soft_quota_size']}
        result = obj.modify_quota('testns', params)
        assert result is False

    def test_success_with_fields(self):
        obj = make_ns_obj()
        params = {'blocked_quota_size': 1024, 'hard_quota_size': 2048,
                  'notification_quota_size': None, 'soft_quota_size': None}

        result = obj.modify_quota('testns', params)

        assert result is True
        obj.namespace_api.namespace_service_update_namespace_quota.assert_called_once()

    def test_api_error_fails(self):
        obj = make_ns_obj()
        obj.namespace_api.namespace_service_update_namespace_quota.side_effect = Exception("quota upd err")
        params = {'blocked_quota_size': 512, 'notification_quota_size': None,
                  'hard_quota_size': None, 'soft_quota_size': None}

        with patch(f'{UTILS}.determine_error', return_value='quota upd err'):
            obj.modify_quota('testns', params)

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_disable_quota_calls_remove(self):
        obj = make_ns_obj()
        result = obj.modify_quota('testns', {'quota_enabled': False})
        assert result is True
        obj.namespace_api.namespace_service_remove_namespace_quota.assert_called_once_with(namespace='testns')

    def test_disable_quota_remove_error(self):
        obj = make_ns_obj()
        obj.namespace_api.namespace_service_remove_namespace_quota.side_effect = Exception("rm err")

        with patch(f'{UTILS}.determine_error', return_value='rm err'):
            obj.modify_quota('testns', {'quota_enabled': False})

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'rm err' in kwargs['msg']


class TestGetRetentionClassesErrors:

    def test_get_retention_classes_server_error(self):
        obj = make_ns_obj()
        err = Exception('server error')
        err.status = 500
        obj.namespace_api.namespace_service_get_retention_classes.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_retention_classes('testns')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'server error' in kwargs['msg']

    def test_sync_retention_classes_api_error(self):
        obj = make_ns_obj()
        obj.get_retention_classes = MagicMock(return_value={})
        obj.namespace_api.namespace_service_create_retention_class.side_effect = Exception("create err")

        with patch(f'{UTILS}.determine_error', return_value='create err'):
            obj.sync_retention_classes('testns', [{'name': 'gold', 'period': 100}])

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'create err' in kwargs['msg']


class TestIsQuotaModifiedExtended:

    def test_none_quota_with_quota_fields_returns_true(self):
        obj = make_ns_obj()
        params = {**BASE_PARAMS, 'hard_quota_size': 1024}
        assert obj.is_quota_modified(None, params) is True

    def test_none_quota_with_quota_disabled_returns_true(self):
        obj = make_ns_obj()
        params = {**BASE_PARAMS, 'quota_enabled': False}
        assert obj.is_quota_modified(None, params) is True

    def test_quota_enabled_false_returns_true(self):
        obj = make_ns_obj()
        quota = {'block_size': 1024}
        params = {**BASE_PARAMS, 'quota_enabled': False}
        assert obj.is_quota_modified(quota, params) is True


class TestIsNamespaceModifiedPassword:

    def test_password_only_current_fails(self):
        obj = make_ns_obj()
        details = {}
        params = {**BASE_PARAMS, 'current_root_user_password': 'old', 'new_root_user_password': None}
        obj.is_namespace_modified(details, params)
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'Both' in kwargs['msg']


class TestCreateNamespaceExtended:

    def test_create_with_all_fields(self):
        obj = make_ns_obj()
        params = {
            **BASE_PARAMS,
            'namespace_admins': ['admin@x.com'],
            'external_group_admins': ['ad-group'],
            'default_object_project': 'proj1',
            'allowed_vpools_list': ['vp1'],
            'disallowed_vpools_list': ['vp2'],
            'user_mapping': [{'domain': 'example.com'}],
            'is_compliance_enabled': True,
            'is_encryption_enabled': True,
            'default_bucket_block_size': 1024,
            'is_stale_allowed': False,
            'is_object_lock_with_ado_allowed': True,
            'default_audit_delete_expiration': 86400,
            'root_user_password': 'secret',
        }
        result = obj.create_namespace('testns', params)
        assert result is True
        obj.namespace_api.namespace_service_create_namespace.assert_called_once()


class TestModifyNamespaceErrors:

    def test_modify_namespace_api_error(self):
        obj = make_ns_obj()
        obj.namespace_api.namespace_service_update_namespace.side_effect = Exception("upd err")

        with patch(f'{UTILS}.determine_error', return_value='upd err'):
            obj.modify_namespace('testns', {'user_mapping': []})

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'upd err' in kwargs['msg']


class TestIsNamespaceModified:

    def _obj(self):
        return make_ns_obj()

    def test_no_change(self):
        obj = self._obj()
        details = {'is_encryption_enabled': True, 'is_compliance_enabled': False,
                   'is_stale_allowed': False, 'default_replication_factor': 1}
        params = {**BASE_PARAMS, 'is_encryption_enabled': True, 'is_compliance_enabled': False}
        result = obj.is_namespace_modified(details, params)
        assert result == {}

    def test_scalar_field_changed(self):
        obj = self._obj()
        details = {'is_encryption_enabled': False, 'is_stale_allowed': False,
                   'is_compliance_enabled': False, 'default_replication_factor': 1}
        params = {**BASE_PARAMS, 'is_encryption_enabled': True}
        result = obj.is_namespace_modified(details, params)
        assert result == {'is_encryption_enabled': True}

    def test_admins_changed_from_string(self):
        obj = self._obj()
        details = {'namespace_admins': 'old@x.com', 'is_encryption_enabled': None,
                   'is_compliance_enabled': None, 'is_stale_allowed': None,
                   'default_replication_factor': None}
        params = {**BASE_PARAMS, 'namespace_admins': ['new@x.com']}
        result = obj.is_namespace_modified(details, params)
        assert 'namespace_admins' in result

    def test_admins_unchanged_string(self):
        obj = self._obj()
        details = {'namespace_admins': 'admin@x.com', 'is_encryption_enabled': None,
                   'is_compliance_enabled': None, 'is_stale_allowed': None,
                   'default_replication_factor': None}
        params = {**BASE_PARAMS, 'namespace_admins': ['admin@x.com']}
        result = obj.is_namespace_modified(details, params)
        assert 'namespace_admins' not in result

    def test_admins_changed_from_list(self):
        obj = self._obj()
        details = {'namespace_admins': ['old@x.com'], 'is_encryption_enabled': None,
                   'is_compliance_enabled': None, 'is_stale_allowed': None,
                   'default_replication_factor': None}
        params = {**BASE_PARAMS, 'namespace_admins': ['new@x.com']}
        result = obj.is_namespace_modified(details, params)
        assert 'namespace_admins' in result

    def test_admins_from_other_type(self):
        obj = self._obj()
        details = {'namespace_admins': 12345, 'is_encryption_enabled': None,
                   'is_compliance_enabled': None, 'is_stale_allowed': None,
                   'default_replication_factor': None}
        params = {**BASE_PARAMS, 'namespace_admins': ['new@x.com']}
        result = obj.is_namespace_modified(details, params)
        assert 'namespace_admins' in result

    def test_protocols_changed_from_dict(self):
        obj = self._obj()
        details = {'allowed_protocols': {'protocol': ['s3']}, 'is_encryption_enabled': None,
                   'is_compliance_enabled': None, 'is_stale_allowed': None,
                   'default_replication_factor': None}
        params = {**BASE_PARAMS, 'allowed_protocols': ['s3', 'swift']}
        result = obj.is_namespace_modified(details, params)
        assert 'allowed_protocols' in result

    def test_protocols_unchanged_from_list(self):
        obj = self._obj()
        details = {'allowed_protocols': ['s3'], 'is_encryption_enabled': None,
                   'is_compliance_enabled': None, 'is_stale_allowed': None,
                   'default_replication_factor': None}
        params = {**BASE_PARAMS, 'allowed_protocols': ['s3']}
        result = obj.is_namespace_modified(details, params)
        assert 'allowed_protocols' not in result

    def test_external_group_admins_changed(self):
        obj = self._obj()
        details = {'external_group_admins': 'old-group'}
        params = {**BASE_PARAMS, 'external_group_admins': ['new-group']}
        result = obj.is_namespace_modified(details, params)
        assert 'external_group_admins' in result

    def test_allowed_disallowed_vpool_diffs(self):
        obj = self._obj()
        details = {
            'allowed_vpools_list': ['vp1', 'vp2'],
            'disallowed_vpools_list': ['vp3'],
        }
        params = {
            **BASE_PARAMS,
            'allowed_vpools_list': ['vp2', 'vp4'],
            'disallowed_vpools_list': ['vp5'],
        }
        result = obj.is_namespace_modified(details, params)
        assert result['vpools_added_to_allowed_vpools_list'] == ['vp4']
        assert result['vpools_removed_from_allowed_vpools_list'] == ['vp1']
        assert result['vpools_added_to_disallowed_vpools_list'] == ['vp5']
        assert result['vpools_removed_from_disallowed_vpools_list'] == ['vp3']

    def test_user_mapping_and_password_update(self):
        obj = self._obj()
        details = {'user_mapping': [{'domain': 'example.com', 'groups': ['ops']}]}
        params = {
            **BASE_PARAMS,
            'user_mapping': [{'domain': 'example.com', 'groups': ['dev']}],
            'current_root_user_password': 'oldpass',
            'new_root_user_password': 'newpass',
        }
        result = obj.is_namespace_modified(details, params)
        assert 'user_mapping' in result
        assert result['current_root_user_password'] == 'oldpass'
        assert result['new_root_user_password'] == 'newpass'


# ---------------------------------------------------------------------------
# is_quota_modified
# ---------------------------------------------------------------------------

class TestIsQuotaModified:

    def _obj(self):
        return make_ns_obj()

    def test_none_quota_details(self):
        obj = self._obj()
        assert obj.is_quota_modified(None, BASE_PARAMS) is False

    def test_no_change(self):
        obj = self._obj()
        quota = {'quota_enabled': True, 'blocked_quota_size': 1024}
        params = {**BASE_PARAMS, 'quota_enabled': True, 'blocked_quota_size': 1024}
        assert obj.is_quota_modified(quota, params) is False

    def test_change_detected(self):
        obj = self._obj()
        quota = {'quota_enabled': False, 'blocked_quota_size': 1024}
        params = {**BASE_PARAMS, 'quota_enabled': True}
        assert obj.is_quota_modified(quota, params) is True

    def test_change_detected_with_api_field_mapping(self):
        obj = self._obj()
        quota = {'block_size': 1024}
        params = {**BASE_PARAMS, 'blocked_quota_size': 2048}
        assert obj.is_quota_modified(quota, params) is True


class TestModifyNamespace:

    def test_modify_namespace_fetches_user_mapping_when_missing(self):
        obj = make_ns_obj()
        obj.get_namespace_details = MagicMock(return_value={'user_mapping': [{'domain': 'example.com'}]})

        result = obj.modify_namespace('testns', {'is_encryption_enabled': True})

        assert result is True
        obj.get_namespace_details.assert_called_once_with('testns')
        obj.namespace_api.namespace_service_update_namespace.assert_called_once()

    def test_modify_namespace_normalizes_admin_fields(self):
        obj = make_ns_obj()

        result = obj.modify_namespace(
            'testns',
            {
                'namespace_admins': ['admin@example.com'],
                'external_group_admins': ['ad-group'],
                'user_mapping': [],
            },
            namespace_details={},
        )

        assert result is True
        kwargs = obj.namespace_api.namespace_service_update_namespace.call_args[1]
        assert kwargs['namespace'] == 'testns'
        assert kwargs['namespace_service_update_namespace_request'] is not None


# ---------------------------------------------------------------------------
# perform_module_operation
# ---------------------------------------------------------------------------

class TestPerformModuleOperation:

    def _make(self, params):
        obj = make_ns_obj(params=params)
        obj.get_namespace_details = MagicMock()
        obj.create_namespace = MagicMock(return_value=True)
        obj.modify_namespace = MagicMock(return_value=True)
        obj.delete_namespace = MagicMock(return_value=True)
        obj.get_quota_details = MagicMock(return_value=None)
        obj.is_namespace_modified = MagicMock(return_value={})
        obj.is_quota_modified = MagicMock(return_value=False)
        obj.modify_quota = MagicMock(return_value=True)
        obj.sync_retention_classes = MagicMock(return_value=False)
        return obj

    def test_state_absent_namespace_exists(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_namespace_details.return_value = {'id': 'testns'}

        obj.perform_module_operation()

        obj.delete_namespace.assert_called_once_with('testns')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_state_absent_namespace_missing(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_namespace_details.return_value = None

        obj.perform_module_operation()

        obj.delete_namespace.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_state_present_creates_namespace(self):
        obj = self._make(BASE_PARAMS.copy())
        ns_detail = {'id': 'testns'}
        # Called 3 times: initial check, after create, after quota change
        obj.get_namespace_details.side_effect = [None, ns_detail, ns_detail]

        obj.perform_module_operation()

        obj.create_namespace.assert_called_once_with('testns', obj.module.params)
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_state_present_quota_on_new_namespace(self):
        """Cover lines 522-523: quota fields set, namespace just created but
        post-create get_namespace_details still returns None."""
        params = {**BASE_PARAMS, 'hard_quota_size': 1024}
        obj = self._make(params)
        # initial check → None, after create → None, final refresh → detail
        obj.get_namespace_details.side_effect = [None, None, {'id': 'testns'}]
        obj.is_quota_modified.return_value = False

        obj.perform_module_operation()

        obj.modify_quota.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_state_present_no_change(self):
        obj = self._make(BASE_PARAMS.copy())
        ns_detail = {'id': 'testns', 'name': 'testns'}
        obj.get_namespace_details.return_value = ns_detail

        obj.perform_module_operation()

        obj.create_namespace.assert_not_called()
        obj.modify_namespace.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_state_present_modifies_namespace(self):
        obj = self._make(BASE_PARAMS.copy())
        ns_detail = {'id': 'testns'}
        obj.get_namespace_details.side_effect = [ns_detail, ns_detail]
        obj.is_namespace_modified.return_value = {'is_encryption_enabled': True}

        obj.perform_module_operation()

        obj.modify_namespace.assert_called_once_with('testns', {'is_encryption_enabled': True})
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_state_present_modifies_quota(self):
        params = {**BASE_PARAMS, 'quota_enabled': True}
        obj = self._make(params)
        ns_detail = {'id': 'testns'}
        obj.get_namespace_details.side_effect = [ns_detail, ns_detail]
        obj.get_quota_details.return_value = {'quota_enabled': False}
        obj.is_quota_modified.return_value = True

        obj.perform_module_operation()

        obj.modify_quota.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_get_namespace_parameters_returns_dict(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace import Namespace
        params = Namespace.get_namespace_parameters()
        assert 'namespace_name' in params
        assert 'state' in params

    def test_state_present_syncs_retention_classes(self):
        params = {**BASE_PARAMS, 'retention_classes': [{'name': 'gold', 'period': 100}]}
        obj = self._make(params)
        ns_detail = {'id': 'testns'}
        obj.get_namespace_details.side_effect = [ns_detail, ns_detail]
        obj.sync_retention_classes.return_value = True

        obj.perform_module_operation()

        obj.sync_retention_classes.assert_called_once_with('testns', params['retention_classes'])
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

class TestNamespaceMain:

    @patch(f'{MODULE}.Namespace')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.namespace import main
        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()
        mock_obj.perform_module_operation.assert_called_once()
