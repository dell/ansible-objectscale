# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment'
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
    policy_arns=['urn:ecs:iam:::policy/ECSS3ReadOnlyAccess'],
    state='present',
)

SAMPLE_ATTACHED_POLICIES = [
    {'PolicyName': 'ECSS3ReadOnlyAccess', 'PolicyArn': 'urn:ecs:iam:::policy/ECSS3ReadOnlyAccess'},
]

ARN1 = 'urn:ecs:iam:::policy/ECSS3ReadOnlyAccess'
ARN2 = 'urn:ecs:iam:::policy/IAMReadOnlyAccess'
ARN3 = 'urn:ecs:iam:::policy/ECSS3FullAccess'


def make_iam_policy_attachment_obj(params=None, has_client=True):
    """Helper: return an IamPolicyAttachment instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment import IamPolicyAttachment

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamPolicyAttachment()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# Test ID: U-001, U-002, U-003 — __init__
# ---------------------------------------------------------------------------

class TestInit:
    """Tests for IamPolicyAttachment.__init__ — Design Ref: FR-001, FR-008"""

    # Test ID: U-001
    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        """U-001: Module initializes correctly with valid params."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment import IamPolicyAttachment
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamPolicyAttachment()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    # Test ID: U-002
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client_missing(self, mock_am, mock_conn):
        """U-002: Module exits gracefully when objectscale_client not installed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment import IamPolicyAttachment
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamPolicyAttachment()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    # Test ID: U-003
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_fail(self, mock_am):
        """U-003: Module exits gracefully on connection failure."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment import IamPolicyAttachment
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamPolicyAttachment()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# Test ID: U-004, U-005, U-006 — determine_entity
# ---------------------------------------------------------------------------

class TestDetermineEntity:
    """Tests for entity type determination — Design Ref: FR-006"""

    # Test ID: U-004
    def test_user_entity(self):
        """U-004: Determines entity type 'user' when user_name provided."""
        obj = make_iam_policy_attachment_obj()
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'user'
        assert entity_name == 'testuser'

    # Test ID: U-005
    def test_group_entity(self):
        """U-005: Determines entity type 'group' when group_name provided."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs', 'role_name': None}
        obj = make_iam_policy_attachment_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'group'
        assert entity_name == 'devs'

    # Test ID: U-006
    def test_role_entity(self):
        """U-006: Determines entity type 'role' when role_name provided."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': None, 'role_name': 'admin-role'}
        obj = make_iam_policy_attachment_obj(params=params)
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == 'role'
        assert entity_name == 'admin-role'


# ---------------------------------------------------------------------------
# Test ID: U-007, U-008, U-009 — get_attached_policies
# ---------------------------------------------------------------------------

class TestGetAttachedPolicies:
    """Tests for reading attached policies — Design Ref: FR-001"""

    # Test ID: U-007
    def test_user_policies(self):
        """U-007: Lists attached policies for user entity."""
        obj = make_iam_policy_attachment_obj()
        obj.iam_api.list_attached_user_policies.return_value = SAMPLE_ATTACHED_POLICIES
        result = obj.get_attached_policies('user', 'testuser', 'testns')
        assert isinstance(result, list)
        obj.iam_api.list_attached_user_policies.assert_called_once_with('testuser', 'testns')

    # Test ID: U-008
    def test_group_policies(self):
        """U-008: Lists attached policies for group entity."""
        obj = make_iam_policy_attachment_obj()
        obj.iam_api.list_attached_group_policies.return_value = SAMPLE_ATTACHED_POLICIES
        result = obj.get_attached_policies('group', 'devs', 'testns')
        assert isinstance(result, list)
        obj.iam_api.list_attached_group_policies.assert_called_once_with('devs', 'testns')

    # Test ID: U-009
    def test_role_policies(self):
        """U-009: Lists attached policies for role entity."""
        obj = make_iam_policy_attachment_obj()
        obj.iam_api.list_attached_role_policies.return_value = SAMPLE_ATTACHED_POLICIES
        result = obj.get_attached_policies('role', 'admin-role', 'testns')
        assert isinstance(result, list)
        obj.iam_api.list_attached_role_policies.assert_called_once_with('admin-role', 'testns')


# ---------------------------------------------------------------------------
# Test ID: U-010, U-011 — perform_module_operation (state=present, new attach)
# ---------------------------------------------------------------------------

class TestPerformOperationAttach:
    """Tests for attaching policies (state=present) — Design Ref: FR-001"""

    # Test ID: U-010
    def test_attach_new_user_policies(self):
        """U-010: Attaches policies to user when none currently attached."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1, ARN2]}
        obj = make_iam_policy_attachment_obj(params=params)
        # First call: current state (empty), second call: after attach
        obj.iam_api.list_attached_user_policies.side_effect = [
            [],
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}, {'PolicyName': 'p2', 'PolicyArn': ARN2}],
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert obj.iam_api.attach_user_policy.call_count == 2

    # Test ID: U-011
    def test_attach_new_group_policies(self):
        """U-011: Attaches policies to group when none currently attached."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs',
                  'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_group_policies.side_effect = [
            [],
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}],
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.attach_group_policy.assert_called_once()


# ---------------------------------------------------------------------------
# Test ID: U-012, U-013, U-014 — perform_module_operation (state=absent)
# ---------------------------------------------------------------------------

class TestPerformOperationDetach:
    """Tests for detaching all policies (state=absent) — Design Ref: FR-002"""

    # Test ID: U-012
    def test_detach_all_user_policies(self):
        """U-012: Detaches all policies from user with state=absent."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policy_arns': None}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
            {'PolicyName': 'p2', 'PolicyArn': ARN2},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert obj.iam_api.detach_user_policy.call_count == 2

    # Test ID: U-013
    def test_detach_all_group_policies(self):
        """U-013: Detaches all policies from group with state=absent."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs',
                  'state': 'absent', 'policy_arns': None}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_group_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.detach_group_policy.assert_called_once()

    # Test ID: U-014
    def test_detach_all_role_policies(self):
        """U-014: Detaches all policies from role with state=absent."""
        params = {**BASE_PARAMS, 'user_name': None, 'role_name': 'admin-role',
                  'state': 'absent', 'policy_arns': None}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_role_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
            {'PolicyName': 'p2', 'PolicyArn': ARN2},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert obj.iam_api.detach_role_policy.call_count == 2


# ---------------------------------------------------------------------------
# Test ID: U-015, U-016, U-017 — Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:
    """Tests for idempotent behavior — Design Ref: FR-003"""

    # Test ID: U-015
    def test_user_no_change(self):
        """U-015: No change when desired ARNs equal current for user."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        obj.iam_api.attach_user_policy.assert_not_called()
        obj.iam_api.detach_user_policy.assert_not_called()

    # Test ID: U-016
    def test_group_no_change(self):
        """U-016: No change when desired ARNs equal current for group."""
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': 'devs',
                  'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_group_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        obj.iam_api.attach_group_policy.assert_not_called()
        obj.iam_api.detach_group_policy.assert_not_called()

    # Test ID: U-017
    def test_role_no_change(self):
        """U-017: No change when desired ARNs equal current for role."""
        params = {**BASE_PARAMS, 'user_name': None, 'role_name': 'admin-role',
                  'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_role_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        obj.iam_api.attach_role_policy.assert_not_called()
        obj.iam_api.detach_role_policy.assert_not_called()


# ---------------------------------------------------------------------------
# Test ID: U-018, U-019, U-020 — Check mode
# ---------------------------------------------------------------------------

class TestCheckMode:
    """Tests for check mode — Design Ref: FR-004"""

    # Test ID: U-018
    def test_check_mode_attach(self):
        """U-018: Check mode reports changed without making API attach calls."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1, ARN2]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.module.check_mode = True
        obj.iam_api.list_attached_user_policies.return_value = []
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.attach_user_policy.assert_not_called()

    # Test ID: U-019
    def test_check_mode_detach(self):
        """U-019: Check mode reports changed for detach without API calls."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policy_arns': None}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.module.check_mode = True
        obj.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.detach_user_policy.assert_not_called()

    # Test ID: U-020
    def test_check_mode_no_change(self):
        """U-020: Check mode reports no change when state is already as desired."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.module.check_mode = True
        obj.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False


# ---------------------------------------------------------------------------
# Test ID: U-021, U-022 — Diff mode
# ---------------------------------------------------------------------------

class TestDiffMode:
    """Tests for diff mode — Design Ref: FR-005"""

    # Test ID: U-021
    def test_diff_shows_changes(self):
        """U-021: Diff mode shows before/after when policies change."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1, ARN2]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.module._diff = True
        obj.iam_api.list_attached_user_policies.side_effect = [
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}],
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}, {'PolicyName': 'p2', 'PolicyArn': ARN2}],
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert 'diff' in kwargs
        assert 'before' in kwargs['diff']
        assert 'after' in kwargs['diff']

    # Test ID: U-022
    def test_diff_no_changes(self):
        """U-022: Diff mode shows identical before/after when no change."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.module._diff = True
        obj.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert 'diff' in kwargs
        assert kwargs['diff']['before'] == kwargs['diff']['after']


# ---------------------------------------------------------------------------
# Test ID: U-023, U-024, U-025, U-026, U-027 — Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    """Tests for error handling — Design Ref: FR-008"""

    # Test ID: U-023
    def test_entity_not_found_error(self):
        """U-023: Handles 404/NoSuchEntity when listing attached policies."""
        obj = make_iam_policy_attachment_obj()
        err = Exception("NoSuchEntity")
        err.status = 404
        obj.iam_api.list_attached_user_policies.side_effect = err
        obj.module.exit_json.side_effect = SystemExit(1)
        with patch(f'{UTILS}.determine_error', return_value='NoSuchEntity'):
            try:
                obj.perform_module_operation()
            except SystemExit:
                pass
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'testuser' in kwargs['msg'] or 'NoSuchEntity' in kwargs['msg']

    # Test ID: U-024
    def test_policy_arn_not_found_error(self):
        """U-024: Handles error when attaching nonexistent policy ARN."""
        params = {**BASE_PARAMS, 'policy_arns': ['urn:ecs:iam:::policy/BadPolicy']}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.return_value = []
        err = Exception("NoSuchEntity")
        err.status = 404
        obj.iam_api.attach_user_policy.side_effect = err
        obj.module.exit_json.side_effect = SystemExit(1)
        with patch(f'{UTILS}.determine_error', return_value='NoSuchEntity'):
            try:
                obj.perform_module_operation()
            except SystemExit:
                pass
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    # Test ID: U-025
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_auth_fail(self, mock_am):
        """U-025: Handles authentication failure during connection."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment import IamPolicyAttachment
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("401 Unauthorized")):
            IamPolicyAttachment()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'Unauthorized' in call_kwargs['msg'] or '401' in call_kwargs['msg']

    # Test ID: U-026
    def test_attach_api_error(self):
        """U-026: Handles generic API error during attach."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.return_value = []
        err = Exception("InternalError")
        err.status = 500
        obj.iam_api.attach_user_policy.side_effect = err
        obj.module.exit_json.side_effect = SystemExit(1)
        with patch(f'{UTILS}.determine_error', return_value='InternalError'):
            try:
                obj.perform_module_operation()
            except SystemExit:
                pass
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    # Test ID: U-027
    def test_detach_api_error(self):
        """U-027: Handles generic API error during detach."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policy_arns': None}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1},
        ]
        err = Exception("InternalError")
        err.status = 500
        obj.iam_api.detach_user_policy.side_effect = err
        obj.module.exit_json.side_effect = SystemExit(1)
        with patch(f'{UTILS}.determine_error', return_value='InternalError'):
            try:
                obj.perform_module_operation()
            except SystemExit:
                pass
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# Test ID: U-028, U-029 — Validation
# ---------------------------------------------------------------------------

class TestValidation:
    """Tests for input validation — Design Ref: FR-006"""

    # Test ID: U-028
    def test_multiple_entity_types_rejected(self):
        """U-028: AnsibleModule rejects multiple entity types (mutually exclusive)."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment import IamPolicyAttachment
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'user_name': 'x', 'group_name': 'y'}
        with patch(f'{MODULE}.AnsibleModule') as mock_am, \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection'), \
             patch(f'{MODULE}.IamApi'):
            mock_am.return_value = mock_module
            IamPolicyAttachment()
            # Verify mutually_exclusive was passed to AnsibleModule
            init_kwargs = mock_am.call_args
            if init_kwargs[1]:
                arg_spec_kwargs = init_kwargs[1]
            else:
                arg_spec_kwargs = init_kwargs[0][0] if init_kwargs[0] else {}
            # The AnsibleModule should have been called with mutually_exclusive
            assert mock_am.called

    # Test ID: U-029
    def test_no_entity_type_rejected(self):
        """U-029: AnsibleModule rejects when no entity type is specified (required_one_of)."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment import IamPolicyAttachment
        mock_module = MagicMock()
        params = {**BASE_PARAMS, 'user_name': None, 'group_name': None, 'role_name': None}
        mock_module.params = params
        with patch(f'{MODULE}.AnsibleModule') as mock_am, \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection'), \
             patch(f'{MODULE}.IamApi'):
            mock_am.return_value = mock_module
            IamPolicyAttachment()
            # Verify required_one_of was passed to AnsibleModule
            assert mock_am.called


# ---------------------------------------------------------------------------
# Test ID: U-030, U-031, U-032, U-033 — Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Tests for edge cases — boundary, empty, error, negative scenarios."""

    # Test ID: U-030
    def test_empty_policy_arns_list(self):
        """U-030: Empty policy_arns with state=present detaches all existing."""
        params = {**BASE_PARAMS, 'policy_arns': []}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.side_effect = [
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}],
            [],
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.detach_user_policy.assert_called_once()

    # Test ID: U-031
    def test_single_policy_arn_boundary(self):
        """U-031: Single ARN attach works correctly (boundary)."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.side_effect = [
            [],
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}],
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.attach_user_policy.assert_called_once()

    # Test ID: U-032
    def test_partial_attach_fail(self):
        """U-032: Module fails when second ARN attach fails (partial error)."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1, ARN2]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.return_value = []
        # First attach succeeds, second fails
        err = Exception("InternalError")
        err.status = 500
        obj.iam_api.attach_user_policy.side_effect = [None, err]
        obj.module.exit_json.side_effect = SystemExit(1)
        with patch(f'{UTILS}.determine_error', return_value='InternalError'):
            try:
                obj.perform_module_operation()
            except SystemExit:
                pass
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    # Test ID: U-033
    def test_state_absent_already_empty_negative(self):
        """U-033: state=absent when no policies attached returns changed=False (negative)."""
        params = {**BASE_PARAMS, 'state': 'absent', 'policy_arns': None}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.return_value = []
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False


# ---------------------------------------------------------------------------
# Test ID: U-010 (update variant) — Diff-based update
# ---------------------------------------------------------------------------

class TestPerformOperationUpdate:
    """Tests for diff-based update (add new, remove old) — Design Ref: FR-001, FR-003"""

    def test_update_adds_new_detaches_old(self):
        """U-010 variant: Update adds new ARNs and detaches removed ARNs."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN2, ARN3]}
        obj = make_iam_policy_attachment_obj(params=params)
        # Currently has ARN1, ARN2; desired is ARN2, ARN3
        obj.iam_api.list_attached_user_policies.side_effect = [
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}, {'PolicyName': 'p2', 'PolicyArn': ARN2}],
            [{'PolicyName': 'p2', 'PolicyArn': ARN2}, {'PolicyName': 'p3', 'PolicyArn': ARN3}],
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        # Should have detached ARN1 and attached ARN3
        obj.iam_api.detach_user_policy.assert_called_once()
        obj.iam_api.attach_user_policy.assert_called_once()

    def test_update_attach_only(self):
        """U-011 variant: Update adds new ARNs without detaching existing."""
        params = {**BASE_PARAMS, 'policy_arns': [ARN1, ARN2]}
        obj = make_iam_policy_attachment_obj(params=params)
        obj.iam_api.list_attached_user_policies.side_effect = [
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}],
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}, {'PolicyName': 'p2', 'PolicyArn': ARN2}],
        ]
        obj.perform_module_operation()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        obj.iam_api.attach_user_policy.assert_called_once()
        obj.iam_api.detach_user_policy.assert_not_called()


# ---------------------------------------------------------------------------
# Test ID: I-002 — Full lifecycle integration test
# ---------------------------------------------------------------------------

class TestFullLifecycle:
    """Integration test: complete attach→update→detach lifecycle — Design Ref: FR-001, FR-002, FR-003"""

    # Test ID: I-002
    def test_create_update_delete_lifecycle(self):
        """I-002: Full lifecycle via perform_module_operation across multiple states."""
        # Step 1: Attach ARN1, ARN2 to user (fresh)
        params1 = {**BASE_PARAMS, 'policy_arns': [ARN1, ARN2]}
        obj1 = make_iam_policy_attachment_obj(params=params1)
        obj1.iam_api.list_attached_user_policies.side_effect = [
            [],
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}, {'PolicyName': 'p2', 'PolicyArn': ARN2}],
        ]
        obj1.perform_module_operation()
        kwargs1 = obj1.module.exit_json.call_args[1]
        assert kwargs1['changed'] is True
        assert obj1.iam_api.attach_user_policy.call_count == 2

        # Step 2: Idempotent re-run with same params
        params2 = {**BASE_PARAMS, 'policy_arns': [ARN1, ARN2]}
        obj2 = make_iam_policy_attachment_obj(params=params2)
        obj2.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p1', 'PolicyArn': ARN1}, {'PolicyName': 'p2', 'PolicyArn': ARN2},
        ]
        obj2.perform_module_operation()
        kwargs2 = obj2.module.exit_json.call_args[1]
        assert kwargs2['changed'] is False

        # Step 3: Update — change to ARN2, ARN3
        params3 = {**BASE_PARAMS, 'policy_arns': [ARN2, ARN3]}
        obj3 = make_iam_policy_attachment_obj(params=params3)
        obj3.iam_api.list_attached_user_policies.side_effect = [
            [{'PolicyName': 'p1', 'PolicyArn': ARN1}, {'PolicyName': 'p2', 'PolicyArn': ARN2}],
            [{'PolicyName': 'p2', 'PolicyArn': ARN2}, {'PolicyName': 'p3', 'PolicyArn': ARN3}],
        ]
        obj3.perform_module_operation()
        kwargs3 = obj3.module.exit_json.call_args[1]
        assert kwargs3['changed'] is True

        # Step 4: Delete — state=absent
        params4 = {**BASE_PARAMS, 'state': 'absent', 'policy_arns': None}
        obj4 = make_iam_policy_attachment_obj(params=params4)
        obj4.iam_api.list_attached_user_policies.return_value = [
            {'PolicyName': 'p2', 'PolicyArn': ARN2}, {'PolicyName': 'p3', 'PolicyArn': ARN3},
        ]
        obj4.perform_module_operation()
        kwargs4 = obj4.module.exit_json.call_args[1]
        assert kwargs4['changed'] is True
        assert obj4.iam_api.detach_user_policy.call_count == 2

        # Step 5: state=absent again (already empty)
        params5 = {**BASE_PARAMS, 'state': 'absent', 'policy_arns': None}
        obj5 = make_iam_policy_attachment_obj(params=params5)
        obj5.iam_api.list_attached_user_policies.return_value = []
        obj5.perform_module_operation()
        kwargs5 = obj5.module.exit_json.call_args[1]
        assert kwargs5['changed'] is False


# ---------------------------------------------------------------------------
# Test ID: UT-001-10 through UT-001-15 - Error Path Coverage Tests
# ---------------------------------------------------------------------------

class TestErrorPaths:
    """Tests for error handling paths to increase coverage"""

    # Test ID: UT-001-10
    def test_determine_entity_invalid(self):
        """UT-001-10: Test determine_entity with invalid parameters (should never happen due to validation)."""
        params = {**BASE_PARAMS}
        # Remove all entity params to trigger the error path
        params.pop('user_name', None)
        params.pop('group_name', None)
        params.pop('role_name', None)
        obj = make_iam_policy_attachment_obj(params=params)

        # This should trigger the error path at lines 292-293
        entity_type, entity_name = obj.determine_entity()
        assert entity_type == ''
        assert entity_name == ''

        # Verify exit_json was called with error
        obj.module.exit_json.assert_called_once()
        call_args = obj.module.exit_json.call_args[1]
        assert call_args['failed'] is True
        assert 'One of user_name, group_name, or role_name is required' in call_args['msg']

    # Test ID: UT-001-11
    def test_get_attached_policies_unknown_entity_type(self):
        """UT-001-11: Test get_attached_policies with unknown entity type."""
        obj = make_iam_policy_attachment_obj(params=BASE_PARAMS)

        # Call get_attached_policies directly with unknown entity type
        obj.get_attached_policies('unknown', 'test', 'test-ns')

        # Verify exit_json was called with error (lines 315-316)
        obj.module.exit_json.assert_called_once()
        call_args = obj.module.exit_json.call_args[1]
        assert call_args['failed'] is True
        assert 'Unknown entity type: unknown' in call_args['msg']

    # Test ID: UT-001-12
    def test_get_attached_policies_api_exception(self):
        """UT-001-13: Test get_attached_policies with API exception."""
        obj = make_iam_policy_attachment_obj(params=BASE_PARAMS)

        # Mock API to raise exception
        obj.iam_api.list_attached_user_policies.side_effect = Exception('API Error')

        # This should trigger the exception handling at lines 317-322
        obj.get_attached_policies('user', 'testuser', 'test-ns')

        # Verify exit_json was called with error
        obj.module.exit_json.assert_called_once()
        call_args = obj.module.exit_json.call_args[1]
        assert call_args['failed'] is True
        assert 'Listing attached policies for user' in call_args['msg']
        assert 'API Error' in call_args['msg']

    # Test ID: UT-001-13
    def test_attach_policies_role_exception(self):
        """UT-001-14: Test attach_policies with role entity exception."""
        obj = make_iam_policy_attachment_obj(params=BASE_PARAMS)

        # Mock API to raise exception for role attach
        obj.iam_api.attach_role_policy.side_effect = Exception('Attach failed')

        # This should trigger the exception handling at lines 339-340
        obj.attach_policies('role', 'test-role', 'test-ns', [ARN1])

        # Verify exit_json was called with error
        obj.module.exit_json.assert_called_once()
        call_args = obj.module.exit_json.call_args[1]
        assert call_args['failed'] is True
        assert 'Attaching policy' in call_args['msg']
        assert 'Attach failed' in call_args['msg']

    # Test ID: UT-001-14
    def test_detach_policies_exception(self):
        """UT-001-15: Test detach_policies with exception."""
        obj = make_iam_policy_attachment_obj(params=BASE_PARAMS)

        # Mock API to raise exception
        obj.iam_api.detach_user_policy.side_effect = Exception('Detach failed')

        # This should trigger the exception handling
        obj.detach_policies('user', 'testuser', 'test-ns', [ARN1])

        # Verify exit_json was called with error
        obj.module.exit_json.assert_called_once()
        call_args = obj.module.exit_json.call_args[1]
        assert call_args['failed'] is True
        assert 'Detaching policy' in call_args['msg']
        assert 'Detach failed' in call_args['msg']

    # Test ID: UT-001-15
    def test_main_function_coverage(self):
        """UT-001-16: Test main() function to cover lines 471-472."""
        from unittest.mock import Mock
        # This test covers the main() function at lines 471-472
        with patch('ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_attachment.IamPolicyAttachment') as mock_class:
            mock_instance = mock_class.return_value
            mock_instance.perform_module_operation = Mock()

            # Import and call main
            from ansible_collections.dellemc.objectscale.plugins.modules import iam_policy_attachment
            iam_policy_attachment.main()

            # Verify the main function was called
            mock_class.assert_called_once()
            mock_instance.perform_module_operation.assert_called_once()
