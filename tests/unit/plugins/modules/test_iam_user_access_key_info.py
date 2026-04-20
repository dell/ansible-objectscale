# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the dellemc.objectscale.iam_user_access_key_info module."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key_info'
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


def _list_response(keys, truncated=False, marker=None):
    resp = MagicMock()
    resp.to_dict.return_value = {
        'ListAccessKeysResult': {
            'AccessKeyMetadata': keys,
            'IsTruncated': truncated,
            'Marker': marker,
        }
    }
    return resp


def make_obj(params=None, has_client=True):
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key_info import (
        IamUserAccessKeyInfo,
    )
    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock.exit_json.side_effect = SystemExit
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection',
               return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamUserAccessKeyInfo()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    obj.namespace = module_mock.params.get('namespace_name')
    return obj


class TestInit:

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, _mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key_info import (
            IamUserAccessKeyInfo,
        )
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        IamUserAccessKeyInfo()

        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_missing_client_uses_exit_json_fail(self, mock_am, _mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_access_key_info import (
            IamUserAccessKeyInfo,
        )
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        IamUserAccessKeyInfo()

        mock_module.fail_json.assert_not_called()
        mock_module.exit_json.assert_called_once()
        kwargs = mock_module.exit_json.call_args[1]
        assert kwargs.get('failed') is True


class TestListAccessKeys:

    def test_list_empty(self):
        obj = make_obj()
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response([])
        assert obj.list_access_keys('sample_user_1') == []

    def test_list_paginates(self):
        obj = make_obj()
        page1 = _list_response([_mock_key('AKIA1')], truncated=True, marker='m1')
        page2 = _list_response([_mock_key('AKIA2')])
        obj.iam_api.iam_service_list_access_keys.side_effect = [page1, page2]

        result = obj.list_access_keys('sample_user_1')
        assert [k['AccessKeyId'] for k in result] == ['AKIA1', 'AKIA2']

    def test_list_error_uses_exit_json_fail(self):
        obj = make_obj()
        obj.iam_api.iam_service_list_access_keys.side_effect = Exception('permission')
        with patch(f'{UTILS}.determine_error', return_value='permission'):
            try:
                obj.list_access_keys('sample_user_1')
            except SystemExit:
                pass

        obj.module.fail_json.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs.get('failed') is True
        assert 'sample_user_1' in kwargs['msg']


class TestReadAndList:

    def test_list_all_returns_all_keys(self):
        obj = make_obj(params=_params())
        keys = [_mock_key('AKIA1'), _mock_key('AKIA2', status='Inactive')]
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(keys)

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['access_keys'] == keys

    def test_read_specific_key_by_id(self):
        obj = make_obj(params=_params(access_key_id='AKIA2'))
        keys = [_mock_key('AKIA1'), _mock_key('AKIA2', status='Inactive')]
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(keys)

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['access_keys']) == 1
        assert kwargs['access_keys'][0]['AccessKeyId'] == 'AKIA2'

    def test_read_missing_key_returns_empty(self):
        obj = make_obj(params=_params(access_key_id='AKIA_MISSING'))
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(
            [_mock_key('AKIA1')]
        )

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['access_keys'] == []

    def test_info_never_returns_secret(self):
        """Info module must NEVER return SecretAccessKey."""
        obj = make_obj(params=_params())
        # Even if API returned a secret (it doesn't), we pass through only
        # what the server provides. Verify no secret ever appears when only
        # metadata is returned.
        keys = [_mock_key('AKIA1')]
        obj.iam_api.iam_service_list_access_keys.return_value = _list_response(keys)

        try:
            obj.perform_module_operation()
        except SystemExit:
            pass

        kwargs = obj.module.exit_json.call_args[1]
        for k in kwargs['access_keys']:
            assert 'SecretAccessKey' not in k
