# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the dellemc.objectscale.iam_user_access_key module."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    user_name='sample_user_1',
    namespace_name='ns1',
    access_key_id=None,
    status=None,
    state='present',
)


def _params(**overrides):
    p = BASE_PARAMS.copy()
    p.update(overrides)
    return p


def _mock_key(key_id='AKIA1', status='Active', user_name='sample_user_1'):
    return {
        'AccessKeyId': key_id,
        'UserName': user_name,
        'Status': status,
        'CreateDate': '2025-01-15T10:30:00Z',
    }


def _mock_created_key(key_id='AKIANEW'):
    return {
        'AccessKeyId': key_id,
        'UserName': 'sample_user_1',
        'Status': 'Active',
        'CreateDate': '2025-01-15T10:30:00Z',
        'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY',
    }


def make_obj(params=None, check_mode=False, diff=False, has_client=True):
    """Return a fully-mocked IamUserAccessKey instance."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key import (
        IamUserAccessKey,
    )

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = check_mode
    module_mock._diff = diff
    module_mock.exit_json.side_effect = SystemExit
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection',
               return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamUserAccessKey()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    obj.namespace = module_mock.params.get('namespace_name')
    return obj


def _list_response(keys, truncated=False, marker=None):
    """Build a mocked list_access_keys response object."""
    resp = MagicMock()
    resp.to_dict.return_value = {
        'ListAccessKeysResult': {
            'AccessKeyMetadata': keys,
            'IsTruncated': truncated,
            'Marker': marker,
        }
    }
    return resp


# ===========================================================================
# Init
# ===========================================================================


class TestInit:

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key import (
            IamUserAccessKey,
        )
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        obj = IamUserAccessKey()

        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_missing_client_uses_exit_json_with_fail(self, mock_am, _mock_conn):
        """Spec mandates exit_json(fail=True) over fail_json."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key import (
            IamUserAccessKey,
        )
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        IamUserAccessKey()

        mock_module.fail_json.assert_not_called()
        mock_module.exit_json.assert_called_once()
        kwargs = mock_module.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'objectscale_client' in kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key import (
            IamUserAccessKey,
        )
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamUserAccessKey()

        mock_module.fail_json.assert_not_called()
        mock_module.exit_json.assert_called_once()
        kwargs = mock_module.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'conn failed' in kwargs['msg']


# ===========================================================================
# list_access_keys / find_access_key
# ===========================================================================


class TestListAccessKeys:

    def test_list_empty(self):
        obj = make_obj()
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response([])
        assert obj.list_access_keys('sample_user_1') == []

    def test_list_single_page(self):
        obj = make_obj()
        keys = [_mock_key('AKIA1'), _mock_key('AKIA2', status='Inactive')]
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(keys)

        result = obj.list_access_keys('sample_user_1')

        assert result == keys
        obj.iam_api.iam_service_list_access_keys.assert_called_once_with(
            user_name='sample_user_1', x_emc_namespace='ns1',
        )

    def test_list_paginates(self):
        obj = make_obj()
        page1 = _list_response([_mock_key('AKIA1')], truncated=True, marker='m1')
        page2 = _list_response([_mock_key('AKIA2')])
        obj.iam_api.iam_service_list_access_keys.side_effect = [page1, page2]

        result = obj.list_access_keys('sample_user_1')

        assert [k['AccessKeyId'] for k in result] == ['AKIA1', 'AKIA2']
        assert obj.iam_api.iam_service_list_access_keys.call_count == 2
        second_call_kwargs = obj.iam_api.iam_service_list_access_keys.call_args_list[1][1]
        assert second_call_kwargs['marker'] == 'm1'

    def test_list_error_uses_exit_json_fail(self):
        obj = make_obj()
        obj.iam_api.iam_service_list_access_keys.side_effect = Exception('boom')
        with patch(f'{UTILS}.determine_error', return_value='boom'):
            try:
                obj.list_access_keys('sample_user_1')
            except SystemExit:
                pass

        obj.module.fail_json.assert_not_called()
        obj.module.exit_json.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'boom' in kwargs['msg']
        assert 'sample_user_1' in kwargs['msg']

    def test_find_access_key_found(self):
        obj = make_obj()
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1'), _mock_key('AKIA2', status='Inactive')]
        )
        found = obj.find_access_key('sample_user_1', 'AKIA2')
        assert found is not None
        assert found['Status'] == 'Inactive'

    def test_find_access_key_missing(self):
        obj = make_obj()
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response([
            _mock_key('AKIA1'),
        ])
        assert obj.find_access_key('sample_user_1', 'AKIA_MISSING') is None


# ===========================================================================
# create_access_key
# ===========================================================================


class TestCreateAccessKey:

    def test_create_success_returns_secret(self):
        obj = make_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {
            'CreateAccessKeyResult': {'AccessKey': _mock_created_key()}
        }
        obj.iam_api.iam_service_create_access_key.return_value = resp

        result = obj.create_access_key('sample_user_1')

        assert result['AccessKeyId'] == 'AKIANEW'
        assert 'SecretAccessKey' in result
        obj.iam_api.iam_service_create_access_key.assert_called_once_with(
            user_name='sample_user_1', x_emc_namespace='ns1',
        )

    def test_create_error_uses_exit_json_fail_no_fail_json(self):
        obj = make_obj()
        obj.iam_api.iam_service_create_access_key.side_effect = Exception('LimitExceeded')
        with patch(f'{UTILS}.determine_error', return_value='LimitExceeded'):
            try:
                obj.create_access_key('sample_user_1')
            except SystemExit:
                pass

        obj.module.fail_json.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'LimitExceeded' in kwargs['msg']
        # Clear, actionable message
        assert 'maximum number' in kwargs['msg']


# ===========================================================================
# delete_access_key
# ===========================================================================


class TestDeleteAccessKey:

    def test_delete_success(self):
        obj = make_obj()
        obj.delete_access_key('sample_user_1', 'AKIA1')
        obj.iam_api.iam_service_delete_access_key.assert_called_once_with(
            access_key_id='AKIA1', user_name='sample_user_1', x_emc_namespace='ns1',
        )

    def test_delete_error_uses_exit_json_fail(self):
        obj = make_obj()
        obj.iam_api.iam_service_delete_access_key.side_effect = Exception('perm denied')
        with patch(f'{UTILS}.determine_error', return_value='perm denied'):
            try:
                obj.delete_access_key('sample_user_1', 'AKIA1')
            except SystemExit:
                pass

        obj.module.fail_json.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'perm denied' in kwargs['msg']
        assert 'AKIA1' in kwargs['msg']


# ===========================================================================
# update_access_key_status
# ===========================================================================


class TestUpdateStatus:

    def test_update_success(self):
        obj = make_obj()
        obj.update_access_key_status('sample_user_1', 'AKIA1', 'Inactive')
        obj.iam_api.iam_service_update_access_key.assert_called_once_with(
            access_key_id='AKIA1', status='Inactive',
            user_name='sample_user_1', x_emc_namespace='ns1',
        )

    def test_update_error_uses_exit_json_fail(self):
        obj = make_obj()
        obj.iam_api.iam_service_update_access_key.side_effect = Exception('nope')
        with patch(f'{UTILS}.determine_error', return_value='nope'):
            try:
                obj.update_access_key_status('sample_user_1', 'AKIA1', 'Active')
            except SystemExit:
                pass

        obj.module.fail_json.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('failed') is True


# ===========================================================================
# Sanitization for diff
# ===========================================================================


class TestSanitize:

    def test_secret_never_in_diff(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key import (
            IamUserAccessKey, REDACTED, NEW_SECRET_MARKER,
        )
        key = _mock_created_key()
        sanitized = IamUserAccessKey._sanitize_for_diff(key)
        assert sanitized['SecretAccessKey'] == REDACTED
        assert 'wJalrXUtnFEMI' not in str(sanitized)

        new_key_sanitized = IamUserAccessKey._sanitize_for_diff(
            key, secret_marker=NEW_SECRET_MARKER,
        )
        assert new_key_sanitized['SecretAccessKey'] == NEW_SECRET_MARKER

    def test_sanitize_empty(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key import (
            IamUserAccessKey,
        )
        assert IamUserAccessKey._sanitize_for_diff(None) == {}
        assert IamUserAccessKey._sanitize_for_diff({}) == {}


# ===========================================================================
# perform_module_operation - state=present, create
# ===========================================================================


class TestCreateFlow:

    def test_create_new_key_when_no_id(self):
        obj = make_obj(params=_params())
        resp = MagicMock()
        resp.to_dict.return_value = {
            'CreateAccessKeyResult': {'AccessKey': _mock_created_key()}
        }
        obj.iam_api.iam_service_create_access_key.return_value = resp

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert kwargs['access_key']['AccessKeyId'] == 'AKIANEW'
        assert kwargs['access_key']['SecretAccessKey']  # only place secret is returned

    def test_create_in_check_mode_does_not_call_api(self):
        obj = make_obj(params=_params(), check_mode=True, diff=True)

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.iam_api.iam_service_create_access_key.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert 'diff' in kwargs
        assert kwargs['diff']['before'] == {}
        assert kwargs['diff']['after']['SecretAccessKey'] == '<NEW_SECRET_KEY_GENERATED>'

    def test_create_diff_mode_redacts_secret(self):
        obj = make_obj(params=_params(), diff=True)
        resp = MagicMock()
        resp.to_dict.return_value = {
            'CreateAccessKeyResult': {'AccessKey': _mock_created_key()}
        }
        obj.iam_api.iam_service_create_access_key.return_value = resp

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        kwargs = obj.module.exit_json.call_args[1]
        diff = kwargs['diff']
        assert diff['before'] == {}
        assert diff['after']['SecretAccessKey'] == '<NEW_SECRET_KEY_GENERATED>'
        # Actual secret must never appear in diff
        assert 'wJalrXUtnFEMI' not in str(diff)


# ===========================================================================
# perform_module_operation - state=present, update status
# ===========================================================================


class TestUpdateFlow:

    def test_update_status_changes_when_different(self):
        params = _params(access_key_id='AKIA1', status='Inactive')
        obj = make_obj(params=params)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1', status='Active')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.iam_api.iam_service_update_access_key.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert kwargs['access_key']['Status'] == 'Inactive'

    def test_update_status_idempotent_when_same(self):
        params = _params(access_key_id='AKIA1', status='Active')
        obj = make_obj(params=params)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1', status='Active')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.iam_api.iam_service_update_access_key.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_update_unknown_key_fails_with_exit_json(self):
        params = _params(access_key_id='AKIA_MISSING', status='Inactive')
        obj = make_obj(params=params)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response([
            _mock_key('AKIA1'),
        ])

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.module.fail_json.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'AKIA_MISSING' in kwargs['msg']

    def test_update_diff_shows_before_after_redacted(self):
        params = _params(access_key_id='AKIA1', status='Inactive')
        obj = make_obj(params=params, diff=True)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1', status='Active')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        diff = obj.module.exit_json.call_args[1]['diff']
        assert diff['before']['Status'] == 'Active'
        assert diff['after']['Status'] == 'Inactive'
        assert diff['before']['SecretAccessKey'] == '<REDACTED>'
        assert diff['after']['SecretAccessKey'] == '<REDACTED>'

    def test_update_check_mode_does_not_call_api(self):
        params = _params(access_key_id='AKIA1', status='Inactive')
        obj = make_obj(params=params, check_mode=True)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1', status='Active')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.iam_api.iam_service_update_access_key.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True


# ===========================================================================
# perform_module_operation - state=absent
# ===========================================================================


class TestDeleteFlow:

    def test_delete_existing_key(self):
        params = _params(state='absent', access_key_id='AKIA1')
        obj = make_obj(params=params)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.iam_api.iam_service_delete_access_key.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_delete_missing_is_idempotent(self):
        params = _params(state='absent', access_key_id='AKIA_MISSING')
        obj = make_obj(params=params)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response([
            _mock_key('AKIA1'),
        ])

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.iam_api.iam_service_delete_access_key.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_delete_check_mode(self):
        params = _params(state='absent', access_key_id='AKIA1')
        obj = make_obj(params=params, check_mode=True)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        obj.iam_api.iam_service_delete_access_key.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_delete_diff_shows_before_with_redacted_secret(self):
        params = _params(state='absent', access_key_id='AKIA1')
        obj = make_obj(params=params, diff=True)
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        diff = obj.module.exit_json.call_args[1]['diff']
        assert diff['after'] == {}
        assert diff['before']['AccessKeyId'] == 'AKIA1'
        assert diff['before']['SecretAccessKey'] == '<REDACTED>'
