# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_group_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    namespace='ns1',
    group_name=None,
)


def make_obj(params=None, has_client=True):
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_group_info import IamGroupInfo

    module_mock = MagicMock()
    module_mock.params = params or PARAMS.copy()
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamGroupInfo()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


class TestIamGroupInfoInit:

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group_info import IamGroupInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        obj = IamGroupInfo()

        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group_info import IamGroupInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        IamGroupInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.IamApi', None)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_iam_api_unavailable(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group_info import IamGroupInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        IamGroupInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert kwargs['msg'] == 'IamApi is not available.'

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group_info import IamGroupInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        with patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('conn failed')):
            IamGroupInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'Failed to connect to ObjectScale' in kwargs['msg']


class TestIamGroupInfoOperations:

    def test_list_groups_success(self):
        obj = make_obj()
        obj.iam_api.list_groups.return_value = [{'GroupName': 'devs'}]

        result = obj.list_groups('ns1')

        obj.iam_api.list_groups.assert_called_once_with('ns1')
        assert result == [{'GroupName': 'devs'}]

    def test_list_groups_error(self):
        obj = make_obj()
        obj.iam_api.list_groups.side_effect = Exception('IAM error')

        with patch(f'{UTILS}.determine_error', return_value='IAM error'):
            obj.list_groups('ns1')

        obj.module.fail_json.assert_called_once()
        kwargs = obj.module.fail_json.call_args[1]
        assert 'IAM error' in kwargs['msg']

    def test_get_group_success(self):
        obj = make_obj(params={**PARAMS, 'group_name': 'devs'})
        obj.iam_api.get_group.return_value = {'GroupName': 'devs'}

        result = obj.get_group('devs', 'ns1')

        obj.iam_api.get_group.assert_called_once_with('devs', 'ns1')
        assert result == [{'GroupName': 'devs'}]

    def test_get_group_not_found(self):
        obj = make_obj(params={**PARAMS, 'group_name': 'missing'})
        obj.iam_api.get_group.return_value = None

        result = obj.get_group('missing', 'ns1')

        assert result == []

    def test_get_group_error(self):
        obj = make_obj(params={**PARAMS, 'group_name': 'devs'})
        obj.iam_api.get_group.side_effect = Exception('IAM error')

        with patch(f'{UTILS}.determine_error', return_value='IAM error'):
            obj.get_group('devs', 'ns1')

        obj.module.fail_json.assert_called_once()
        kwargs = obj.module.fail_json.call_args[1]
        assert 'IAM error' in kwargs['msg']


class TestIamGroupInfoPerform:

    def test_perform_list(self):
        obj = make_obj()
        obj.module.params = PARAMS.copy()
        obj.list_groups = MagicMock(return_value=[{'GroupName': 'devs'}])

        obj.perform_module_operation()

        obj.list_groups.assert_called_once_with('ns1')
        obj.module.exit_json.assert_called_once_with(
            changed=False,
            iam_groups=[{'GroupName': 'devs'}],
        )

    def test_perform_get(self):
        obj = make_obj(params={**PARAMS, 'group_name': 'devs'})
        obj.get_group = MagicMock(return_value=[{'GroupName': 'devs'}])

        obj.perform_module_operation()

        obj.get_group.assert_called_once_with('devs', 'ns1')
        obj.module.exit_json.assert_called_once_with(
            changed=False,
            iam_groups=[{'GroupName': 'devs'}],
        )


class TestIamGroupInfoMain:

    @patch(f'{MODULE}.IamGroupInfo')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group_info import main

        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj

        main()

        mock_obj.perform_module_operation.assert_called_once()
