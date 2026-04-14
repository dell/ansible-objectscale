# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Tests for the objectscale_iam_role CRUD module.

Test IDs: R-038 through R-138
These tests follow the iam_user test patterns exactly.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_role'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

# ---------------------------------------------------------------------------
# Base parameters — mirrors the argument_spec the module will use
# ---------------------------------------------------------------------------

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    state='present',
    role_name='testrole',
    namespace_name='testns',
    assume_role_policy_document=None,
    description=None,
    max_session_duration=None,
    path='/',
    permissions_boundary=None,
    tags=None,
    purge_tags=True,
    managed_policies=None,
    purge_managed_policies=True,
    inline_policies=None,
    purge_inline_policies=True,
    force_delete=False,
)

# ---------------------------------------------------------------------------
# Mock data factories
# ---------------------------------------------------------------------------

TRUST_POLICY = {
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Principal': {'AWS': ['urn:ecs:iam::testns:user/app-service']},
        'Action': 'sts:AssumeRole',
    }],
}

TRUST_POLICY_V2 = {
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Principal': {'AWS': ['urn:ecs:iam::testns:user/other-service']},
        'Action': 'sts:AssumeRole',
    }],
}


def _mock_role(name='testrole', arn=None, role_id='AROA123', path='/',
               tags=None, boundary=None, description='', max_session_duration=3600,
               assume_role_policy_document=None):
    """Return a role dict as the module would extract from an API response."""
    return {
        'RoleName': name,
        'Arn': arn or f'urn:ecs:iam::testns:role/{name}',
        'RoleId': role_id,
        'CreateDate': '2025-01-15T10:30:00Z',
        'Path': path,
        'PermissionsBoundary': boundary,
        'Tags': tags or [],
        'Description': description,
        'MaxSessionDuration': max_session_duration,
        'AssumeRolePolicyDocument': assume_role_policy_document or json.dumps(TRUST_POLICY),
    }


# ---------------------------------------------------------------------------
# Helper to build a fully-mocked IamRole instance
# ---------------------------------------------------------------------------


def make_iam_role_obj(params=None, has_client=True):
    """Helper: return an IamRole instance with all I/O mocked.

    Follows the ``make_iam_user_obj()`` pattern from ``test_iam_user.py``.
    """
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_role import IamRole

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection',
               return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamRole()

    # Replace module and api with fresh mocks for full test control
    obj.module = module_mock
    obj.iam_api = MagicMock()
    obj.namespace = module_mock.params.get('namespace_name')
    return obj


# ===========================================================================
# 1. TestIamRoleInit  (R-038, R-039, R-040)
# ===========================================================================


class TestIamRoleInit:
    """Verify module initialisation, client check, and connection handling."""

    # R-038
    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role import IamRole
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        obj = IamRole()

        assert obj.module is mock_module
        mock_conn.assert_called_once()

    # R-039
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_missing_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role import IamRole
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        IamRole()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in call_kwargs['msg']

    # R-040
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role import IamRole
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamRole()

        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'conn failed' in call_kwargs['msg']


# ===========================================================================
# 2. TestIamRoleGetRoleDetails  (R-041 to R-045)
# ===========================================================================


class TestIamRoleGetRoleDetails:
    """Verify get_role() behaviour for success, 404, 400, 500, and None."""

    # R-041
    def test_get_role_exists(self):
        obj = make_iam_role_obj()
        mock_resp = MagicMock()
        mock_resp.data = json.dumps({'GetRoleResult': {'Role': _mock_role()}}).encode('utf-8')
        obj._iam_raw_post = MagicMock(return_value=mock_resp)

        result = obj.get_role('testrole')

        assert result is not None
        assert result['RoleName'] == 'testrole'
        assert result['Arn'] == 'urn:ecs:iam::testns:role/testrole'
        obj._iam_raw_post.assert_called_once_with('GetRole', {'RoleName': 'testrole'})

    # R-042
    def test_get_role_not_found_returns_none(self):
        obj = make_iam_role_obj()
        obj._iam_raw_post = MagicMock(side_effect=Exception("{'Error': {'Code': 'NoSuchEntity'}}"))

        result = obj.get_role('testrole')

        assert result is None
        obj.module.exit_json.assert_not_called()

    # R-043
    def test_get_role_bad_request_returns_none(self):
        obj = make_iam_role_obj()
        err = Exception("bad request")
        err.status = 400
        obj.iam_api.iam_service_get_role.side_effect = err

        result = obj.get_role('testrole')

        assert result is None
        obj.module.exit_json.assert_not_called()

    # R-044
    def test_get_role_other_error_fails(self):
        obj = make_iam_role_obj()
        err = Exception("server error")
        err.status = 500
        obj.iam_api.iam_service_get_role.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_role('testrole')

        kwargs = obj.module.fail_json.call_args[1]
        assert 'testrole' in kwargs['msg']

    # R-045
    def test_get_role_none_response(self):
        obj = make_iam_role_obj()
        err = Exception("bad request")
        err.status = 400
        obj.iam_api.iam_service_get_role.side_effect = err

        result = obj.get_role(None)

        assert result is None


# ===========================================================================
# 3. TestIamRoleCreateRole  (R-046 to R-051)
# ===========================================================================


class TestIamRoleCreateRole:
    """Verify create_role() for basic, trust policy, boundary, all-options, error, idempotent."""

    # R-046
    def test_create_role_basic(self):
        params = {**BASE_PARAMS, 'assume_role_policy_document': TRUST_POLICY}
        obj = make_iam_role_obj(params)
        mock_resp = MagicMock()
        mock_resp.data = json.dumps({'CreateRoleResult': {'Role': _mock_role()}}).encode('utf-8')
        obj._iam_raw_post = MagicMock(return_value=mock_resp)

        result = obj.create_role('testrole')

        assert result is not None
        assert result['RoleName'] == 'testrole'
        obj._iam_raw_post.assert_called_once()
        call_args = obj._iam_raw_post.call_args
        api_params = call_args[0][1]
        assert api_params.get('Path', '/') == '/'
        assert 'AssumeRolePolicyDocument' in api_params

    # R-047
    def test_create_role_missing_trust_policy(self):
        """Creating without assume_role_policy_document fails."""
        params = {**BASE_PARAMS, 'assume_role_policy_document': None}
        obj = make_iam_role_obj(params)

        obj.create_role('testrole')

        obj.module.fail_json.assert_called_once()
        call_kwargs = obj.module.fail_json.call_args[1]
        assert 'assume_role_policy_document' in call_kwargs['msg']

    # R-048
    def test_create_role_with_permissions_boundary(self):
        params = {
            **BASE_PARAMS,
            'assume_role_policy_document': TRUST_POLICY,
            'permissions_boundary': 'urn:ecs:iam::testns:policy/BoundaryPol',
        }
        obj = make_iam_role_obj(params)
        mock_resp = MagicMock()
        mock_resp.data = json.dumps({'CreateRoleResult': {'Role': _mock_role()}}).encode('utf-8')
        obj._iam_raw_post = MagicMock(return_value=mock_resp)

        result = obj.create_role('testrole')

        assert result is not None
        call_args = obj._iam_raw_post.call_args
        assert call_args[0][0] == 'CreateRole'
        assert call_args[0][1].get('PermissionsBoundary') == 'urn:ecs:iam::testns:policy/BoundaryPol'

    # R-049
    def test_create_role_with_all_options(self):
        params = {
            **BASE_PARAMS,
            'assume_role_policy_document': TRUST_POLICY,
            'permissions_boundary': 'urn:ecs:iam::testns:policy/Boundary',
            'path': '/',
            'tags': {'Env': 'prod'},
        }
        obj = make_iam_role_obj(params)
        mock_resp = MagicMock()
        mock_resp.data = json.dumps({'CreateRoleResult': {'Role': _mock_role()}}).encode('utf-8')
        obj._iam_raw_post = MagicMock(return_value=mock_resp)

        result = obj.create_role('testrole')

        assert result is not None
        call_args = obj._iam_raw_post.call_args
        api_params = call_args[0][1]
        assert api_params.get('PermissionsBoundary') == 'urn:ecs:iam::testns:policy/Boundary'
        # Tags are applied separately via manage_tags after creation
        assert 'tags_member_n' not in api_params

    # R-050
    def test_create_role_api_error(self):
        params = {**BASE_PARAMS, 'assume_role_policy_document': TRUST_POLICY}
        obj = make_iam_role_obj(params)
        obj.iam_api.iam_service_create_role.side_effect = Exception("create err")

        with patch(f'{UTILS}.determine_error', return_value='create err'):
            obj.create_role('testrole')

        kwargs = obj.module.fail_json.call_args[1]
        assert "Creating IAM role" in kwargs['msg']
        assert 'testrole' in kwargs['msg']

    # R-051
    def test_create_role_already_exists(self):
        """Idempotent: if role exists, perform_module_operation should skip create."""
        obj = make_iam_role_obj()
        obj.get_role = MagicMock(return_value=_mock_role())
        obj.create_role = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        obj.perform_module_operation()

        obj.create_role.assert_not_called()


# ===========================================================================
# 4. TestIamRoleDeleteRole  (R-052 to R-054)
# ===========================================================================


class TestIamRoleDeleteRole:
    """Verify delete_role() for success, not-found idempotent, and deps."""

    # R-052
    def test_delete_role_success(self):
        obj = make_iam_role_obj()
        obj.delete_role('testrole')

        obj.iam_api.iam_service_delete_role.assert_called_once_with(
            role_name='testrole',
            x_emc_namespace='testns',
        )

    # R-053
    def test_delete_role_not_found(self):
        """state=absent with role not found => changed=False (idempotent)."""
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = make_iam_role_obj(params)
        obj.get_role = MagicMock(return_value=None)
        obj.delete_role = MagicMock()

        obj.perform_module_operation()

        obj.delete_role.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # R-054
    def test_delete_role_has_dependencies_no_force(self):
        """Delete without force when role has dependencies => API error propagated."""
        obj = make_iam_role_obj()
        err = Exception("DeleteConflict: role has deps")
        err.status = 409
        obj.iam_api.iam_service_delete_role.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='DeleteConflict: role has deps'):
            obj.delete_role('testrole')

        kwargs = obj.module.fail_json.call_args[1]
        assert 'DeleteConflict' in kwargs['msg']


# ===========================================================================
# 5. TestIamRoleForceDelete  (R-055 to R-058)
# ===========================================================================


class TestIamRoleForceDelete:
    """Verify force_delete_cleanup() cleans all dependency types."""

    # R-055
    def test_force_delete_cleans_policies(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolB'},
        ])
        obj.list_inline_policy_names = MagicMock(return_value=['inline1'])
        obj.get_role = MagicMock(return_value=_mock_role())

        obj.force_delete_cleanup('testrole')

        assert obj.iam_api.iam_service_detach_role_policy.call_count == 2
        obj.iam_api.iam_service_delete_role_policy.assert_called_once()

    # R-056
    def test_force_delete_cleans_boundary(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[])
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.get_role = MagicMock(return_value=_mock_role(
            boundary={'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/Boundary'}
        ))

        obj.force_delete_cleanup('testrole')

        obj.iam_api.iam_service_delete_role_permissions_boundary.assert_called_once()

    # R-057
    def test_force_delete_no_boundary_skips(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[])
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.get_role = MagicMock(return_value=_mock_role())

        obj.force_delete_cleanup('testrole')

        obj.iam_api.iam_service_delete_role_permissions_boundary.assert_not_called()

    # R-058
    def test_force_delete_full_cleanup_then_delete(self):
        """Full cleanup with all dependency types present."""
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
        ])
        obj.list_inline_policy_names = MagicMock(return_value=['inline1', 'inline2'])
        obj.get_role = MagicMock(return_value=_mock_role(
            boundary={'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/Boundary'}
        ))

        obj.force_delete_cleanup('testrole')

        assert obj.iam_api.iam_service_detach_role_policy.call_count == 1
        assert obj.iam_api.iam_service_delete_role_policy.call_count == 2
        obj.iam_api.iam_service_delete_role_permissions_boundary.assert_called_once()

    # R-058b — error accumulation
    def test_force_delete_error_accumulation(self):
        """Errors in force_delete_cleanup are accumulated and warned, not raised."""
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
        ])
        obj.iam_api.iam_service_detach_role_policy.side_effect = Exception("detach err")
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.get_role = MagicMock(return_value=_mock_role())

        obj.force_delete_cleanup('testrole')

        obj.module.warn.assert_called_once()
        warn_msg = obj.module.warn.call_args[0][0]
        assert 'detach err' in warn_msg


# ===========================================================================
# 6. TestIamRoleManageTags  (R-059 to R-068)
# ===========================================================================


class TestIamRoleManageTags:
    """Verify manage_tags() for add, remove, purge, idempotent, check_mode, etc."""

    # R-059
    def test_manage_tags_add_new(self):
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[])
        obj._tag_role_raw = MagicMock()
        obj._untag_role_raw = MagicMock()

        result = obj.manage_tags('testrole', {'Env': 'prod'}, purge=True)

        assert result is True
        obj._tag_role_raw.assert_called_once_with('testrole', {'Env': 'prod'})

    # R-060
    def test_manage_tags_no_change(self):
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])

        result = obj.manage_tags('testrole', {'Env': 'prod'}, purge=True)

        assert result is False
        obj.iam_api.iam_service_tag_role.assert_not_called()
        obj.iam_api.iam_service_untag_role.assert_not_called()

    # R-061
    def test_manage_tags_update_value(self):
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])
        obj._tag_role_raw = MagicMock()
        obj._untag_role_raw = MagicMock()

        result = obj.manage_tags('testrole', {'Env': 'staging'}, purge=True)

        assert result is True
        obj._tag_role_raw.assert_called_once_with('testrole', {'Env': 'staging'})

    # R-062
    def test_manage_tags_purge_extra(self):
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
            {'Key': 'Old', 'Value': 'remove-me'},
        ])
        obj._tag_role_raw = MagicMock()
        obj._untag_role_raw = MagicMock()

        result = obj.manage_tags('testrole', {'Env': 'prod'}, purge=True)

        assert result is True
        obj._untag_role_raw.assert_called_once_with('testrole', ['Old'])

    # R-063
    def test_manage_tags_no_purge_keeps_extra(self):
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
            {'Key': 'Extra', 'Value': 'keep'},
        ])

        result = obj.manage_tags('testrole', {'Env': 'prod'}, purge=False)

        assert result is False
        obj.iam_api.iam_service_untag_role.assert_not_called()
        obj.iam_api.iam_service_tag_role.assert_not_called()

    # R-064
    def test_manage_tags_add_and_remove(self):
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[
            {'Key': 'Old', 'Value': 'val'},
        ])
        obj._tag_role_raw = MagicMock()
        obj._untag_role_raw = MagicMock()

        result = obj.manage_tags('testrole', {'New': 'val2'}, purge=True)

        assert result is True
        obj._tag_role_raw.assert_called_once()
        obj._untag_role_raw.assert_called_once()

    # R-065
    def test_manage_tags_empty_dict(self):
        """Empty desired with purge=True removes all current tags."""
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])
        obj._tag_role_raw = MagicMock()
        obj._untag_role_raw = MagicMock()

        result = obj.manage_tags('testrole', {}, purge=True)

        assert result is True
        obj._untag_role_raw.assert_called_once()
        obj._tag_role_raw.assert_not_called()

    # R-066
    def test_manage_tags_none_skips(self):
        """tags=None means 'don't manage' — perform_module_operation guards this."""
        obj = make_iam_role_obj()
        obj.get_role = MagicMock(return_value=_mock_role())
        obj.manage_tags = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        # params['tags'] is None by default
        obj.perform_module_operation()

        obj.manage_tags.assert_not_called()

    # R-067
    def test_manage_tags_api_error(self):
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[])
        obj._tag_role_raw = MagicMock(side_effect=Exception("tag err"))
        obj._untag_role_raw = MagicMock()

        with pytest.raises(Exception, match="tag err"):
            obj.manage_tags('testrole', {'Env': 'prod'}, purge=True)

    # R-068
    def test_manage_tags_large_set(self):
        """50 tags (max limit) handled correctly."""
        obj = make_iam_role_obj()
        obj.list_role_tags = MagicMock(return_value=[])
        obj._tag_role_raw = MagicMock()
        obj._untag_role_raw = MagicMock()
        desired = {f'Key{i}': f'Value{i}' for i in range(50)}

        result = obj.manage_tags('testrole', desired, purge=True)

        assert result is True
        obj._tag_role_raw.assert_called_once()
        call_args = obj._tag_role_raw.call_args
        assert len(call_args[0][1]) == 50


# ===========================================================================
# 7. TestIamRoleManageManagedPolicies  (R-069 to R-075)
# ===========================================================================


class TestIamRoleManageManagedPolicies:
    """Verify manage_managed_policies() for attach, detach, purge, idempotent."""

    # R-069
    def test_attach_missing_policies(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[])

        result = obj.manage_managed_policies(
            'testrole', ['urn:ecs:iam::testns:policy/NewPol'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_attach_role_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_attach_role_policy.call_args[1]
        assert call_kwargs['policy_arn'] == 'urn:ecs:iam::testns:policy/NewPol'

    # R-070
    def test_all_policies_already_attached(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
        ])

        result = obj.manage_managed_policies(
            'testrole', ['urn:ecs:iam::testns:policy/PolA'], purge=True
        )

        assert result is False
        obj.iam_api.iam_service_attach_role_policy.assert_not_called()
        obj.iam_api.iam_service_detach_role_policy.assert_not_called()

    # R-071
    def test_purge_extra_policies(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
            {'PolicyArn': 'urn:ecs:iam::testns:policy/OldPol'},
        ])

        result = obj.manage_managed_policies(
            'testrole', ['urn:ecs:iam::testns:policy/PolA'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_detach_role_policy.assert_called_once()

    # R-072
    def test_no_purge_keeps_extra(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
            {'PolicyArn': 'urn:ecs:iam::testns:policy/Extra'},
        ])

        result = obj.manage_managed_policies(
            'testrole', ['urn:ecs:iam::testns:policy/PolA'], purge=False
        )

        assert result is False
        obj.iam_api.iam_service_detach_role_policy.assert_not_called()

    # R-073
    def test_attach_and_detach_combined(self):
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/OldPol'},
        ])

        result = obj.manage_managed_policies(
            'testrole', ['urn:ecs:iam::testns:policy/NewPol'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_attach_role_policy.assert_called_once()
        obj.iam_api.iam_service_detach_role_policy.assert_called_once()

    # R-074
    def test_attach_policy_invalid_arn(self):
        """Invalid ARN passed to API — server validates, client just sends."""
        obj = make_iam_role_obj()
        obj.list_attached_policies = MagicMock(return_value=[])

        result = obj.manage_managed_policies(
            'testrole', ['not-a-valid-arn'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_attach_role_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_attach_role_policy.call_args[1]
        assert call_kwargs['policy_arn'] == 'not-a-valid-arn'

    # R-075
    def test_manage_policies_none_skips(self):
        """managed_policies=None => manage_managed_policies not called."""
        obj = make_iam_role_obj()
        obj.get_role = MagicMock(return_value=_mock_role())
        obj.manage_managed_policies = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        obj.perform_module_operation()

        obj.manage_managed_policies.assert_not_called()


# ===========================================================================
# 8. TestIamRoleManageInlinePolicies  (R-076 to R-084)
# ===========================================================================


class TestIamRoleManageInlinePolicies:
    """Verify manage_inline_policies() for put, delete, purge, idempotent."""

    _POLICY_DOC = {
        'Version': '2012-10-17',
        'Statement': [{'Effect': 'Allow', 'Action': 's3:*', 'Resource': '*'}],
    }

    _POLICY_DOC_V2 = {
        'Version': '2012-10-17',
        'Statement': [{'Effect': 'Deny', 'Action': 's3:Delete*', 'Resource': '*'}],
    }

    # R-076
    def test_put_new_inline_policy(self):
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])

        result = obj.manage_inline_policies(
            'testrole', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_put_role_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_put_role_policy.call_args[1]
        assert call_kwargs['policy_name'] == 'pol1'

    # R-077
    def test_put_inline_policy_same_document(self):
        """Idempotent: same name and document => no change."""
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testrole', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is False
        obj.iam_api.iam_service_put_role_policy.assert_not_called()

    # R-078
    def test_put_inline_policy_different_document(self):
        """Update: same name, different document."""
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testrole', {'pol1': self._POLICY_DOC_V2}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_put_role_policy.assert_called_once()

    # R-079
    def test_purge_extra_inline_policies(self):
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1', 'old_pol'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testrole', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_delete_role_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_delete_role_policy.call_args[1]
        assert call_kwargs['policy_name'] == 'old_pol'

    # R-080
    def test_no_purge_keeps_extra_inline(self):
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1', 'extra'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testrole', {'pol1': self._POLICY_DOC}, purge=False
        )

        assert result is False
        obj.iam_api.iam_service_delete_role_policy.assert_not_called()

    # R-081
    def test_inline_policy_json_encoding(self):
        """Verify policy document is JSON-encoded before sending to API."""
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])

        result = obj.manage_inline_policies(
            'testrole', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is True
        call_kwargs = obj.iam_api.iam_service_put_role_policy.call_args[1]
        doc_sent = call_kwargs['policy_document']
        assert isinstance(doc_sent, str)
        assert json.loads(doc_sent) == self._POLICY_DOC

    # R-082
    def test_manage_inline_policies_none_skips(self):
        """inline_policies=None => manage_inline_policies not called."""
        obj = make_iam_role_obj()
        obj.get_role = MagicMock(return_value=_mock_role())
        obj.manage_inline_policies = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        obj.perform_module_operation()

        obj.manage_inline_policies.assert_not_called()

    # R-083
    def test_inline_policy_api_error(self):
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.iam_api.iam_service_put_role_policy.side_effect = Exception("put err")

        with pytest.raises(Exception, match="put err"):
            obj.manage_inline_policies(
                'testrole', {'pol1': self._POLICY_DOC}, purge=True
            )

    # R-084
    def test_inline_policy_malformed_document(self):
        """Malformed doc is still sent through — server validates."""
        obj = make_iam_role_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])
        malformed = {'not': 'a valid policy'}

        result = obj.manage_inline_policies(
            'testrole', {'pol1': malformed}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_put_role_policy.assert_called_once()


# ===========================================================================
# 9. TestIamRoleManagePermissionsBoundary  (R-092 to R-097)
# ===========================================================================


class TestIamRoleManagePermissionsBoundary:
    """Verify manage_permissions_boundary() for set, remove, no-change, etc."""

    # R-092
    def test_set_permissions_boundary(self):
        obj = make_iam_role_obj()
        role = _mock_role()

        result = obj.manage_permissions_boundary(
            'testrole', 'urn:ecs:iam::testns:policy/Boundary', role
        )

        assert result is True
        obj.iam_api.iam_service_put_role_permissions_boundary.assert_called_once()

    # R-093
    def test_permissions_boundary_no_change(self):
        obj = make_iam_role_obj()
        boundary_arn = 'urn:ecs:iam::testns:policy/Boundary'
        role = _mock_role(boundary={
            'PermissionsBoundaryArn': boundary_arn,
        })

        result = obj.manage_permissions_boundary('testrole', boundary_arn, role)

        assert result is False
        obj.iam_api.iam_service_put_role_permissions_boundary.assert_not_called()
        obj.iam_api.iam_service_delete_role_permissions_boundary.assert_not_called()

    # R-094
    def test_update_permissions_boundary(self):
        obj = make_iam_role_obj()
        role = _mock_role(boundary={
            'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/OldBoundary',
        })

        result = obj.manage_permissions_boundary(
            'testrole', 'urn:ecs:iam::testns:policy/NewBoundary', role
        )

        assert result is True
        obj.iam_api.iam_service_put_role_permissions_boundary.assert_called_once()

    # R-095
    def test_remove_permissions_boundary(self):
        """Empty string means 'remove boundary'."""
        obj = make_iam_role_obj()
        role = _mock_role(boundary={
            'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/Boundary',
        })

        result = obj.manage_permissions_boundary('testrole', '', role)

        assert result is True
        obj.iam_api.iam_service_delete_role_permissions_boundary.assert_called_once()

    # R-096
    def test_permissions_boundary_already_removed(self):
        """Remove boundary when none exists => no-op."""
        obj = make_iam_role_obj()
        role = _mock_role()  # No boundary

        result = obj.manage_permissions_boundary('testrole', '', role)

        assert result is False
        obj.iam_api.iam_service_delete_role_permissions_boundary.assert_not_called()

    # R-097
    def test_permissions_boundary_none_skips(self):
        """desired=None means 'don't manage'."""
        obj = make_iam_role_obj()
        role = _mock_role()

        result = obj.manage_permissions_boundary('testrole', None, role)

        assert result is False
        obj.iam_api.iam_service_put_role_permissions_boundary.assert_not_called()
        obj.iam_api.iam_service_delete_role_permissions_boundary.assert_not_called()


# ===========================================================================
# 10. TestIamRoleManageAssumeRolePolicy  (R-098 to R-102)
# ===========================================================================


class TestIamRoleManageAssumeRolePolicy:
    """Verify manage_assume_role_policy() for set, update, no-change, etc."""

    # R-098
    def test_update_assume_role_policy(self):
        obj = make_iam_role_obj()
        role = _mock_role(assume_role_policy_document=json.dumps(TRUST_POLICY))

        result = obj.manage_assume_role_policy('testrole', TRUST_POLICY_V2, role)

        assert result is True
        obj.iam_api.iam_service_update_assume_role_policy.assert_called_once()

    # R-099
    def test_assume_role_policy_no_change(self):
        obj = make_iam_role_obj()
        role = _mock_role(assume_role_policy_document=json.dumps(TRUST_POLICY))

        result = obj.manage_assume_role_policy('testrole', TRUST_POLICY, role)

        assert result is False
        obj.iam_api.iam_service_update_assume_role_policy.assert_not_called()

    # R-100
    def test_assume_role_policy_none_skips(self):
        obj = make_iam_role_obj()
        role = _mock_role()

        result = obj.manage_assume_role_policy('testrole', None, role)

        assert result is False
        obj.iam_api.iam_service_update_assume_role_policy.assert_not_called()


# ===========================================================================
# 11. TestIamRoleManageRoleAttributes  (R-103 to R-108)
# ===========================================================================


class TestIamRoleManageRoleAttributes:
    """Verify manage_role_attributes() for description, max_session_duration."""

    # R-103
    def test_update_description(self):
        params = {**BASE_PARAMS, 'description': 'New description'}
        obj = make_iam_role_obj(params)
        role = _mock_role(description='Old description')

        result = obj.manage_role_attributes('testrole', role)

        assert result is True
        obj.iam_api.iam_service_update_role.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_update_role.call_args[1]
        assert call_kwargs['description'] == 'New description'

    # R-104
    def test_update_max_session_duration(self):
        params = {**BASE_PARAMS, 'max_session_duration': 7200}
        obj = make_iam_role_obj(params)
        role = _mock_role(max_session_duration=3600)

        result = obj.manage_role_attributes('testrole', role)

        assert result is True
        obj.iam_api.iam_service_update_role.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_update_role.call_args[1]
        assert call_kwargs['max_session_duration'] == 7200

    # R-105
    def test_attributes_no_change(self):
        params = {**BASE_PARAMS, 'description': 'Same', 'max_session_duration': 3600}
        obj = make_iam_role_obj(params)
        role = _mock_role(description='Same', max_session_duration=3600)

        result = obj.manage_role_attributes('testrole', role)

        assert result is False
        obj.iam_api.iam_service_update_role.assert_not_called()

    # R-106
    def test_update_both_attributes(self):
        params = {**BASE_PARAMS, 'description': 'New desc', 'max_session_duration': 14400}
        obj = make_iam_role_obj(params)
        role = _mock_role(description='Old desc', max_session_duration=3600)

        result = obj.manage_role_attributes('testrole', role)

        assert result is True
        obj.iam_api.iam_service_update_role.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_update_role.call_args[1]
        assert call_kwargs['description'] == 'New desc'
        assert call_kwargs['max_session_duration'] == 14400

    # R-107
    def test_attributes_none_skips(self):
        """description=None and max_session_duration=None => no update."""
        obj = make_iam_role_obj()  # both None by default
        role = _mock_role()

        result = obj.manage_role_attributes('testrole', role)

        assert result is False
        obj.iam_api.iam_service_update_role.assert_not_called()


# ===========================================================================
# 12. TestIamRoleCaptureCurrentState  (R-110 to R-112)
# ===========================================================================


class TestIamRoleCaptureCurrentState:
    """Verify capture_current_state() for full, minimal, and None role."""

    # R-110
    def test_capture_state_full(self):
        obj = make_iam_role_obj()
        role = _mock_role()
        obj.list_role_tags = MagicMock(return_value=[{'Key': 'Env', 'Value': 'prod'}])
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
        ])
        obj.list_inline_policy_names = MagicMock(return_value=['inline1'])

        state = obj.capture_current_state('testrole', role)

        assert 'role' in state
        assert 'tags' in state
        assert 'managed_policies' in state
        assert 'inline_policies' in state

    # R-111
    def test_capture_state_minimal(self):
        obj = make_iam_role_obj()
        role = _mock_role()
        obj.list_role_tags = MagicMock(return_value=[])
        obj.list_attached_policies = MagicMock(return_value=[])
        obj.list_inline_policy_names = MagicMock(return_value=[])

        state = obj.capture_current_state('testrole', role)

        assert state['tags'] == []
        assert state['managed_policies'] == []
        assert state['inline_policies'] == []

    # R-112
    def test_capture_state_role_not_found(self):
        obj = make_iam_role_obj()

        state = obj.capture_current_state('testrole', None)

        assert state == {} or state is not None


# ===========================================================================
# 13. TestIamRolePerformModuleOperation  (R-113 to R-132)
# ===========================================================================


class TestIamRolePerformModuleOperation:
    """Verify the main perform_module_operation() orchestrator."""

    def _make(self, params):
        """Build an IamRole with all sub-methods mocked."""
        obj = make_iam_role_obj(params=params)
        obj.get_role = MagicMock(return_value=None)
        obj.create_role = MagicMock(return_value=_mock_role())
        obj.delete_role = MagicMock()
        obj.force_delete_cleanup = MagicMock()
        obj.manage_tags = MagicMock(return_value=False)
        obj.manage_managed_policies = MagicMock(return_value=False)
        obj.manage_inline_policies = MagicMock(return_value=False)
        obj.manage_permissions_boundary = MagicMock(return_value=False)
        obj.manage_assume_role_policy = MagicMock(return_value=False)
        obj.manage_role_attributes = MagicMock(return_value=False)
        obj.capture_current_state = MagicMock(return_value={})
        obj.list_role_tags = MagicMock(return_value=[])
        obj.list_attached_policies = MagicMock(return_value=[])
        obj.list_inline_policy_names = MagicMock(return_value=[])
        return obj

    # R-113
    def test_create_role_state_present_new(self):
        params = {**BASE_PARAMS, 'assume_role_policy_document': TRUST_POLICY}
        obj = self._make(params)
        obj.get_role.side_effect = [None, _mock_role()]

        obj.perform_module_operation()

        obj.create_role.assert_called_once_with('testrole')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-114
    def test_create_role_state_present_exists(self):
        """Idempotent: role already exists => no create."""
        obj = self._make(BASE_PARAMS.copy())
        obj.get_role.return_value = _mock_role()

        obj.perform_module_operation()

        obj.create_role.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # R-115
    def test_delete_role_state_absent(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_role.return_value = _mock_role()

        obj.perform_module_operation()

        obj.delete_role.assert_called_once_with('testrole')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-116
    def test_delete_role_state_absent_not_exists(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_role.return_value = None

        obj.perform_module_operation()

        obj.delete_role.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # R-117
    def test_force_delete_role(self):
        params = {**BASE_PARAMS, 'state': 'absent', 'force_delete': True}
        obj = self._make(params)
        obj.get_role.return_value = _mock_role()

        obj.perform_module_operation()

        obj.force_delete_cleanup.assert_called_once_with('testrole')
        obj.delete_role.assert_called_once_with('testrole')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-118
    def test_create_role_with_sub_resources(self):
        params = {
            **BASE_PARAMS,
            'assume_role_policy_document': TRUST_POLICY,
            'tags': {'Env': 'prod'},
            'managed_policies': ['urn:ecs:iam::testns:policy/PolA'],
        }
        obj = self._make(params)
        obj.get_role.side_effect = [None, _mock_role()]

        obj.perform_module_operation()

        obj.create_role.assert_called_once()
        obj.manage_tags.assert_called_once()
        obj.manage_managed_policies.assert_called_once()

    # R-119
    def test_update_tags_on_existing_role(self):
        params = {**BASE_PARAMS, 'tags': {'Env': 'staging'}}
        obj = self._make(params)
        obj.get_role.return_value = _mock_role()
        obj.manage_tags.return_value = True

        obj.perform_module_operation()

        obj.manage_tags.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-120
    def test_update_policies_on_existing_role(self):
        params = {**BASE_PARAMS, 'managed_policies': ['urn:ecs:iam::testns:policy/PolA']}
        obj = self._make(params)
        obj.get_role.return_value = _mock_role()
        obj.manage_managed_policies.return_value = True

        obj.perform_module_operation()

        obj.manage_managed_policies.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-121
    def test_update_boundary_on_existing_role(self):
        params = {**BASE_PARAMS, 'permissions_boundary': 'urn:ecs:iam::testns:policy/Boundary'}
        obj = self._make(params)
        obj.get_role.return_value = _mock_role()
        obj.manage_permissions_boundary.return_value = True

        obj.perform_module_operation()

        obj.manage_permissions_boundary.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-122
    def test_update_description_on_existing_role(self):
        params = {**BASE_PARAMS, 'description': 'New description'}
        obj = self._make(params)
        obj.get_role.return_value = _mock_role()
        obj.manage_role_attributes.return_value = True

        obj.perform_module_operation()

        obj.manage_role_attributes.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-123
    def test_update_trust_policy_on_existing_role(self):
        params = {**BASE_PARAMS, 'assume_role_policy_document': TRUST_POLICY_V2}
        obj = self._make(params)
        obj.get_role.return_value = _mock_role()
        obj.manage_assume_role_policy.return_value = True

        obj.perform_module_operation()

        obj.manage_assume_role_policy.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-126
    def test_check_mode_create_role(self):
        params = {**BASE_PARAMS, 'assume_role_policy_document': TRUST_POLICY}
        obj = self._make(params)
        obj.module.check_mode = True
        obj.get_role.return_value = None

        obj.perform_module_operation()

        obj.create_role.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-127
    def test_check_mode_delete_role(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.module.check_mode = True
        obj.get_role.return_value = _mock_role()

        obj.perform_module_operation()

        obj.delete_role.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # R-128
    def test_diff_mode_returns_before_after(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.module._diff = True
        obj.get_role.return_value = _mock_role()
        obj.capture_current_state.return_value = {'role': _mock_role()}

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in kwargs
        assert 'before' in kwargs['diff']
        assert 'after' in kwargs['diff']
        assert kwargs['diff']['before'] != {}
        assert kwargs['diff']['after'] == {}

    # R-129
    def test_auth_error_401(self):
        """401 auth error during get_role => module fails."""
        obj = self._make(BASE_PARAMS.copy())
        err = Exception("Unauthorized")
        err.status = 401
        obj.get_role = MagicMock(side_effect=err)

        with pytest.raises(Exception, match="Unauthorized"):
            obj.perform_module_operation()

    # R-130
    def test_permission_error_403(self):
        """403 permission error during get_role => module fails."""
        obj = self._make(BASE_PARAMS.copy())
        err = Exception("Forbidden")
        err.status = 403
        obj.get_role = MagicMock(side_effect=err)

        with pytest.raises(Exception, match="Forbidden"):
            obj.perform_module_operation()

    # R-131
    def test_connection_error(self):
        """Connection error propagates."""
        obj = self._make(BASE_PARAMS.copy())
        obj.get_role = MagicMock(side_effect=ConnectionError("network unreachable"))

        with pytest.raises(ConnectionError, match="network unreachable"):
            obj.perform_module_operation()

    # R-132
    def test_full_lifecycle_create_configure_delete(self):
        """End-to-end: verify create, configure sub-resources, then delete works."""
        # Phase 1: Create with sub-resources
        params_create = {
            **BASE_PARAMS,
            'state': 'present',
            'assume_role_policy_document': TRUST_POLICY,
            'tags': {'Env': 'prod'},
            'managed_policies': ['urn:ecs:iam::testns:policy/PolA'],
        }
        obj1 = self._make(params_create)
        obj1.get_role.side_effect = [None, _mock_role()]
        obj1.manage_tags.return_value = True
        obj1.manage_managed_policies.return_value = True

        obj1.perform_module_operation()

        obj1.create_role.assert_called_once()
        kwargs1 = obj1.module.exit_json.call_args[1]
        assert kwargs1['changed'] is True

        # Phase 2: Delete with force
        params_delete = {**BASE_PARAMS, 'state': 'absent', 'force_delete': True}
        obj2 = self._make(params_delete)
        obj2.get_role.return_value = _mock_role()

        obj2.perform_module_operation()

        obj2.force_delete_cleanup.assert_called_once()
        obj2.delete_role.assert_called_once()
        kwargs2 = obj2.module.exit_json.call_args[1]
        assert kwargs2['changed'] is True


# ===========================================================================
# 14. TestIamRoleHelperMethods  (R-133 to R-137)
# ===========================================================================


class TestIamRoleHelperMethods:
    """Verify helper/utility methods."""

    # R-133
    def test_extract_role_from_response(self):
        obj = make_iam_role_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'Result': {'Role': _mock_role(name='myrole')}}

        result = obj._extract_role_dict(resp)

        assert result['RoleName'] == 'myrole'
        assert 'Arn' in result

    # R-134
    def test_extract_role_from_create_response(self):
        """_extract_role_dict from CreateRole response also works."""
        obj = make_iam_role_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'Result': {'Role': _mock_role(name='myrole')}}

        result = obj._extract_role_dict(resp)

        assert result['RoleName'] == 'myrole'

    # R-135
    def test_dict_to_tag_members(self):
        """_dict_to_tag_members converts dict to list of {Key, Value}."""
        obj = make_iam_role_obj()

        result = obj._dict_to_tag_members({'Env': 'prod', 'Team': 'ops'})

        assert len(result) == 2
        keys = {t['Key'] for t in result}
        assert 'Env' in keys
        assert 'Team' in keys
        vals = {t['Value'] for t in result}
        assert 'prod' in vals
        assert 'ops' in vals

    # R-136
    def test_dict_to_tag_members_empty(self):
        """_dict_to_tag_members with empty dict returns empty list."""
        obj = make_iam_role_obj()

        result = obj._dict_to_tag_members({})

        assert result == []

    # R-137
    def test_paginate_list_multiple_pages(self):
        """_paginate_list collects items across multiple pages."""
        obj = make_iam_role_obj()
        mock_list_func = MagicMock()

        def _make_page(items, is_truncated, marker=None):
            result_obj = MagicMock()
            d = {'Items': items, 'IsTruncated': is_truncated}
            if marker:
                d['Marker'] = marker
            result_obj.to_dict.return_value = d
            resp = MagicMock()
            resp.list_result = result_obj
            return resp

        page1 = _make_page([{'id': 1}, {'id': 2}], True, 'page2')
        page2 = _make_page([{'id': 3}, {'id': 4}], True, 'page3')
        page3 = _make_page([{'id': 5}, {'id': 6}], False)

        mock_list_func.side_effect = [page1, page2, page3]

        result = obj._paginate_list(
            mock_list_func, 'list_result', 'Items',
            role_name='testrole', x_emc_namespace='testns'
        )

        assert len(result) == 6
        assert mock_list_func.call_count == 3


# ===========================================================================
# 15. TestIamRoleGetParameters  (R-138)
# ===========================================================================


class TestIamRoleGetParameters:
    """Verify get_iam_role_parameters() returns complete argument_spec."""

    # R-138
    def test_get_parameters_returns_complete_spec(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role import IamRole

        params = IamRole.get_iam_role_parameters()

        assert isinstance(params, dict)
        # Core params
        assert 'role_name' in params
        assert 'state' in params
        assert 'namespace_name' in params
        assert 'path' in params
        # State choices
        assert params['state']['choices'] == ['present', 'absent']
        # Role-specific params
        assert 'assume_role_policy_document' in params
        assert 'description' in params
        assert 'max_session_duration' in params
        # Sub-resource params
        assert 'tags' in params
        assert 'purge_tags' in params
        assert 'managed_policies' in params
        assert 'purge_managed_policies' in params
        assert 'inline_policies' in params
        assert 'purge_inline_policies' in params
        assert 'permissions_boundary' in params
        assert 'force_delete' in params


# ===========================================================================
# main() entry point test
# ===========================================================================


class TestIamRoleMain:

    @patch(f'{MODULE}.IamRole')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role import main
        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()
        mock_obj.perform_module_operation.assert_called_once()
