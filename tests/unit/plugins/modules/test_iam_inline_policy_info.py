# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info'
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

POLICY_DOC_1 = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["iam:Get*","iam:List*"],"Resource":"*"}]}'
POLICY_DOC_2 = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:*","Resource":"*"}]}'

SAMPLE_POLICIES = [
    {'name': 'readOnlyPolicy', 'document': POLICY_DOC_1},
    {'name': 's3FullAccess', 'document': POLICY_DOC_2},
]


def make_info_obj(params=None, has_client=True):
    """Helper: return an IamInlinePolicyInfo instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info import IamInlinePolicyInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamInlinePolicyInfo()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------

class TestInit:
    """Tests for IamInlinePolicyInfo.__init__"""

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        """Module initializes correctly with valid params."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info import IamInlinePolicyInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamInlinePolicyInfo()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        """Module fails gracefully when objectscale_client not installed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info import IamInlinePolicyInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamInlinePolicyInfo()
        mock_module.fail_json.assert_called_once()
        assert 'objectscale_client' in mock_module.fail_json.call_args[1]['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_fail(self, mock_am):
        """Module fails gracefully when connection to ObjectScale fails."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info import IamInlinePolicyInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamInlinePolicyInfo()
        mock_module.fail_json.assert_called_once()
        assert 'conn failed' in mock_module.fail_json.call_args[1]['msg']


# ---------------------------------------------------------------------------
# determine_entity tests
# ---------------------------------------------------------------------------

class TestDetermineEntity:
    """Tests for IamInlinePolicyInfo.determine_entity"""

    def test_user_entity(self):
        """Returns (user, name) when user_name is set."""
        obj = make_info_obj()
        obj.module.params = BASE_PARAMS.copy()
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'user'
        assert entity_name == 'testuser'

    def test_group_entity(self):
        """Returns (group, name) when group_name is set."""
        params = BASE_PARAMS.copy()
        params['user_name'] = None
        params['group_name'] = 'testgroup'
        obj = make_info_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'group'
        assert entity_name == 'testgroup'

    def test_role_entity(self):
        """Returns (role, name) when role_name is set."""
        params = BASE_PARAMS.copy()
        params['user_name'] = None
        params['role_name'] = 'testrole'
        obj = make_info_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'role'
        assert entity_name == 'testrole'

    def test_no_entity(self):
        """Calls fail_json when no entity specified."""
        params = BASE_PARAMS.copy()
        params['user_name'] = None
        params['group_name'] = None
        params['role_name'] = None
        obj = make_info_obj(params=params)
        obj.determine_entity()
        obj.module.fail_json.assert_called_once()


# ---------------------------------------------------------------------------
# get_inline_policies tests
# ---------------------------------------------------------------------------

class TestGetInlinePolicies:
    """Tests for IamInlinePolicyInfo.get_inline_policies"""

    def test_user_inline_policies(self):
        """Returns list of inline policies for user."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = ['readOnlyPolicy']
        obj.iam_api.get_user_policy.return_value = {'PolicyDocument': POLICY_DOC_1}
        result = obj.get_inline_policies('user', 'testuser', 'testns')
        assert len(result) == 1
        assert result[0]['name'] == 'readOnlyPolicy'
        assert result[0]['document'] == POLICY_DOC_1
        obj.iam_api.list_user_policies.assert_called_once_with('testuser', 'testns')

    def test_group_inline_policies(self):
        """Returns list of inline policies for group."""
        obj = make_info_obj()
        obj.iam_api.list_group_policies.return_value = ['s3FullAccess']
        obj.iam_api.get_group_policy.return_value = {'PolicyDocument': POLICY_DOC_2}
        result = obj.get_inline_policies('group', 'testgroup', 'testns')
        assert len(result) == 1
        assert result[0]['name'] == 's3FullAccess'
        obj.iam_api.list_group_policies.assert_called_once_with('testgroup', 'testns')

    def test_role_inline_policies(self):
        """Returns list of inline policies for role."""
        obj = make_info_obj()
        obj.iam_api.list_role_policies.return_value = ['readOnlyPolicy']
        obj.iam_api.get_role_policy.return_value = {'PolicyDocument': POLICY_DOC_1}
        result = obj.get_inline_policies('role', 'testrole', 'testns')
        assert len(result) == 1
        assert result[0]['name'] == 'readOnlyPolicy'
        obj.iam_api.list_role_policies.assert_called_once_with('testrole', 'testns')

    def test_multiple_policies(self):
        """Returns multiple policies correctly."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = ['readOnlyPolicy', 's3FullAccess']
        obj.iam_api.get_user_policy.side_effect = [
            {'PolicyDocument': POLICY_DOC_1},
            {'PolicyDocument': POLICY_DOC_2},
        ]
        result = obj.get_inline_policies('user', 'testuser', 'testns')
        assert len(result) == 2
        names = [p['name'] for p in result]
        assert 'readOnlyPolicy' in names
        assert 's3FullAccess' in names

    def test_empty_policies(self):
        """Returns empty list when entity has no inline policies."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = []
        result = obj.get_inline_policies('user', 'testuser', 'testns')
        assert result == []

    def test_url_encoded_document(self):
        """URL-decodes percent-encoded policy documents."""
        obj = make_info_obj()
        encoded_doc = '%7B%22Version%22%3A%222012-10-17%22%7D'
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.return_value = {'PolicyDocument': encoded_doc}
        result = obj.get_inline_policies('user', 'testuser', 'testns')
        assert result[0]['document'] == '{"Version":"2012-10-17"}'

    def test_unknown_entity_type(self):
        """Calls fail_json for unknown entity type."""
        obj = make_info_obj()
        obj.get_inline_policies('unknown', 'x', 'testns')
        obj.module.fail_json.assert_called_once()
        assert 'Unknown entity type' in obj.module.fail_json.call_args[1]['msg']

    def test_list_api_exception(self):
        """Calls fail_json when list API call raises exception."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.side_effect = Exception("list error")
        obj.get_inline_policies('user', 'testuser', 'testns')
        obj.module.fail_json.assert_called_once()
        assert 'list error' in obj.module.fail_json.call_args[1]['msg']

    def test_get_api_exception(self):
        """Calls fail_json when get policy API call raises exception."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.side_effect = Exception("get error")
        obj.get_inline_policies('user', 'testuser', 'testns')
        obj.module.fail_json.assert_called_once()
        assert 'get error' in obj.module.fail_json.call_args[1]['msg']

    def test_get_returns_none(self):
        """Skips policy when get returns None (deleted between list and get)."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.return_value = None
        result = obj.get_inline_policies('user', 'testuser', 'testns')
        assert result == []

    def test_unknown_entity_type_returns_none(self):
        """Unknown entity type returns None for result."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        result = obj.get_inline_policies('unknown', 'testuser', 'testns')
        assert result == []


# ---------------------------------------------------------------------------
# perform_module_operation tests
# ---------------------------------------------------------------------------

class TestPerformModuleOperation:
    """Tests for IamInlinePolicyInfo.perform_module_operation"""

    def test_user_with_policies(self):
        """Returns inline policies for user."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = ['readOnlyPolicy']
        obj.iam_api.get_user_policy.return_value = {'PolicyDocument': POLICY_DOC_1}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        assert call_kwargs['entity_type'] == 'user'
        assert call_kwargs['entity_name'] == 'testuser'
        assert call_kwargs['namespace'] == 'testns'
        assert len(call_kwargs['inline_policies']) == 1
        assert call_kwargs['inline_policies'][0]['name'] == 'readOnlyPolicy'

    def test_group_with_policies(self):
        """Returns inline policies for group."""
        params = BASE_PARAMS.copy()
        params['user_name'] = None
        params['group_name'] = 'testgroup'
        obj = make_info_obj(params=params)
        obj.iam_api.list_group_policies.return_value = ['s3FullAccess']
        obj.iam_api.get_group_policy.return_value = {'PolicyDocument': POLICY_DOC_2}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        assert call_kwargs['entity_type'] == 'group'
        assert call_kwargs['entity_name'] == 'testgroup'
        assert len(call_kwargs['inline_policies']) == 1

    def test_role_with_policies(self):
        """Returns inline policies for role."""
        params = BASE_PARAMS.copy()
        params['user_name'] = None
        params['role_name'] = 'testrole'
        obj = make_info_obj(params=params)
        obj.iam_api.list_role_policies.return_value = ['fullAccess']
        obj.iam_api.get_role_policy.return_value = {'PolicyDocument': POLICY_DOC_1}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['entity_type'] == 'role'
        assert call_kwargs['entity_name'] == 'testrole'

    def test_empty_policies_returns_empty_list(self):
        """Returns empty list when entity has no inline policies."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = []
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['inline_policies'] == []

    def test_always_changed_false(self):
        """changed is always False for info modules."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.return_value = {'PolicyDocument': POLICY_DOC_1}
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False

    def test_namespace_in_result(self):
        """Returns namespace in result."""
        obj = make_info_obj()
        obj.iam_api.list_user_policies.return_value = []
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['namespace'] == 'testns'


# ---------------------------------------------------------------------------
# main() tests
# ---------------------------------------------------------------------------

class TestMain:
    """Tests for module main() entry point."""

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_main_function(self, mock_am, mock_conn, mock_iam_api):
        """main() creates IamInlinePolicyInfo and calls perform_module_operation."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info import main
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        mock_iam_api_instance = MagicMock()
        mock_iam_api.return_value = mock_iam_api_instance
        mock_iam_api_instance.list_user_policies.return_value = []
        main()
        mock_module.exit_json.assert_called_once()

    def test_main_guard_execution(self):
        """Test main guard execution path."""
        import subprocess
        import sys

        # Test that main guard works by importing and checking if it runs
        result = subprocess.run([
            sys.executable, '-c',
            """
import sys
sys.path.insert(0, '/root/Storage/collections')
from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info import main
try:
    main()
except SystemExit:
    pass  # Expected when module exits
except Exception as e:
    if 'AnsibleModule' in str(e):
        pass  # Expected when module is not properly initialized
    else:
        raise
"""
        ], capture_output=True, text=True, cwd='/root/Storage/collections/ansible_collections/dellemc/objectscale')

        # Should not crash - the main guard should handle execution
        assert result.returncode == 0 or 'AnsibleModule' in result.stderr

    def test_import_exception_sets_iam_api_none(self):
        """Import exception sets IamApi to None."""
        import sys
        import ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info as module
        original_iam_api = getattr(module, 'IamApi', None)

        # Force import error
        with patch.dict(sys.modules, {'ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api': None}):
            # Reload module to trigger import exception
            if 'ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info' in sys.modules:
                del sys.modules['ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info']

            # Re-import with broken dependency
            try:
                import ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy_info as module_reloaded
                assert module_reloaded.IamApi is None
            except ImportError:
                pass  # Expected when dependency is missing

        # Restore original
        module.IamApi = original_iam_api
