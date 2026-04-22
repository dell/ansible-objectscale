# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch, Mock

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='notreal',
    validate_certs=False,
    timeout=30,
    namespace='testns',
    user_name='testuser',
    group_name=None,
    role_name=None,
)

SAMPLE_POLICIES = [
    {'PolicyName': 'ECSS3ReadOnlyAccess', 'PolicyArn': 'urn:ecs:iam:::policy/ECSS3ReadOnlyAccess'},
    {'PolicyName': 'IAMReadOnlyAccess', 'PolicyArn': 'urn:ecs:iam:::policy/IAMReadOnlyAccess'},
]


def make_info_obj(params=None, has_client=True):
    """Helper: return an IamPolicyAttachmentInfo instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment_info import IamPolicyAttachmentInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamPolicyAttachmentInfo()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------

class TestInit:
    """Tests for IamPolicyAttachmentInfo.__init__"""

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        """Module initializes correctly with valid params."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment_info import IamPolicyAttachmentInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamPolicyAttachmentInfo()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        """Module fails gracefully when objectscale_client not installed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment_info import IamPolicyAttachmentInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamPolicyAttachmentInfo()
        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_fail(self, mock_am):
        """Module fails gracefully on connection failure."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment_info import IamPolicyAttachmentInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamPolicyAttachmentInfo()
        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# determine_entity tests
# ---------------------------------------------------------------------------

class TestDetermineEntity:
    """Tests for entity type determination."""

    def test_user_entity(self):
        """Determines entity type 'user' when user_name provided."""
        obj = make_info_obj()
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'user'
        assert entity_name == 'testuser'

    def test_group_entity(self):
        """Determines entity type 'group' when group_name provided."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs', 'role_name': None}
        obj = make_info_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'group'
        assert entity_name == 'devs'

    def test_role_entity(self):
        """Determines entity type 'role' when role_name provided."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': None, 'role_name': 'admin-role'}
        obj = make_info_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'role'
        assert entity_name == 'admin-role'

    def test_no_entity(self):
        """Calls fail_json when no entity type specified."""
        params = {**BASE_PARAMS}
        params.pop('user_name', None)
        params.pop('group_name', None)
        params.pop('role_name', None)
        obj = make_info_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == ''
        assert entity_name == ''
        obj.module.fail_json.assert_called_once()
        call_args = obj.module.fail_json.call_args[1]
        assert 'One of user_name, group_name, or role_name is required' in call_args['msg']


# ---------------------------------------------------------------------------
# get_attached_policies tests
# ---------------------------------------------------------------------------

class TestGetAttachedPolicies:
    """Tests for reading attached policies."""

    def test_user_policies(self):
        """Lists attached policies for user entity."""
        obj = make_info_obj()
        obj.iam_api.list_attached_user_policies.return_value = SAMPLE_POLICIES
        result = obj.get_attached_policies('user', 'testuser', 'testns')
        assert result == SAMPLE_POLICIES
        obj.iam_api.list_attached_user_policies.assert_called_once_with('testuser', 'testns')

    def test_group_policies(self):
        """Lists attached policies for group entity."""
        obj = make_info_obj()
        obj.iam_api.list_attached_group_policies.return_value = SAMPLE_POLICIES
        result = obj.get_attached_policies('group', 'devs', 'testns')
        assert result == SAMPLE_POLICIES
        obj.iam_api.list_attached_group_policies.assert_called_once_with('devs', 'testns')

    def test_role_policies(self):
        """Lists attached policies for role entity."""
        obj = make_info_obj()
        obj.iam_api.list_attached_role_policies.return_value = SAMPLE_POLICIES
        result = obj.get_attached_policies('role', 'admin-role', 'testns')
        assert result == SAMPLE_POLICIES
        obj.iam_api.list_attached_role_policies.assert_called_once_with('admin-role', 'testns')

    def test_unknown_entity_type(self):
        """Calls fail_json for unknown entity type."""
        obj = make_info_obj()
        obj.get_attached_policies('unknown', 'test', 'testns')
        obj.module.fail_json.assert_called_once()
        call_args = obj.module.fail_json.call_args[1]
        assert 'Unknown entity type: unknown' in call_args['msg']

    def test_api_exception(self):
        """Calls fail_json on API exception."""
        obj = make_info_obj()
        obj.iam_api.list_attached_user_policies.side_effect = Exception('API Error')
        obj.get_attached_policies('user', 'testuser', 'testns')
        obj.module.fail_json.assert_called_once()
        call_args = obj.module.fail_json.call_args[1]
        assert 'API Error' in call_args['msg']

    def test_empty_result(self):
        """Returns empty list when no policies attached."""
        obj = make_info_obj()
        obj.iam_api.list_attached_user_policies.return_value = []
        result = obj.get_attached_policies('user', 'testuser', 'testns')
        assert result == []


# ---------------------------------------------------------------------------
# perform_module_operation tests
# ---------------------------------------------------------------------------

class TestPerformModuleOperation:
    """Tests for the main module operation."""

    def test_user_with_policies(self):
        """Returns attached policies for user."""
        obj = make_info_obj()
        obj.iam_api.list_attached_user_policies.return_value = SAMPLE_POLICIES
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['entity_type'] == 'user'
        assert kwargs['entity_name'] == 'testuser'
        assert kwargs['iam_attached_policies'] == SAMPLE_POLICIES

    def test_group_with_policies(self):
        """Returns attached policies for group."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs', 'role_name': None}
        obj = make_info_obj(params=params)
        obj.iam_api.list_attached_group_policies.return_value = SAMPLE_POLICIES
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['entity_type'] == 'group'
        assert kwargs['entity_name'] == 'devs'
        assert kwargs['iam_attached_policies'] == SAMPLE_POLICIES

    def test_role_with_policies(self):
        """Returns attached policies for role."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': None, 'role_name': 'admin-role'}
        obj = make_info_obj(params=params)
        obj.iam_api.list_attached_role_policies.return_value = SAMPLE_POLICIES
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['entity_type'] == 'role'
        assert kwargs['entity_name'] == 'admin-role'
        assert kwargs['iam_attached_policies'] == SAMPLE_POLICIES

    def test_empty_policies(self):
        """Returns empty list when no policies attached."""
        obj = make_info_obj()
        obj.iam_api.list_attached_user_policies.return_value = []
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['iam_attached_policies'] == []

    def test_none_policies_returns_empty(self):
        """Returns empty list when API returns None."""
        obj = make_info_obj()
        obj.iam_api.list_attached_user_policies.return_value = None
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['iam_attached_policies'] == []

    def test_always_changed_false(self):
        """Info module always returns changed=False."""
        obj = make_info_obj()
        obj.iam_api.list_attached_user_policies.return_value = SAMPLE_POLICIES
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False


# ---------------------------------------------------------------------------
# main() function test
# ---------------------------------------------------------------------------

class TestMain:
    """Tests for main() function."""

    def test_main_function(self):
        """main() creates instance and calls perform_module_operation."""
        with patch(f'{MODULE}.IamPolicyAttachmentInfo') as mock_class:
            mock_instance = mock_class.return_value
            mock_instance.perform_module_operation = Mock()

            from ansible_collections.dellemc.objectscale.plugins.modules import iam_policy_attachment_info
            iam_policy_attachment_info.main()

            mock_class.assert_called_once()
            mock_instance.perform_module_operation.assert_called_once()
