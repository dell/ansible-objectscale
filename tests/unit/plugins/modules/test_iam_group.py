# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_group'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    group_name='developers',
    namespace='testns',
    path='/',
    users=None,
    user_state='present-in-group',
    policies=None,
    policy_state='present-in-group',
    inline_policies=None,
    inline_policy_state='present-in-group',
    state='present',
)

SAMPLE_GROUP_DETAILS = {
    'group_name': 'developers',
    'group_id': 'AGPA123',
    'arn': 'urn:ecs:iam::testns:group/developers',
    'path': '/',
    'create_date': '2024-01-15T10:30:00Z',
    'users': ['alice'],
    'attached_policies': [{'PolicyName': 'ReadOnly', 'PolicyArn': 'urn:ecs:iam:::policy/ReadOnly'}],
    'inline_policies': ['InlinePolicy1'],
}


def make_iam_group_obj(params=None, has_client=True):
    """Helper: return an IamGroup instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_group import IamGroup

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamGroup()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestIamGroupInit:

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group import IamGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamGroup()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group import IamGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamGroup()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group import IamGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamGroup()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# get_group_details
# ---------------------------------------------------------------------------

class TestGetGroupDetails:

    def test_success(self):
        obj = make_iam_group_obj()
        obj.iam_api.get_group.return_value = {
            'GroupName': 'developers', 'GroupId': 'AGPA123',
            'Arn': 'urn:ecs:iam::testns:group/developers', 'Path': '/',
            'CreateDate': '2024-01-15T10:30:00Z',
            'Users': [{'UserName': 'alice', 'UserId': 'AIDA111', 'Arn': 'urn:user/alice'}],
        }
        obj.iam_api.list_attached_group_policies.return_value = [
            {'PolicyName': 'ReadOnly', 'PolicyArn': 'urn:ecs:iam:::policy/ReadOnly'},
        ]
        obj.iam_api.list_group_policies.return_value = ['InlinePolicy1']

        result = obj.get_group_details('developers', 'testns')

        assert result is not None
        assert result['group_name'] == 'developers'
        assert result['users'] == ['alice']
        assert len(result['attached_policies']) == 1
        assert result['inline_policies'] == ['InlinePolicy1']

    def test_not_found(self):
        obj = make_iam_group_obj()
        obj.iam_api.get_group.return_value = None

        result = obj.get_group_details('nonexistent', 'testns')
        assert result is None

    def test_api_error(self):
        obj = make_iam_group_obj()
        err = Exception("server error")
        err.status = 500
        obj.iam_api.get_group.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_group_details('developers', 'testns')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'developers' in kwargs['msg']


# ---------------------------------------------------------------------------
# create_group
# ---------------------------------------------------------------------------

class TestCreateGroup:

    def test_success(self):
        obj = make_iam_group_obj()
        result = obj.create_group('developers', 'testns')
        assert result is True
        obj.iam_api.create_group.assert_called_once()

    def test_api_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.create_group.side_effect = Exception("create err")

        with patch(f'{UTILS}.determine_error', return_value='create err'):
            obj.create_group('developers', 'testns')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# delete_group
# ---------------------------------------------------------------------------

class TestDeleteGroup:

    def test_success_with_cleanup(self):
        obj = make_iam_group_obj()
        result = obj.delete_group('developers', 'testns', SAMPLE_GROUP_DETAILS)
        assert result is True
        obj.iam_api.remove_user_from_group.assert_called_once()
        obj.iam_api.detach_group_policy.assert_called_once()
        obj.iam_api.delete_group_policy.assert_called_once()
        obj.iam_api.delete_group.assert_called_once()

    def test_delete_api_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.delete_group.side_effect = Exception("del err")
        current = {'users': [], 'attached_policies': [], 'inline_policies': []}

        with patch(f'{UTILS}.determine_error', return_value='del err'):
            obj.delete_group('developers', 'testns', current)

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# is_group_modified
# ---------------------------------------------------------------------------

class TestIsGroupModified:

    def test_users_to_add(self):
        params = {**BASE_PARAMS, 'users': ['alice', 'bob'], 'user_state': 'present-in-group'}
        obj = make_iam_group_obj(params=params)
        current = {**SAMPLE_GROUP_DETAILS, 'users': ['alice']}
        result = obj.is_group_modified(current)
        assert 'bob' in result['users_to_add']
        assert result['is_modified'] is True

    def test_users_to_remove(self):
        params = {**BASE_PARAMS, 'users': ['alice'], 'user_state': 'absent-in-group'}
        obj = make_iam_group_obj(params=params)
        current = {**SAMPLE_GROUP_DETAILS, 'users': ['alice', 'bob']}
        result = obj.is_group_modified(current)
        assert 'alice' in result['users_to_remove']
        assert result['is_modified'] is True

    def test_policies_to_attach(self):
        params = {**BASE_PARAMS, 'policies': ['urn:new-policy'], 'policy_state': 'present-in-group'}
        obj = make_iam_group_obj(params=params)
        current = {**SAMPLE_GROUP_DETAILS}
        result = obj.is_group_modified(current)
        assert 'urn:new-policy' in result['policies_to_attach']

    def test_no_changes(self):
        obj = make_iam_group_obj()
        current = {**SAMPLE_GROUP_DETAILS}
        result = obj.is_group_modified(current)
        assert result['is_modified'] is False


# ---------------------------------------------------------------------------
# check_mode
# ---------------------------------------------------------------------------

class TestCheckMode:

    def test_check_mode_create(self):
        obj = make_iam_group_obj()
        obj.module.check_mode = True
        obj.get_group_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.create_group.assert_not_called()

    def test_check_mode_delete(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = make_iam_group_obj(params=params)
        obj.module.check_mode = True
        obj.get_group_details = MagicMock(return_value=SAMPLE_GROUP_DETAILS.copy())

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.delete_group.assert_not_called()

    def test_check_mode_no_change(self):
        obj = make_iam_group_obj()
        obj.module.check_mode = True
        obj.get_group_details = MagicMock(return_value=SAMPLE_GROUP_DETAILS.copy())

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False


# ---------------------------------------------------------------------------
# diff_mode
# ---------------------------------------------------------------------------

class TestDiffMode:

    def test_diff_on_create(self):
        obj = make_iam_group_obj()
        obj.module._diff = True
        obj.get_group_details = MagicMock(side_effect=[None, SAMPLE_GROUP_DETAILS.copy()])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in kwargs
        assert kwargs['diff']['before'] == {}

    def test_diff_on_delete(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = make_iam_group_obj(params=params)
        obj.module._diff = True
        obj.get_group_details = MagicMock(return_value=SAMPLE_GROUP_DETAILS.copy())

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in kwargs
        assert kwargs['diff']['after'] == {}


# ---------------------------------------------------------------------------
# perform_module_operation
# ---------------------------------------------------------------------------

class TestPerformModuleOperation:

    def _make(self, params):
        obj = make_iam_group_obj(params=params)
        obj.get_group_details = MagicMock()
        obj.create_group = MagicMock(return_value=True)
        obj.delete_group = MagicMock(return_value=True)
        obj.add_users = MagicMock()
        obj.remove_users = MagicMock()
        obj.attach_policies = MagicMock()
        obj.detach_policies = MagicMock()
        obj.put_inline_policies = MagicMock()
        obj.delete_inline_policies = MagicMock()
        obj.is_group_modified = MagicMock(return_value={
            'users_to_add': [], 'users_to_remove': [],
            'policies_to_attach': [], 'policies_to_detach': [],
            'inline_to_put': [], 'inline_to_delete': [],
            'is_modified': False,
        })
        return obj

    def test_state_present_creates(self):
        obj = self._make(BASE_PARAMS.copy())
        obj.get_group_details.side_effect = [None, SAMPLE_GROUP_DETAILS.copy()]

        obj.perform_module_operation()

        obj.create_group.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_state_present_no_change(self):
        obj = self._make(BASE_PARAMS.copy())
        obj.get_group_details.return_value = SAMPLE_GROUP_DETAILS.copy()

        obj.perform_module_operation()

        obj.create_group.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_state_present_modifies(self):
        params = {**BASE_PARAMS, 'users': ['alice', 'bob']}
        obj = self._make(params)
        obj.get_group_details.side_effect = [SAMPLE_GROUP_DETAILS.copy(), SAMPLE_GROUP_DETAILS.copy()]
        obj.is_group_modified.return_value = {
            'users_to_add': ['bob'], 'users_to_remove': [],
            'policies_to_attach': [], 'policies_to_detach': [],
            'inline_to_put': [], 'inline_to_delete': [],
            'is_modified': True,
        }

        obj.perform_module_operation()

        obj.add_users.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_state_absent_deletes(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_group_details.return_value = SAMPLE_GROUP_DETAILS.copy()

        obj.perform_module_operation()

        obj.delete_group.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_state_absent_noop(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_group_details.return_value = None

        obj.perform_module_operation()

        obj.delete_group.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_get_iam_group_parameters(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_group import IamGroup
        params = IamGroup.get_iam_group_parameters()
        assert 'group_name' in params
        assert 'namespace' in params
        assert 'state' in params
        assert 'users' in params
        assert 'policies' in params
        assert 'inline_policies' in params


# ---------------------------------------------------------------------------
# Direct write operation tests
# ---------------------------------------------------------------------------

class TestWriteOperations:

    def test_add_users_calls_api(self):
        obj = make_iam_group_obj()
        obj.add_users('developers', 'testns', ['alice', 'bob'])
        assert obj.iam_api.add_user_to_group.call_count == 2

    def test_add_users_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.add_user_to_group.side_effect = Exception("add err")
        with patch(f'{UTILS}.determine_error', return_value='add err'):
            obj.add_users('developers', 'testns', ['alice'])
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_remove_users_calls_api(self):
        obj = make_iam_group_obj()
        obj.remove_users('developers', 'testns', ['alice'])
        obj.iam_api.remove_user_from_group.assert_called_once()

    def test_remove_users_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.remove_user_from_group.side_effect = Exception("rm err")
        with patch(f'{UTILS}.determine_error', return_value='rm err'):
            obj.remove_users('developers', 'testns', ['alice'])
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_attach_policies_calls_api(self):
        obj = make_iam_group_obj()
        obj.attach_policies('developers', 'testns', ['urn:pol1', 'urn:pol2'])
        assert obj.iam_api.attach_group_policy.call_count == 2

    def test_attach_policies_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.attach_group_policy.side_effect = Exception("att err")
        with patch(f'{UTILS}.determine_error', return_value='att err'):
            obj.attach_policies('developers', 'testns', ['urn:pol1'])
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_detach_policies_calls_api(self):
        obj = make_iam_group_obj()
        obj.detach_policies('developers', 'testns', ['urn:pol1'])
        obj.iam_api.detach_group_policy.assert_called_once()

    def test_detach_policies_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.detach_group_policy.side_effect = Exception("det err")
        with patch(f'{UTILS}.determine_error', return_value='det err'):
            obj.detach_policies('developers', 'testns', ['urn:pol1'])
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_put_inline_policies_calls_api(self):
        obj = make_iam_group_obj()
        obj.put_inline_policies('developers', 'testns', [{'name': 'pol1', 'document': '{}'}])
        obj.iam_api.put_group_policy.assert_called_once()

    def test_put_inline_policies_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.put_group_policy.side_effect = Exception("put err")
        with patch(f'{UTILS}.determine_error', return_value='put err'):
            obj.put_inline_policies('developers', 'testns', [{'name': 'pol1', 'document': '{}'}])
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_delete_inline_policies_calls_api(self):
        obj = make_iam_group_obj()
        obj.delete_inline_policies('developers', 'testns', ['pol1', 'pol2'])
        assert obj.iam_api.delete_group_policy.call_count == 2

    def test_delete_inline_policies_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.delete_group_policy.side_effect = Exception("del err")
        with patch(f'{UTILS}.determine_error', return_value='del err'):
            obj.delete_inline_policies('developers', 'testns', ['pol1'])
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_get_group_details_policy_exception(self):
        obj = make_iam_group_obj()
        obj.iam_api.get_group.return_value = {
            'GroupName': 'dev', 'GroupId': 'G1', 'Arn': 'a', 'Path': '/', 'CreateDate': 't',
            'Users': [],
        }
        obj.iam_api.list_attached_group_policies.side_effect = Exception("err")
        obj.iam_api.list_group_policies.side_effect = Exception("err")
        result = obj.get_group_details('dev', 'ns')
        assert result is not None
        assert result['attached_policies'] == []
        assert result['inline_policies'] == []

    def test_get_group_details_404_exception(self):
        obj = make_iam_group_obj()
        err = Exception("not found")
        err.status = 404
        obj.iam_api.get_group.side_effect = err
        result = obj.get_group_details('dev', 'ns')
        assert result is None

    def test_delete_group_cleanup_user_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.remove_user_from_group.side_effect = Exception("rm err")
        current = {'users': ['alice'], 'attached_policies': [], 'inline_policies': []}
        with patch(f'{UTILS}.determine_error', return_value='rm err'):
            obj.delete_group('dev', 'ns', current)
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_delete_group_cleanup_detach_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.detach_group_policy.side_effect = Exception("det err")
        current = {'users': [], 'attached_policies': [{'PolicyArn': 'urn:p'}], 'inline_policies': []}
        with patch(f'{UTILS}.determine_error', return_value='det err'):
            obj.delete_group('dev', 'ns', current)
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_delete_group_cleanup_inline_error(self):
        obj = make_iam_group_obj()
        obj.iam_api.delete_group_policy.side_effect = Exception("del err")
        current = {'users': [], 'attached_policies': [], 'inline_policies': ['ip1']}
        with patch(f'{UTILS}.determine_error', return_value='del err'):
            obj.delete_group('dev', 'ns', current)
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


class TestPerformWithModifications:

    def test_create_with_all_options(self):
        params = {**BASE_PARAMS, 'users': ['alice'], 'policies': ['urn:pol1'],
                  'inline_policies': [{'name': 'ip1', 'document': '{}'}]}
        obj = make_iam_group_obj(params=params)
        obj.get_group_details = MagicMock(side_effect=[None, SAMPLE_GROUP_DETAILS.copy()])
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.create_group.assert_called_once()
        obj.iam_api.add_user_to_group.assert_called_once()
        obj.iam_api.attach_group_policy.assert_called_once()
        obj.iam_api.put_group_policy.assert_called_once()

    def test_modify_with_removals(self):
        params = {**BASE_PARAMS, 'users': ['alice'], 'user_state': 'absent-in-group',
                  'policies': ['urn:ecs:iam:::policy/ReadOnly'], 'policy_state': 'absent-in-group',
                  'inline_policies': [{'name': 'InlinePolicy1'}], 'inline_policy_state': 'absent-in-group'}
        obj = make_iam_group_obj(params=params)
        obj.get_group_details = MagicMock(side_effect=[
            SAMPLE_GROUP_DETAILS.copy(), SAMPLE_GROUP_DETAILS.copy()])
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_main_function(self):
        with patch(f'{MODULE}.IamGroup') as mock_cls:
            from ansible_collections.dellemc.objectscale.plugins.modules.iam_group import main
            mock_obj = MagicMock()
            mock_cls.return_value = mock_obj
            main()
            mock_obj.perform_module_operation.assert_called_once()
