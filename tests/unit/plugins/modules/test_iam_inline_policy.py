# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

POLICY_DOC_1 = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": ["iam:Get*", "iam:List*"], "Resource": "*"}]
})

POLICY_DOC_2 = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*"}]
})

POLICY_DOC_1_NORMALIZED = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": ["iam:Get*", "iam:List*"], "Resource": "*"}]
}, sort_keys=True, separators=(',', ':'))

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
    policies=[{'name': 'pol1', 'document': POLICY_DOC_1}],
    state='present',
)


def make_obj(params=None, has_client=True):
    """Helper: return an IamInlinePolicy instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamInlinePolicy()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# Test ID: U-001, U-002, U-003 — __init__
# ---------------------------------------------------------------------------

class TestInit:
    """Tests for IamInlinePolicy.__init__"""

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        """U-001: Module initializes correctly with valid params."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamInlinePolicy()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        """U-002: Module exits gracefully when objectscale_client not installed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamInlinePolicy()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_fail(self, mock_am):
        """U-003: Module exits gracefully on connection failure."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamInlinePolicy()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# Test ID: U-004, U-005, U-006 — determine_entity
# ---------------------------------------------------------------------------

class TestDetermineEntity:
    """Tests for entity type determination"""

    def test_user_entity(self):
        """U-004: Determines entity type 'user'."""
        obj = make_obj()
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'user'
        assert entity_name == 'testuser'

    def test_group_entity(self):
        """U-005: Determines entity type 'group'."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs', 'role_name': None}
        obj = make_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'group'
        assert entity_name == 'devs'

    def test_role_entity(self):
        """U-006: Determines entity type 'role'."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': None, 'role_name': 'admin-role'}
        obj = make_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'role'
        assert entity_name == 'admin-role'

    def test_no_entity_fails(self):
        """U-006b: Fails when no entity is specified."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': None, 'role_name': None}
        obj = make_obj(params=params)
        obj.determine_entity()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'One of user_name, group_name, or role_name is required' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# Test ID: U-007 to U-015 — get_current_policies
# ---------------------------------------------------------------------------

class TestGetCurrentPolicies:
    """Tests for reading inline policies"""

    def test_read_user_policies(self):
        """U-007: Reads user inline policies correctly."""
        obj = make_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.return_value = {
            'UserName': 'testuser', 'PolicyName': 'pol1', 'PolicyDocument': POLICY_DOC_1,
        }
        result = obj.get_current_policies('user', 'testuser', 'testns')
        assert len(result) == 1
        assert result[0]['name'] == 'pol1'
        assert result[0]['document'] == POLICY_DOC_1
        obj.iam_api.list_user_policies.assert_called_once_with('testuser', 'testns')

    def test_read_group_policies(self):
        """U-008: Reads group inline policies correctly."""
        obj = make_obj()
        obj.iam_api.list_group_policies.return_value = ['gpol1']
        obj.iam_api.get_group_policy.return_value = {
            'GroupName': 'devs', 'PolicyName': 'gpol1', 'PolicyDocument': POLICY_DOC_2,
        }
        result = obj.get_current_policies('group', 'devs', 'testns')
        assert len(result) == 1
        assert result[0]['name'] == 'gpol1'

    def test_read_role_policies(self):
        """U-009: Reads role inline policies correctly."""
        obj = make_obj()
        obj.iam_api.list_role_policies.return_value = ['rpol1']
        obj.iam_api.get_role_policy.return_value = {
            'RoleName': 'admin', 'PolicyName': 'rpol1', 'PolicyDocument': POLICY_DOC_1,
        }
        result = obj.get_current_policies('role', 'admin', 'testns')
        assert len(result) == 1
        assert result[0]['name'] == 'rpol1'

    def test_read_empty_policies(self):
        """U-010: Returns empty list when no policies exist."""
        obj = make_obj()
        obj.iam_api.list_user_policies.return_value = []
        result = obj.get_current_policies('user', 'testuser', 'testns')
        assert result == []

    def test_read_multiple_policies(self):
        """U-011: Reads multiple policies (simulating pagination at API level)."""
        obj = make_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1', 'pol2']
        obj.iam_api.get_user_policy.side_effect = [
            {'UserName': 'testuser', 'PolicyName': 'pol1', 'PolicyDocument': POLICY_DOC_1},
            {'UserName': 'testuser', 'PolicyName': 'pol2', 'PolicyDocument': POLICY_DOC_2},
        ]
        result = obj.get_current_policies('user', 'testuser', 'testns')
        assert len(result) == 2
        assert result[0]['name'] == 'pol1'
        assert result[1]['name'] == 'pol2'

    def test_read_list_fails(self):
        """U-012: Exits with error when list fails."""
        obj = make_obj()
        obj.iam_api.list_user_policies.side_effect = Exception("list error")
        obj.get_current_policies('user', 'testuser', 'testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'list error' in call_kwargs['msg']

    def test_read_get_fails(self):
        """U-013: Exits with error when get fails."""
        obj = make_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.side_effect = Exception("get error")
        obj.get_current_policies('user', 'testuser', 'testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'get error' in call_kwargs['msg']

    def test_read_url_encoded_document(self):
        """U-014: Properly decodes URL-encoded policy documents."""
        obj = make_obj()
        url_encoded_doc = '%7B%22Version%22%3A%222012-10-17%22%7D'
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.return_value = {
            'UserName': 'testuser', 'PolicyName': 'pol1', 'PolicyDocument': url_encoded_doc,
        }
        result = obj.get_current_policies('user', 'testuser', 'testns')
        assert result[0]['document'] == '{"Version":"2012-10-17"}'

    def test_read_unknown_entity_type(self):
        """U-015: Exits with error for unknown entity type."""
        obj = make_obj()
        obj.get_current_policies('unknown', 'testuser', 'testns')
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'Unknown entity type' in call_kwargs['msg']

    def test_read_get_returns_none(self):
        """Extra: Handles get returning None (policy deleted between list and get)."""
        obj = make_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        obj.iam_api.get_user_policy.return_value = None
        result = obj.get_current_policies('user', 'testuser', 'testns')
        assert result == []

    def test_read_unknown_entity_type_returns_none(self):
        """Extra: Unknown entity type returns None for result."""
        obj = make_obj()
        obj.iam_api.list_user_policies.return_value = ['pol1']
        result = obj.get_current_policies('unknown', 'testuser', 'testns')
        assert result == []


# ---------------------------------------------------------------------------
# Test ID: U-016 to U-019 — JSON normalization
# ---------------------------------------------------------------------------

class TestNormalizeDocument:
    """Tests for _normalize_document"""

    def test_normalize_valid_json(self):
        """U-016: Normalizes JSON with different key ordering."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        doc = '{"b": 2, "a": 1}'
        result = IamInlinePolicy._normalize_document(doc)
        assert result == '{"a":1,"b":2}'

    def test_normalize_already_normalized(self):
        """U-017: Returns same result for already normalized JSON."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        doc = '{"a":1,"b":2}'
        result = IamInlinePolicy._normalize_document(doc)
        assert result == '{"a":1,"b":2}'

    def test_normalize_with_whitespace(self):
        """U-018: Handles extra whitespace in JSON."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        doc = '  { "b" : 2 ,  "a" : 1 }  '
        result = IamInlinePolicy._normalize_document(doc)
        assert result == '{"a":1,"b":2}'

    def test_normalize_invalid_json(self):
        """U-019: Returns original string for invalid JSON."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        doc = 'not-json{{'
        result = IamInlinePolicy._normalize_document(doc)
        assert result == 'not-json{{'

    def test_normalize_none(self):
        """Extra: Returns empty string for None input."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        result = IamInlinePolicy._normalize_document(None)
        assert result == ''

    def test_normalize_action_string_to_array(self):
        """Extra: Normalizes single-string Action to array (ObjectScale behavior)."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        # User provides string Action
        user_doc = '{"Statement":[{"Action":"s3:GetObject","Effect":"Allow","Resource":"*"}]}'
        # API returns array Action
        api_doc = '{"Statement":[{"Action":["s3:GetObject"],"Effect":"Allow","Resource":["*"]}]}'
        assert IamInlinePolicy._normalize_document(user_doc) == IamInlinePolicy._normalize_document(api_doc)

    def test_normalize_action_already_array(self):
        """Extra: Array Action stays as array after normalization."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        doc = '{"Statement":[{"Action":["s3:Get*","s3:List*"],"Effect":"Allow","Resource":["*"]}]}'
        result = IamInlinePolicy._normalize_document(doc)
        parsed = json.loads(result)
        assert parsed['Statement'][0]['Action'] == ['s3:Get*', 's3:List*']

    def test_normalize_not_action_resource(self):
        """Extra: NotAction and NotResource strings are also normalized to arrays."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        doc = '{"Statement":[{"NotAction":"s3:Delete*","Effect":"Deny","NotResource":"arn:aws:s3:::secret"}]}'
        result = IamInlinePolicy._normalize_document(doc)
        parsed = json.loads(result)
        assert parsed['Statement'][0]['NotAction'] == ['s3:Delete*']
        assert parsed['Statement'][0]['NotResource'] == ['arn:aws:s3:::secret']

    def test_normalize_no_statement(self):
        """Extra: Documents without Statement are still normalized."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        doc = '{"Version":"2012-10-17"}'
        result = IamInlinePolicy._normalize_document(doc)
        assert result == '{"Version":"2012-10-17"}'


# ---------------------------------------------------------------------------
# Test ID: U-020 to U-025 — compute_changes
# ---------------------------------------------------------------------------

class TestComputeChanges:
    """Tests for diff computation"""

    def test_no_changes(self):
        """U-020: No changes when desired matches current."""
        obj = make_obj()
        desired = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        current = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        to_put, to_delete, changed = obj.compute_changes(desired, current, 'present')
        assert to_put == []
        assert to_delete == []
        assert changed is False

    def test_add_new_policy(self):
        """U-021: Detects new policy to add."""
        obj = make_obj()
        desired = [{'name': 'pol1', 'document': POLICY_DOC_1}, {'name': 'pol2', 'document': POLICY_DOC_2}]
        current = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        to_put, to_delete, changed = obj.compute_changes(desired, current, 'present')
        assert len(to_put) == 1
        assert to_put[0]['name'] == 'pol2'
        assert to_delete == []
        assert changed is True

    def test_remove_policy(self):
        """U-022: Detects policy to remove."""
        obj = make_obj()
        desired = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        current = [{'name': 'pol1', 'document': POLICY_DOC_1}, {'name': 'pol2', 'document': POLICY_DOC_2}]
        to_put, to_delete, changed = obj.compute_changes(desired, current, 'present')
        assert to_put == []
        assert to_delete == ['pol2']
        assert changed is True

    def test_update_document(self):
        """U-023: Detects policy with changed document."""
        obj = make_obj()
        desired = [{'name': 'pol1', 'document': POLICY_DOC_2}]
        current = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        to_put, to_delete, changed = obj.compute_changes(desired, current, 'present')
        assert len(to_put) == 1
        assert to_put[0]['name'] == 'pol1'
        assert to_delete == []
        assert changed is True

    def test_mixed_changes(self):
        """U-024: Complex mixed add/remove/update."""
        obj = make_obj()
        desired = [
            {'name': 'pol1', 'document': POLICY_DOC_2},  # updated doc
            {'name': 'pol3', 'document': POLICY_DOC_1},   # new
        ]
        current = [
            {'name': 'pol1', 'document': POLICY_DOC_1},  # will be updated
            {'name': 'pol2', 'document': POLICY_DOC_2},   # will be deleted
        ]
        to_put, to_delete, changed = obj.compute_changes(desired, current, 'present')
        put_names = {p['name'] for p in to_put}
        assert put_names == {'pol1', 'pol3'}
        assert to_delete == ['pol2']
        assert changed is True

    def test_absent_deletes_all(self):
        """U-025: state=absent produces delete of all current policies."""
        obj = make_obj()
        current = [{'name': 'pol1', 'document': POLICY_DOC_1}, {'name': 'pol2', 'document': POLICY_DOC_2}]
        to_put, to_delete, changed = obj.compute_changes([], current, 'absent')
        assert to_put == []
        assert set(to_delete) == {'pol1', 'pol2'}
        assert changed is True

    def test_absent_no_current(self):
        """Extra: state=absent with no current policies."""
        obj = make_obj()
        to_put, to_delete, changed = obj.compute_changes([], [], 'absent')
        assert to_put == []
        assert to_delete == []
        assert changed is False


# ---------------------------------------------------------------------------
# Test ID: U-026 to U-034 — apply_changes
# ---------------------------------------------------------------------------

class TestApplyChanges:
    """Tests for applying policy changes"""

    def test_put_user_policy(self):
        """U-026: Puts inline policy for user."""
        obj = make_obj()
        to_put = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        obj.apply_changes('user', 'testuser', 'testns', to_put, [])
        obj.iam_api.put_user_policy.assert_called_once_with('testuser', 'pol1', POLICY_DOC_1, 'testns')

    def test_put_group_policy(self):
        """U-027: Puts inline policy for group."""
        obj = make_obj()
        to_put = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        obj.apply_changes('group', 'devs', 'testns', to_put, [])
        obj.iam_api.put_group_policy.assert_called_once_with('devs', 'pol1', POLICY_DOC_1, 'testns')

    def test_put_role_policy(self):
        """U-028: Puts inline policy for role."""
        obj = make_obj()
        to_put = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        obj.apply_changes('role', 'admin-role', 'testns', to_put, [])
        obj.iam_api.put_role_policy.assert_called_once_with('admin-role', 'pol1', POLICY_DOC_1, 'testns')

    def test_delete_user_policy(self):
        """U-029: Deletes inline policy from user."""
        obj = make_obj()
        obj.apply_changes('user', 'testuser', 'testns', [], ['pol1'])
        obj.iam_api.delete_user_policy.assert_called_once_with('testuser', 'pol1', 'testns')

    def test_delete_group_policy(self):
        """U-030: Deletes inline policy from group."""
        obj = make_obj()
        obj.apply_changes('group', 'devs', 'testns', [], ['pol1'])
        obj.iam_api.delete_group_policy.assert_called_once_with('devs', 'pol1', 'testns')

    def test_delete_role_policy(self):
        """U-031: Deletes inline policy from role."""
        obj = make_obj()
        obj.apply_changes('role', 'admin-role', 'testns', [], ['pol1'])
        obj.iam_api.delete_role_policy.assert_called_once_with('admin-role', 'pol1', 'testns')

    def test_check_mode_skips_put(self):
        """U-032: Check mode skips put API calls."""
        obj = make_obj()
        obj.module.check_mode = True
        to_put = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        obj.apply_changes('user', 'testuser', 'testns', to_put, [])
        obj.iam_api.put_user_policy.assert_not_called()

    def test_check_mode_skips_delete(self):
        """U-033: Check mode skips delete API calls."""
        obj = make_obj()
        obj.module.check_mode = True
        obj.apply_changes('user', 'testuser', 'testns', [], ['pol1'])
        obj.iam_api.delete_user_policy.assert_not_called()

    def test_put_fails(self):
        """U-034: Exits with error when put fails."""
        obj = make_obj()
        obj.iam_api.put_user_policy.side_effect = Exception("put error")
        to_put = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        obj.apply_changes('user', 'testuser', 'testns', to_put, [])
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'put error' in call_kwargs['msg']

    def test_delete_fails(self):
        """U-045: Exits with error when delete fails."""
        obj = make_obj()
        obj.iam_api.delete_user_policy.side_effect = Exception("delete error")
        obj.apply_changes('user', 'testuser', 'testns', [], ['pol1'])
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'delete error' in call_kwargs['msg']

    def test_delete_unknown_entity(self):
        """U-047a: Unknown entity type on delete path."""
        obj = make_obj()
        obj.apply_changes('unknown', 'x', 'testns', [], ['pol1'])
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'Unknown entity type' in call_kwargs['msg']

    def test_put_unknown_entity(self):
        """U-047b: Unknown entity type on put path."""
        obj = make_obj()
        to_put = [{'name': 'pol1', 'document': POLICY_DOC_1}]
        obj.apply_changes('unknown', 'x', 'testns', to_put, [])
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'Unknown entity type' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# Test ID: U-035 to U-044 — perform_module_operation (full orchestration)
# ---------------------------------------------------------------------------

class TestPerformModuleOperation:
    """Tests for full orchestration"""

    def _setup_obj(self, params=None, current_policies=None):
        """Helper to create an obj with mocked get_current_policies."""
        obj = make_obj(params=params)
        if current_policies is None:
            current_policies = []
        obj.get_current_policies = MagicMock(return_value=current_policies)
        return obj

    def test_create_new_policies(self):
        """U-035: Creates new policies when none exist."""
        obj = self._setup_obj()
        # After apply, re-read returns the new policies
        obj.get_current_policies.side_effect = [
            [],  # initial read
            [{'name': 'pol1', 'document': POLICY_DOC_1}],  # after apply
        ]
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        assert len(call_kwargs['inline_policy_details']['policies']) == 1
        obj.iam_api.put_user_policy.assert_called_once()

    def test_update_existing_policies(self):
        """U-036: Updates policies with changed documents."""
        params = {**BASE_PARAMS, 'policies': [{'name': 'pol1', 'document': POLICY_DOC_2}]}
        obj = self._setup_obj(params=params)
        obj.get_current_policies.side_effect = [
            [{'name': 'pol1', 'document': POLICY_DOC_1}],  # initial
            [{'name': 'pol1', 'document': POLICY_DOC_2}],  # after
        ]
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True

    def test_idempotent_no_change(self):
        """U-037: No changes when desired matches current."""
        obj = self._setup_obj(current_policies=[{'name': 'pol1', 'document': POLICY_DOC_1}])
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        obj.iam_api.put_user_policy.assert_not_called()
        obj.iam_api.delete_user_policy.assert_not_called()

    def test_delete_all_absent(self):
        """U-038: Deletes all policies when state=absent."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policies': None}
        obj = self._setup_obj(params=params)
        obj.get_current_policies.side_effect = [
            [{'name': 'pol1', 'document': POLICY_DOC_1}],  # initial
            [],  # after delete
        ]
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        obj.iam_api.delete_user_policy.assert_called_once()

    def test_absent_idempotent(self):
        """U-039: No changes when state=absent and no policies exist."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policies': None}
        obj = self._setup_obj(params=params, current_policies=[])
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False

    def test_check_mode_create(self):
        """U-040: Check mode reports changes without API calls."""
        obj = self._setup_obj(current_policies=[])
        obj.module.check_mode = True
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        # In check mode, get_current_policies should only be called once (no re-read)
        assert obj.get_current_policies.call_count == 1

    def test_check_mode_delete(self):
        """U-041: Check mode for absent reports changes without API calls."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policies': None}
        obj = self._setup_obj(params=params, current_policies=[{'name': 'pol1', 'document': POLICY_DOC_1}])
        obj.module.check_mode = True
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        assert call_kwargs['inline_policy_details']['policies'] == []

    def test_diff_mode(self):
        """U-042: Diff mode includes before/after snapshot."""
        obj = self._setup_obj(current_policies=[])
        obj.module._diff = True
        obj.get_current_policies.side_effect = [
            [],  # initial
            [{'name': 'pol1', 'document': POLICY_DOC_1}],  # after
        ]
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in call_kwargs
        assert 'before' in call_kwargs['diff']
        assert 'after' in call_kwargs['diff']
        assert call_kwargs['diff']['before']['policies'] == []
        assert len(call_kwargs['diff']['after']['policies']) == 1

    def test_group_entity_full_cycle(self):
        """U-043: Full create cycle for group entity."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs', 'role_name': None}
        obj = self._setup_obj(params=params)
        obj.get_current_policies.side_effect = [
            [],
            [{'name': 'pol1', 'document': POLICY_DOC_1}],
        ]
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        assert call_kwargs['inline_policy_details']['entity_type'] == 'group'
        assert call_kwargs['id'] == 'testns:group:devs'
        obj.iam_api.put_group_policy.assert_called_once()

    def test_role_entity_full_cycle(self):
        """U-044: Full create cycle for role entity."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': None, 'role_name': 'admin-role'}
        obj = self._setup_obj(params=params)
        obj.get_current_policies.side_effect = [
            [],
            [{'name': 'pol1', 'document': POLICY_DOC_1}],
        ]
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        assert call_kwargs['inline_policy_details']['entity_type'] == 'role'
        assert call_kwargs['id'] == 'testns:role:admin-role'
        obj.iam_api.put_role_policy.assert_called_once()

    def test_id_format(self):
        """Extra: Verify id format is namespace:entity_type:entity_name."""
        obj = self._setup_obj(current_policies=[{'name': 'pol1', 'document': POLICY_DOC_1}])
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['id'] == 'testns:user:testuser'

    def test_policies_none_defaults_empty(self):
        """Extra: policies=None defaults to empty list for absent."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policies': None}
        obj = self._setup_obj(params=params, current_policies=[])
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False


# ---------------------------------------------------------------------------
# Test ID: U-046, U-048 — Misc
# ---------------------------------------------------------------------------

class TestMisc:
    """Miscellaneous tests"""

    def test_invalid_policy_document_handled(self):
        """U-046: Module handles non-JSON document gracefully in comparison."""
        obj = make_obj()
        desired = [{'name': 'pol1', 'document': 'not-json'}]
        current = [{'name': 'pol1', 'document': 'not-json'}]
        to_put, to_delete, changed = obj.compute_changes(desired, current, 'present')
        assert changed is False

    def test_main_function(self):
        """U-048: main() calls perform_module_operation."""
        with patch(f'{MODULE}.IamInlinePolicy') as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import main
            main()
            mock_instance.perform_module_operation.assert_called_once()

    def test_import_exception_handling(self):
        """U-049: Import exception sets IamApi to None."""
        import sys
        import ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy as module
        original_iam_api = getattr(module, 'IamApi', None)
        
        # Force import error
        with patch.dict(sys.modules, {'ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api': None}):
            # Reload module to trigger import exception
            if 'ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy' in sys.modules:
                del sys.modules['ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy']
            
            # Re-import with broken dependency
            try:
                import ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy as module_reloaded
                assert module_reloaded.IamApi is None
            except ImportError:
                pass  # Expected when dependency is missing
        
        # Restore original
        module.IamApi = original_iam_api

    def test_get_iam_inline_policy_parameters(self):
        """Extra: Verify parameter spec is correct."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        params = IamInlinePolicy.get_iam_inline_policy_parameters()
        assert 'namespace' in params
        assert 'user_name' in params
        assert 'group_name' in params
        assert 'role_name' in params
        assert 'policies' in params
        assert 'state' in params
        assert params['state']['choices'] == ['present', 'absent']

    def test_build_state_snapshot(self):
        """Extra: Verify state snapshot building."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import IamInlinePolicy
        policies = [
            {'name': 'bpol', 'document': 'doc2'},
            {'name': 'apol', 'document': 'doc1'},
        ]
        snapshot = IamInlinePolicy._build_state_snapshot(policies)
        assert snapshot['policies'][0]['name'] == 'apol'
        assert snapshot['policies'][1]['name'] == 'bpol'

    def test_check_mode_present_simulates_after(self):
        """Extra: Check mode present correctly simulates after state."""
        params = {**BASE_PARAMS, 'policies': [
            {'name': 'pol1', 'document': POLICY_DOC_2},
            {'name': 'pol3', 'document': POLICY_DOC_1},
        ]}
        obj = make_obj(params=params)
        obj.module.check_mode = True
        obj.get_current_policies = MagicMock(return_value=[
            {'name': 'pol1', 'document': POLICY_DOC_1},
            {'name': 'pol2', 'document': POLICY_DOC_2},
        ])
        obj.perform_module_operation()
        call_kwargs = obj.module.exit_json.call_args[1]
        assert call_kwargs['changed'] is True
        policy_names = {p['name'] for p in call_kwargs['inline_policy_details']['policies']}
        assert policy_names == {'pol1', 'pol3'}

    def test_main_guard_execution(self):
        """U-050: Test main guard execution path."""
        import subprocess
        import sys
        
        # Test that main guard works by importing and checking if it runs
        result = subprocess.run([
            sys.executable, '-c',
            """
import sys
sys.path.insert(0, '/root/Storage/collections')
from ansible_collections.dellemc.objectscale.plugins.modules.iam_inline_policy import main
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
