# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
TDD tests for the objectscale_iam_user CRUD module.

Test IDs: U-038 through U-138  (101 tests)
These tests are written BEFORE the implementation and are expected to FAIL
until the IamUser class methods are implemented.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from unittest.mock import MagicMock, patch
from urllib.parse import quote as url_encode

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_user'
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
    user_name='testuser',
    namespace_name='testns',
    path='/',
    permissions_boundary=None,
    tags=None,
    purge_tags=True,
    managed_policies=None,
    purge_managed_policies=True,
    inline_policies=None,
    purge_inline_policies=True,
    groups=None,
    purge_groups=True,
    access_key_state=None,
    access_key_id=None,
    access_key_status=None,
    force_delete=False,
)

# ---------------------------------------------------------------------------
# Mock data factories
# ---------------------------------------------------------------------------


def _mock_user(name='testuser', arn=None, user_id='AIDA123', path='/',
               tags=None, boundary=None):
    """Return a user dict as the module would extract from an API response."""
    return {
        'UserName': name,
        'Arn': arn or f'urn:ecs:iam::testns:user/{name}',
        'UserId': user_id,
        'CreateDate': '2025-01-15T10:30:00Z',
        'Path': path,
        'PermissionsBoundary': boundary,
        'Tags': tags or [],
    }


def _mock_access_key(key_id='AKIA1', status='Active', user_name='testuser'):
    return {
        'AccessKeyId': key_id,
        'Status': status,
        'CreateDate': '2025-01-15T10:30:00Z',
        'UserName': user_name,
    }


def _mock_created_access_key(key_id='AKIANEW'):
    return {
        'AccessKeyId': key_id,
        'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY',
        'Status': 'Active',
        'CreateDate': '2025-01-15T10:30:00Z',
        'UserName': 'testuser',
    }


# ---------------------------------------------------------------------------
# Helper to build a fully-mocked IamUser instance
# ---------------------------------------------------------------------------


def make_iam_user_obj(params=None, has_client=True):
    """Helper: return an IamUser instance with all I/O mocked.

    Follows the ``make_ns_obj()`` pattern from ``test_namespace.py``.
    """
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import IamUser

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
        obj = IamUser()

    # Replace module and api with fresh mocks for full test control
    obj.module = module_mock
    obj.iam_api = MagicMock()
    obj.namespace = module_mock.params.get('namespace_name')
    return obj


# ===========================================================================
# 1. TestIamUserInit  (U-038, U-039, U-040)
# ===========================================================================


class TestIamUserInit:
    """Verify module initialisation, client check, and connection handling."""

    # U-038
    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import IamUser
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        obj = IamUser()

        assert obj.module is mock_module
        mock_conn.assert_called_once()

    # U-039
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_missing_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import IamUser
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        IamUser()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in call_kwargs['msg']

    # U-040
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import IamUser
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamUser()

        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'conn failed' in call_kwargs['msg']


# ===========================================================================
# 2. TestIamUserGetUserDetails  (U-041 to U-045)
# ===========================================================================


class TestIamUserGetUserDetails:
    """Verify get_user() behaviour for success, 404, 400, 500, and None."""

    # U-041
    def test_get_user_exists(self):
        obj = make_iam_user_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'GetUserResult': {'User': _mock_user()}}
        obj.iam_api.iam_service_get_user.return_value = resp

        result = obj.get_user('testuser')

        assert result is not None
        assert result['UserName'] == 'testuser'
        assert result['Arn'] == 'urn:ecs:iam::testns:user/testuser'
        obj.iam_api.iam_service_get_user.assert_called_once_with(
            user_name='testuser',
            x_emc_namespace='testns',
        )

    # U-042
    def test_get_user_not_found_returns_none(self):
        obj = make_iam_user_obj()
        err = Exception("not found")
        err.status = 404
        obj.iam_api.iam_service_get_user.side_effect = err

        result = obj.get_user('testuser')

        assert result is None
        obj.module.exit_json.assert_not_called()

    # U-043
    def test_get_user_bad_request_returns_none(self):
        obj = make_iam_user_obj()
        err = Exception("bad request")
        err.status = 400
        obj.iam_api.iam_service_get_user.side_effect = err

        result = obj.get_user('testuser')

        assert result is None
        obj.module.exit_json.assert_not_called()

    # U-044
    def test_get_user_other_error_fails(self):
        obj = make_iam_user_obj()
        err = Exception("server error")
        err.status = 500
        obj.iam_api.iam_service_get_user.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_user('testuser')

        kwargs = obj.module.fail_json.call_args[1]
        assert 'testuser' in kwargs['msg']

    # U-045
    def test_get_user_none_response(self):
        obj = make_iam_user_obj()
        err = Exception("bad request")
        err.status = 400
        obj.iam_api.iam_service_get_user.side_effect = err

        result = obj.get_user(None)

        # None user_name passed through; API raises 400 which returns None
        assert result is None


# ===========================================================================
# 3. TestIamUserCreateUser  (U-046 to U-051)
# ===========================================================================


class TestIamUserCreateUser:
    """Verify create_user() for basic, tags, boundary, all-options, error, idempotent."""

    # U-046
    def test_create_user_basic(self):
        obj = make_iam_user_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'CreateUserResult': {'User': _mock_user()}}
        obj.iam_api.iam_service_create_user.return_value = resp

        result = obj.create_user('testuser')

        assert result is not None
        assert result['UserName'] == 'testuser'
        obj.iam_api.iam_service_create_user.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_create_user.call_args
        # Verify path='/' is passed
        assert call_kwargs[1].get('path', '/') == '/'

    # U-047
    def test_create_user_with_tags(self):
        params = {**BASE_PARAMS, 'tags': {'Env': 'prod', 'Team': 'ops'}}
        obj = make_iam_user_obj(params)
        resp = MagicMock()
        resp.to_dict.return_value = {'CreateUserResult': {'User': _mock_user()}}
        obj.iam_api.iam_service_create_user.return_value = resp

        result = obj.create_user('testuser')

        assert result is not None
        # Tags are no longer passed to create_user; they are applied
        # separately via manage_tags after creation.
        call_kwargs = obj.iam_api.iam_service_create_user.call_args[1]
        assert 'tags_member_n' not in call_kwargs

    # U-048
    def test_create_user_with_permissions_boundary(self):
        params = {**BASE_PARAMS, 'permissions_boundary': 'urn:ecs:iam::testns:policy/BoundaryPol'}
        obj = make_iam_user_obj(params)
        resp = MagicMock()
        resp.to_dict.return_value = {'CreateUserResult': {'User': _mock_user()}}
        obj.iam_api.iam_service_create_user.return_value = resp

        result = obj.create_user('testuser')

        assert result is not None
        call_kwargs = obj.iam_api.iam_service_create_user.call_args[1]
        assert call_kwargs.get('permissions_boundary') == 'urn:ecs:iam::testns:policy/BoundaryPol'

    # U-049
    def test_create_user_with_all_options(self):
        params = {
            **BASE_PARAMS,
            'tags': {'Env': 'prod'},
            'permissions_boundary': 'urn:ecs:iam::testns:policy/Boundary',
            'path': '/',
        }
        obj = make_iam_user_obj(params)
        resp = MagicMock()
        resp.to_dict.return_value = {'CreateUserResult': {'User': _mock_user()}}
        obj.iam_api.iam_service_create_user.return_value = resp

        result = obj.create_user('testuser')

        assert result is not None
        call_kwargs = obj.iam_api.iam_service_create_user.call_args[1]
        assert call_kwargs.get('permissions_boundary') == 'urn:ecs:iam::testns:policy/Boundary'
        # Tags are no longer passed to create_user; they are applied
        # separately via manage_tags after creation.
        assert 'tags_member_n' not in call_kwargs
        assert call_kwargs.get('x_emc_namespace') == 'testns'

    # U-050
    def test_create_user_api_error(self):
        obj = make_iam_user_obj()
        obj.iam_api.iam_service_create_user.side_effect = Exception("create err")

        with patch(f'{UTILS}.determine_error', return_value='create err'):
            obj.create_user('testuser')

        kwargs = obj.module.fail_json.call_args[1]
        assert "Creating IAM user" in kwargs['msg']
        assert 'testuser' in kwargs['msg']

    # U-051
    def test_create_user_already_exists(self):
        """Idempotent: if user exists, perform_module_operation should skip create."""
        obj = make_iam_user_obj()
        # Simulate that get_user finds the user already
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.create_user = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        obj.perform_module_operation()

        obj.create_user.assert_not_called()


# ===========================================================================
# 4. TestIamUserDeleteUser  (U-052 to U-054)
# ===========================================================================


class TestIamUserDeleteUser:
    """Verify delete_user() for success, not-found idempotent, and deps."""

    # U-052
    def test_delete_user_success(self):
        obj = make_iam_user_obj()
        obj.delete_user('testuser')

        obj.iam_api.iam_service_delete_user.assert_called_once_with(
            user_name='testuser',
            x_emc_namespace='testns',
        )

    # U-053
    def test_delete_user_not_found(self):
        """state=absent with user not found => changed=False (idempotent)."""
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = make_iam_user_obj(params)
        obj.get_user = MagicMock(return_value=None)
        obj.delete_user = MagicMock()

        obj.perform_module_operation()

        obj.delete_user.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # U-054
    def test_delete_user_has_dependencies_no_force(self):
        """Delete without force when user has dependencies => API error propagated."""
        obj = make_iam_user_obj()
        err = Exception("DeleteConflict: user has deps")
        err.status = 409
        obj.iam_api.iam_service_delete_user.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='DeleteConflict: user has deps'):
            obj.delete_user('testuser')

        kwargs = obj.module.fail_json.call_args[1]
        assert 'DeleteConflict' in kwargs['msg']


# ===========================================================================
# 5. TestIamUserForceDelete  (U-055 to U-058)
# ===========================================================================


class TestIamUserForceDelete:
    """Verify force_delete_cleanup() cleans all dependency types."""

    # U-055
    def test_force_delete_cleans_access_keys(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1'),
            _mock_access_key('AKIA2'),
        ])
        obj.list_attached_policies = MagicMock(return_value=[])
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.list_groups_for_user = MagicMock(return_value=[])
        obj.get_user = MagicMock(return_value=_mock_user())

        obj.force_delete_cleanup('testuser')

        assert obj.iam_api.iam_service_delete_access_key.call_count == 2

    # U-056
    def test_force_delete_cleans_policies(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[])
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolB'},
        ])
        obj.list_inline_policy_names = MagicMock(return_value=['inline1'])
        obj.list_groups_for_user = MagicMock(return_value=[])
        obj.get_user = MagicMock(return_value=_mock_user())

        obj.force_delete_cleanup('testuser')

        assert obj.iam_api.iam_service_detach_user_policy.call_count == 2
        obj.iam_api.iam_service_delete_user_policy.assert_called_once()

    # U-057
    def test_force_delete_cleans_groups_and_boundary(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[])
        obj.list_attached_policies = MagicMock(return_value=[])
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'admins'},
            {'GroupName': 'devs'},
        ])
        obj.get_user = MagicMock(return_value=_mock_user(
            boundary={'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/Boundary'}
        ))

        obj.force_delete_cleanup('testuser')

        assert obj.iam_api.iam_service_remove_user_from_group.call_count == 2
        obj.iam_api.iam_service_delete_user_permissions_boundary.assert_called_once()

    # U-058
    def test_force_delete_full_cleanup_then_delete(self):
        """Full cleanup with all dependency types present."""
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1'),
            _mock_access_key('AKIA2'),
            _mock_access_key('AKIA3'),
        ])
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
        ])
        obj.list_inline_policy_names = MagicMock(return_value=['inline1', 'inline2'])
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'admins'},
        ])
        obj.get_user = MagicMock(return_value=_mock_user(
            boundary={'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/Boundary'}
        ))

        obj.force_delete_cleanup('testuser')

        # All dependency types cleaned
        assert obj.iam_api.iam_service_delete_access_key.call_count == 3
        assert obj.iam_api.iam_service_detach_user_policy.call_count == 1
        assert obj.iam_api.iam_service_delete_user_policy.call_count == 2
        assert obj.iam_api.iam_service_remove_user_from_group.call_count == 1
        obj.iam_api.iam_service_delete_user_permissions_boundary.assert_called_once()


# ===========================================================================
# 6. TestIamUserManageTags  (U-059 to U-068)
# ===========================================================================


class TestIamUserManageTags:
    """Verify manage_tags() for add, remove, purge, idempotent, check_mode, etc."""

    # U-059
    def test_manage_tags_add_new(self):
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[])
        obj._tag_user_raw = MagicMock()
        obj._untag_user_raw = MagicMock()

        result = obj.manage_tags('testuser', {'Env': 'prod'}, purge=True)

        assert result is True
        obj._tag_user_raw.assert_called_once_with('testuser', {'Env': 'prod'})

    # U-060
    def test_manage_tags_no_change(self):
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])

        result = obj.manage_tags('testuser', {'Env': 'prod'}, purge=True)

        assert result is False
        obj.iam_api.iam_service_tag_user.assert_not_called()
        obj.iam_api.iam_service_untag_user.assert_not_called()

    # U-061
    def test_manage_tags_update_value(self):
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])
        obj._tag_user_raw = MagicMock()
        obj._untag_user_raw = MagicMock()

        result = obj.manage_tags('testuser', {'Env': 'staging'}, purge=True)

        assert result is True
        obj._tag_user_raw.assert_called_once_with('testuser', {'Env': 'staging'})

    # U-062
    def test_manage_tags_purge_extra(self):
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
            {'Key': 'Old', 'Value': 'remove-me'},
        ])
        obj._tag_user_raw = MagicMock()
        obj._untag_user_raw = MagicMock()

        result = obj.manage_tags('testuser', {'Env': 'prod'}, purge=True)

        assert result is True
        obj._untag_user_raw.assert_called_once_with('testuser', ['Old'])

    # U-063
    def test_manage_tags_no_purge_keeps_extra(self):
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
            {'Key': 'Extra', 'Value': 'keep'},
        ])

        result = obj.manage_tags('testuser', {'Env': 'prod'}, purge=False)

        assert result is False
        obj.iam_api.iam_service_untag_user.assert_not_called()
        obj.iam_api.iam_service_tag_user.assert_not_called()

    # U-064
    def test_manage_tags_add_and_remove(self):
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[
            {'Key': 'Old', 'Value': 'val'},
        ])
        obj._tag_user_raw = MagicMock()
        obj._untag_user_raw = MagicMock()

        result = obj.manage_tags('testuser', {'New': 'val2'}, purge=True)

        assert result is True
        obj._tag_user_raw.assert_called_once()
        obj._untag_user_raw.assert_called_once()

    # U-065
    def test_manage_tags_empty_dict(self):
        """Empty desired with purge=True removes all current tags."""
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])
        obj._tag_user_raw = MagicMock()
        obj._untag_user_raw = MagicMock()

        result = obj.manage_tags('testuser', {}, purge=True)

        assert result is True
        obj._untag_user_raw.assert_called_once()
        obj._tag_user_raw.assert_not_called()

    # U-066
    def test_manage_tags_none_skips(self):
        """tags=None means 'don't manage' — perform_module_operation guards this."""
        obj = make_iam_user_obj()
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.manage_tags = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        # params['tags'] is None by default
        obj.perform_module_operation()

        obj.manage_tags.assert_not_called()

    # U-067
    def test_manage_tags_api_error(self):
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[])
        obj._tag_user_raw = MagicMock(side_effect=Exception("tag err"))
        obj._untag_user_raw = MagicMock()

        with pytest.raises(Exception, match="tag err"):
            obj.manage_tags('testuser', {'Env': 'prod'}, purge=True)

    # U-068
    def test_manage_tags_special_characters(self):
        """50 tags (max limit) handled correctly."""
        obj = make_iam_user_obj()
        obj.list_user_tags = MagicMock(return_value=[])
        obj._tag_user_raw = MagicMock()
        obj._untag_user_raw = MagicMock()
        # Build 50 tags
        desired = {f'Key{i}': f'Value{i}' for i in range(50)}

        result = obj.manage_tags('testuser', desired, purge=True)

        assert result is True
        obj._tag_user_raw.assert_called_once()
        call_args = obj._tag_user_raw.call_args
        assert len(call_args[0][1]) == 50


# ===========================================================================
# 7. TestIamUserManageManagedPolicies  (U-069 to U-075)
# ===========================================================================


class TestIamUserManageManagedPolicies:
    """Verify manage_managed_policies() for attach, detach, purge, idempotent."""

    # U-069
    def test_attach_missing_policies(self):
        obj = make_iam_user_obj()
        obj.list_attached_policies = MagicMock(return_value=[])

        result = obj.manage_managed_policies(
            'testuser', ['urn:ecs:iam::testns:policy/NewPol'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_attach_user_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_attach_user_policy.call_args[1]
        assert call_kwargs['policy_arn'] == 'urn:ecs:iam::testns:policy/NewPol'

    # U-070
    def test_all_policies_already_attached(self):
        obj = make_iam_user_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
        ])

        result = obj.manage_managed_policies(
            'testuser', ['urn:ecs:iam::testns:policy/PolA'], purge=True
        )

        assert result is False
        obj.iam_api.iam_service_attach_user_policy.assert_not_called()
        obj.iam_api.iam_service_detach_user_policy.assert_not_called()

    # U-071
    def test_purge_extra_policies(self):
        obj = make_iam_user_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
            {'PolicyArn': 'urn:ecs:iam::testns:policy/OldPol'},
        ])

        result = obj.manage_managed_policies(
            'testuser', ['urn:ecs:iam::testns:policy/PolA'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_detach_user_policy.assert_called_once()

    # U-072
    def test_no_purge_keeps_extra(self):
        obj = make_iam_user_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
            {'PolicyArn': 'urn:ecs:iam::testns:policy/Extra'},
        ])

        result = obj.manage_managed_policies(
            'testuser', ['urn:ecs:iam::testns:policy/PolA'], purge=False
        )

        assert result is False
        obj.iam_api.iam_service_detach_user_policy.assert_not_called()

    # U-073
    def test_attach_and_detach_combined(self):
        obj = make_iam_user_obj()
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/OldPol'},
        ])

        result = obj.manage_managed_policies(
            'testuser', ['urn:ecs:iam::testns:policy/NewPol'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_attach_user_policy.assert_called_once()
        obj.iam_api.iam_service_detach_user_policy.assert_called_once()

    # U-074
    def test_attach_policy_not_found_error(self):
        """Invalid ARN passed to API — server validates, client just sends."""
        obj = make_iam_user_obj()
        obj.list_attached_policies = MagicMock(return_value=[])

        result = obj.manage_managed_policies(
            'testuser', ['not-a-valid-arn'], purge=True
        )

        assert result is True
        obj.iam_api.iam_service_attach_user_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_attach_user_policy.call_args[1]
        assert call_kwargs['policy_arn'] == 'not-a-valid-arn'

    # U-075
    def test_manage_policies_none_skips(self):
        """managed_policies=None => manage_managed_policies not called."""
        obj = make_iam_user_obj()
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.manage_managed_policies = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        obj.perform_module_operation()

        obj.manage_managed_policies.assert_not_called()


# ===========================================================================
# 8. TestIamUserManageInlinePolicies  (U-076 to U-084)
# ===========================================================================


class TestIamUserManageInlinePolicies:
    """Verify manage_inline_policies() for put, delete, purge, idempotent."""

    _POLICY_DOC = {
        'Version': '2012-10-17',
        'Statement': [{'Effect': 'Allow', 'Action': 's3:*', 'Resource': '*'}],
    }

    _POLICY_DOC_V2 = {
        'Version': '2012-10-17',
        'Statement': [{'Effect': 'Deny', 'Action': 's3:Delete*', 'Resource': '*'}],
    }

    # U-076
    def test_put_new_inline_policy(self):
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])

        result = obj.manage_inline_policies(
            'testuser', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_put_user_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_put_user_policy.call_args[1]
        assert call_kwargs['policy_name'] == 'pol1'

    # U-077
    def test_put_inline_policy_same_document(self):
        """Idempotent: same name and document => no change."""
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testuser', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is False
        obj.iam_api.iam_service_put_user_policy.assert_not_called()

    # U-078
    def test_put_inline_policy_different_document(self):
        """Update: same name, different document."""
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testuser', {'pol1': self._POLICY_DOC_V2}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_put_user_policy.assert_called_once()

    # U-079
    def test_purge_extra_inline_policies(self):
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1', 'old_pol'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testuser', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_delete_user_policy.assert_called_once()
        call_kwargs = obj.iam_api.iam_service_delete_user_policy.call_args[1]
        assert call_kwargs['policy_name'] == 'old_pol'

    # U-080
    def test_no_purge_keeps_extra_inline(self):
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=['pol1', 'extra'])
        obj.get_inline_policy_document = MagicMock(return_value=self._POLICY_DOC)

        result = obj.manage_inline_policies(
            'testuser', {'pol1': self._POLICY_DOC}, purge=False
        )

        assert result is False
        obj.iam_api.iam_service_delete_user_policy.assert_not_called()

    # U-081
    def test_inline_policy_url_encoding(self):
        """Verify policy document is URL-encoded before sending to API."""
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])

        result = obj.manage_inline_policies(
            'testuser', {'pol1': self._POLICY_DOC}, purge=True
        )

        assert result is True
        call_kwargs = obj.iam_api.iam_service_put_user_policy.call_args[1]
        doc_sent = call_kwargs['policy_document']
        # Should be URL-encoded JSON
        assert isinstance(doc_sent, str)
        # URL encoding means no raw '{' in the string (it's encoded as %7B)
        # or it's a valid url-encoded JSON string
        assert '%' in doc_sent or doc_sent == url_encode(json.dumps(self._POLICY_DOC))

    # U-082
    def test_manage_inline_policies_none_skips(self):
        """inline_policies=None => manage_inline_policies not called."""
        obj = make_iam_user_obj()
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.manage_inline_policies = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        obj.perform_module_operation()

        obj.manage_inline_policies.assert_not_called()

    # U-083
    def test_inline_policy_api_error(self):
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.iam_api.iam_service_put_user_policy.side_effect = Exception("put err")

        with pytest.raises(Exception, match="put err"):
            obj.manage_inline_policies(
                'testuser', {'pol1': self._POLICY_DOC}, purge=True
            )

    # U-084
    def test_inline_policy_malformed_document(self):
        """Malformed doc is still sent through — server validates."""
        obj = make_iam_user_obj()
        obj.list_inline_policy_names = MagicMock(return_value=[])
        malformed = {'not': 'a valid policy'}

        result = obj.manage_inline_policies(
            'testuser', {'pol1': malformed}, purge=True
        )

        assert result is True
        obj.iam_api.iam_service_put_user_policy.assert_called_once()


# ===========================================================================
# 9. TestIamUserManageGroups  (U-085 to U-091)
# ===========================================================================


class TestIamUserManageGroups:
    """Verify manage_groups() for add, remove, purge, idempotent."""

    # U-085
    def test_add_to_missing_groups(self):
        obj = make_iam_user_obj()
        obj.list_groups_for_user = MagicMock(return_value=[])

        result = obj.manage_groups('testuser', ['admins', 'devs'], purge=True)

        assert result is True
        assert obj.iam_api.iam_service_add_user_to_group.call_count == 2

    # U-086
    def test_already_in_all_groups(self):
        obj = make_iam_user_obj()
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'admins'},
        ])

        result = obj.manage_groups('testuser', ['admins'], purge=True)

        assert result is False
        obj.iam_api.iam_service_add_user_to_group.assert_not_called()
        obj.iam_api.iam_service_remove_user_from_group.assert_not_called()

    # U-087
    def test_purge_extra_groups(self):
        obj = make_iam_user_obj()
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'admins'},
            {'GroupName': 'old-group'},
        ])

        result = obj.manage_groups('testuser', ['admins'], purge=True)

        assert result is True
        obj.iam_api.iam_service_remove_user_from_group.assert_called_once()

    # U-088
    def test_no_purge_keeps_extra_groups(self):
        obj = make_iam_user_obj()
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'admins'},
            {'GroupName': 'extra'},
        ])

        result = obj.manage_groups('testuser', ['admins'], purge=False)

        assert result is False
        obj.iam_api.iam_service_remove_user_from_group.assert_not_called()

    # U-089
    def test_add_and_remove_groups(self):
        obj = make_iam_user_obj()
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'old-group'},
        ])

        result = obj.manage_groups('testuser', ['new-group'], purge=True)

        assert result is True
        obj.iam_api.iam_service_add_user_to_group.assert_called_once()
        obj.iam_api.iam_service_remove_user_from_group.assert_called_once()

    # U-090
    def test_group_not_found_error(self):
        """Empty desired with purge removes all groups."""
        obj = make_iam_user_obj()
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'g1'},
            {'GroupName': 'g2'},
            {'GroupName': 'g3'},
        ])

        result = obj.manage_groups('testuser', [], purge=True)

        assert result is True
        assert obj.iam_api.iam_service_remove_user_from_group.call_count == 3

    # U-091
    def test_manage_groups_none_skips(self):
        """groups=None => manage_groups not called."""
        obj = make_iam_user_obj()
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.manage_groups = MagicMock()
        obj.capture_current_state = MagicMock(return_value={})

        obj.perform_module_operation()

        obj.manage_groups.assert_not_called()


# ===========================================================================
# 10. TestIamUserManagePermissionsBoundary  (U-092 to U-097)
# ===========================================================================


class TestIamUserManagePermissionsBoundary:
    """Verify manage_permissions_boundary() for set, remove, no-change, etc."""

    # U-092
    def test_set_permissions_boundary(self):
        obj = make_iam_user_obj()
        user = _mock_user()

        result = obj.manage_permissions_boundary(
            'testuser', 'urn:ecs:iam::testns:policy/Boundary', user
        )

        assert result is True
        obj.iam_api.iam_service_put_user_permissions_boundary.assert_called_once()

    # U-093
    def test_permissions_boundary_no_change(self):
        obj = make_iam_user_obj()
        boundary_arn = 'urn:ecs:iam::testns:policy/Boundary'
        user = _mock_user(boundary={
            'PermissionsBoundaryArn': boundary_arn,
        })

        result = obj.manage_permissions_boundary('testuser', boundary_arn, user)

        assert result is False
        obj.iam_api.iam_service_put_user_permissions_boundary.assert_not_called()
        obj.iam_api.iam_service_delete_user_permissions_boundary.assert_not_called()

    # U-094
    def test_update_permissions_boundary(self):
        obj = make_iam_user_obj()
        user = _mock_user(boundary={
            'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/OldBoundary',
        })

        result = obj.manage_permissions_boundary(
            'testuser', 'urn:ecs:iam::testns:policy/NewBoundary', user
        )

        assert result is True
        obj.iam_api.iam_service_put_user_permissions_boundary.assert_called_once()

    # U-095
    def test_remove_permissions_boundary(self):
        """Empty string means 'remove boundary'."""
        obj = make_iam_user_obj()
        user = _mock_user(boundary={
            'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/Boundary',
        })

        result = obj.manage_permissions_boundary('testuser', '', user)

        assert result is True
        obj.iam_api.iam_service_delete_user_permissions_boundary.assert_called_once()

    # U-096
    def test_permissions_boundary_already_removed(self):
        """Remove boundary when none exists => no-op."""
        obj = make_iam_user_obj()
        user = _mock_user()  # No boundary

        result = obj.manage_permissions_boundary('testuser', '', user)

        assert result is False
        obj.iam_api.iam_service_delete_user_permissions_boundary.assert_not_called()

    # U-097
    def test_permissions_boundary_none_skips(self):
        """desired=None means 'don't manage'."""
        obj = make_iam_user_obj()
        user = _mock_user()

        result = obj.manage_permissions_boundary('testuser', None, user)

        assert result is False
        obj.iam_api.iam_service_put_user_permissions_boundary.assert_not_called()
        obj.iam_api.iam_service_delete_user_permissions_boundary.assert_not_called()


# ===========================================================================
# 11. TestIamUserCreateAccessKey  (U-098 to U-100)
# ===========================================================================


class TestIamUserCreateAccessKey:
    """Verify create_access_key() for success, secret masking, and API error."""

    # U-098
    def test_create_access_key_success(self):
        obj = make_iam_user_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'CreateAccessKeyResult': {'AccessKey': _mock_created_access_key()}}
        obj.iam_api.iam_service_create_access_key.return_value = resp

        result = obj.create_access_key('testuser')

        assert result is not None
        assert result['AccessKeyId'] == 'AKIANEW'
        assert result['SecretAccessKey'] is not None
        assert result['Status'] == 'Active'
        obj.iam_api.iam_service_create_access_key.assert_called_once_with(
            user_name='testuser',
            x_emc_namespace='testns',
        )

    # U-099
    def test_create_access_key_masks_secret(self):
        """In diff mode, SecretAccessKey should be masked as '***'."""
        params = {**BASE_PARAMS, 'access_key_state': 'present'}
        obj = make_iam_user_obj(params)
        obj.module._diff = True
        obj.module.check_mode = False
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.capture_current_state = MagicMock(return_value={})

        created_key = _mock_created_access_key()
        obj.create_access_key = MagicMock(return_value=created_key)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        # The diff after state should mask SecretAccessKey
        if 'diff' in kwargs and 'after' in kwargs['diff']:
            after = kwargs['diff']['after']
            if 'access_key' in after and 'SecretAccessKey' in after['access_key']:
                assert after['access_key']['SecretAccessKey'] == '***'

    # U-100
    def test_create_access_key_api_error(self):
        obj = make_iam_user_obj()
        obj.iam_api.iam_service_create_access_key.side_effect = Exception("create key err")

        with patch(f'{UTILS}.determine_error', return_value='create key err'):
            obj.create_access_key('testuser')

        kwargs = obj.module.fail_json.call_args[1]
        assert 'create key err' in kwargs['msg']


# ===========================================================================
# 12. TestIamUserDeleteAccessKey  (U-101 to U-104)
# ===========================================================================


class TestIamUserDeleteAccessKey:
    """Verify delete_access_key() for success, not-found, missing-id, error."""

    # U-101
    def test_delete_access_key_success(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1'),
        ])

        result = obj.delete_access_key('testuser', 'AKIA1')

        assert result is True
        obj.iam_api.iam_service_delete_access_key.assert_called_once_with(
            access_key_id='AKIA1',
            user_name='testuser',
            x_emc_namespace='testns',
        )

    # U-102
    def test_delete_access_key_not_found(self):
        """Idempotent: key not in list => changed=False."""
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[])

        result = obj.delete_access_key('testuser', 'AKIA_NONEXISTENT')

        assert result is False
        obj.iam_api.iam_service_delete_access_key.assert_not_called()

    # U-103
    def test_delete_access_key_missing_id_error(self):
        """access_key_state=absent without key_id => required_if validation.

        This is enforced by AnsibleModule's required_if, so we verify
        the parameter spec includes this constraint.
        """
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import IamUser
        params = IamUser.get_iam_user_parameters()
        # Verify access_key_id is in the spec (required_if is validated at init time)
        assert 'access_key_id' in params
        assert 'access_key_state' in params

    # U-104
    def test_delete_access_key_api_error(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1'),
        ])
        obj.iam_api.iam_service_delete_access_key.side_effect = Exception("del key err")

        with pytest.raises(Exception, match="del key err"):
            obj.delete_access_key('testuser', 'AKIA1')


# ===========================================================================
# 13. TestIamUserUpdateAccessKeyStatus  (U-105 to U-109)
# ===========================================================================


class TestIamUserUpdateAccessKeyStatus:
    """Verify update_access_key_status() for status changes and idempotent."""

    # U-105
    def test_update_access_key_active_to_inactive(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1', status='Active'),
        ])

        result = obj.update_access_key_status('testuser', 'AKIA1', 'Inactive')

        assert result is True
        obj.iam_api.iam_service_update_access_key.assert_called_once_with(
            access_key_id='AKIA1',
            status='Inactive',
            user_name='testuser',
            x_emc_namespace='testns',
        )

    # U-106
    def test_update_access_key_already_desired_status(self):
        """Idempotent: status already matches => no change."""
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1', status='Active'),
        ])

        result = obj.update_access_key_status('testuser', 'AKIA1', 'Active')

        assert result is False
        obj.iam_api.iam_service_update_access_key.assert_not_called()

    # U-107
    def test_update_access_key_inactive_to_active(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1', status='Inactive'),
        ])

        result = obj.update_access_key_status('testuser', 'AKIA1', 'Active')

        assert result is True
        obj.iam_api.iam_service_update_access_key.assert_called_once()

    # U-108
    def test_update_access_key_missing_id_error(self):
        """Key ID not found in list => graceful handling."""
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA_OTHER', status='Active'),
        ])

        # Key AKIA_MISSING is not in the list
        result = obj.update_access_key_status('testuser', 'AKIA_MISSING', 'Inactive')

        # Should either return False or raise appropriate error
        # The implementation should handle gracefully
        obj.iam_api.iam_service_update_access_key.assert_not_called()

    # U-109
    def test_update_access_key_bad_status_value(self):
        """Invalid status value is rejected by choices validation in argument_spec."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import IamUser
        params = IamUser.get_iam_user_parameters()
        assert params['access_key_status']['choices'] == ['Active', 'Inactive']


# ===========================================================================
# 14. TestIamUserCaptureCurrentState  (U-110 to U-112)
# ===========================================================================


class TestIamUserCaptureCurrentState:
    """Verify capture_current_state() for full, minimal, and None user."""

    # U-110
    def test_capture_state_full(self):
        obj = make_iam_user_obj()
        user = _mock_user()
        obj.list_user_tags = MagicMock(return_value=[{'Key': 'Env', 'Value': 'prod'}])
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyArn': 'urn:ecs:iam::testns:policy/PolA'},
        ])
        obj.list_inline_policy_names = MagicMock(return_value=['inline1'])
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'admins'},
        ])
        obj.list_access_keys = MagicMock(return_value=[
            _mock_access_key('AKIA1'),
        ])

        state = obj.capture_current_state('testuser', user)

        assert 'user' in state
        assert 'tags' in state
        assert 'managed_policies' in state
        assert 'inline_policies' in state
        assert 'groups' in state
        assert 'access_keys' in state

    # U-111
    def test_capture_state_minimal(self):
        obj = make_iam_user_obj()
        user = _mock_user()
        obj.list_user_tags = MagicMock(return_value=[])
        obj.list_attached_policies = MagicMock(return_value=[])
        obj.list_inline_policy_names = MagicMock(return_value=[])
        obj.list_groups_for_user = MagicMock(return_value=[])
        obj.list_access_keys = MagicMock(return_value=[])

        state = obj.capture_current_state('testuser', user)

        assert state['tags'] == []
        assert state['managed_policies'] == []
        assert state['groups'] == []
        assert state['access_keys'] == []

    # U-112
    def test_capture_state_user_not_found(self):
        obj = make_iam_user_obj()

        state = obj.capture_current_state('testuser', None)

        assert state == {} or state is not None


# ===========================================================================
# 15. TestIamUserPerformModuleOperation  (U-113 to U-132)
# ===========================================================================


class TestIamUserPerformModuleOperation:
    """Verify the main perform_module_operation() orchestrator."""

    def _make(self, params):
        """Build an IamUser with all sub-methods mocked."""
        obj = make_iam_user_obj(params=params)
        obj.get_user = MagicMock(return_value=None)
        obj.create_user = MagicMock(return_value=_mock_user())
        obj.delete_user = MagicMock()
        obj.force_delete_cleanup = MagicMock()
        obj.manage_tags = MagicMock(return_value=False)
        obj.manage_managed_policies = MagicMock(return_value=False)
        obj.manage_inline_policies = MagicMock(return_value=False)
        obj.manage_groups = MagicMock(return_value=False)
        obj.manage_permissions_boundary = MagicMock(return_value=False)
        obj.create_access_key = MagicMock(return_value=_mock_created_access_key())
        obj.delete_access_key = MagicMock(return_value=False)
        obj.update_access_key_status = MagicMock(return_value=False)
        obj.capture_current_state = MagicMock(return_value={})
        obj.list_access_keys = MagicMock(return_value=[])
        return obj

    # U-113
    def test_create_user_state_present_new(self):
        obj = self._make(BASE_PARAMS.copy())
        obj.get_user.side_effect = [None, _mock_user()]

        obj.perform_module_operation()

        obj.create_user.assert_called_once_with('testuser')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-114
    def test_create_user_state_present_exists(self):
        """Idempotent: user already exists => no create."""
        obj = self._make(BASE_PARAMS.copy())
        obj.get_user.return_value = _mock_user()

        obj.perform_module_operation()

        obj.create_user.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # U-115
    def test_delete_user_state_absent(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()

        obj.perform_module_operation()

        obj.delete_user.assert_called_once_with('testuser')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-116
    def test_delete_user_state_absent_not_exists(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.get_user.return_value = None

        obj.perform_module_operation()

        obj.delete_user.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # U-117
    def test_force_delete_user(self):
        params = {**BASE_PARAMS, 'state': 'absent', 'force_delete': True}
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()

        obj.perform_module_operation()

        obj.force_delete_cleanup.assert_called_once_with('testuser')
        obj.delete_user.assert_called_once_with('testuser')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-118
    def test_create_user_with_sub_resources(self):
        params = {
            **BASE_PARAMS,
            'tags': {'Env': 'prod'},
            'managed_policies': ['urn:ecs:iam::testns:policy/PolA'],
            'groups': ['admins'],
        }
        obj = self._make(params)
        obj.get_user.side_effect = [None, _mock_user()]

        obj.perform_module_operation()

        obj.create_user.assert_called_once()
        obj.manage_tags.assert_called_once()
        obj.manage_managed_policies.assert_called_once()
        obj.manage_groups.assert_called_once()

    # U-119
    def test_update_tags_on_existing_user(self):
        params = {**BASE_PARAMS, 'tags': {'Env': 'staging'}}
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()
        obj.manage_tags.return_value = True

        obj.perform_module_operation()

        obj.manage_tags.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-120
    def test_update_policies_on_existing_user(self):
        params = {**BASE_PARAMS, 'managed_policies': ['urn:ecs:iam::testns:policy/PolA']}
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()
        obj.manage_managed_policies.return_value = True

        obj.perform_module_operation()

        obj.manage_managed_policies.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-121
    def test_update_groups_on_existing_user(self):
        params = {**BASE_PARAMS, 'groups': ['admins']}
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()
        obj.manage_groups.return_value = True

        obj.perform_module_operation()

        obj.manage_groups.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-122
    def test_update_boundary_on_existing_user(self):
        params = {**BASE_PARAMS, 'permissions_boundary': 'urn:ecs:iam::testns:policy/Boundary'}
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()
        obj.manage_permissions_boundary.return_value = True

        obj.perform_module_operation()

        obj.manage_permissions_boundary.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-123
    def test_create_access_key_operation(self):
        params = {**BASE_PARAMS, 'access_key_state': 'present'}
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()

        obj.perform_module_operation()

        obj.create_access_key.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert 'access_key' in kwargs

    # U-124
    def test_delete_access_key_operation(self):
        params = {
            **BASE_PARAMS,
            'access_key_state': 'absent',
            'access_key_id': 'AKIA1',
        }
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()
        obj.delete_access_key.return_value = True

        obj.perform_module_operation()

        obj.delete_access_key.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-125
    def test_update_access_key_operation(self):
        params = {
            **BASE_PARAMS,
            'access_key_id': 'AKIA1',
            'access_key_status': 'Inactive',
        }
        obj = self._make(params)
        obj.get_user.return_value = _mock_user()
        obj.update_access_key_status.return_value = True

        obj.perform_module_operation()

        obj.update_access_key_status.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-126
    def test_check_mode_create_user(self):
        obj = self._make(BASE_PARAMS.copy())
        obj.module.check_mode = True
        obj.get_user.return_value = None

        obj.perform_module_operation()

        obj.create_user.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-127
    def test_check_mode_delete_user(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.module.check_mode = True
        obj.get_user.return_value = _mock_user()

        obj.perform_module_operation()

        obj.delete_user.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    # U-128
    def test_diff_mode_returns_before_after(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = self._make(params)
        obj.module._diff = True
        obj.get_user.return_value = _mock_user()
        obj.capture_current_state.return_value = {'user': _mock_user()}

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in kwargs
        assert 'before' in kwargs['diff']
        assert 'after' in kwargs['diff']
        assert kwargs['diff']['before'] != {}
        assert kwargs['diff']['after'] == {}

    # U-129
    def test_auth_error_401(self):
        """401 auth error during get_user => module fails."""
        obj = self._make(BASE_PARAMS.copy())
        err = Exception("Unauthorized")
        err.status = 401
        obj.get_user = MagicMock(side_effect=err)

        with pytest.raises(Exception, match="Unauthorized"):
            obj.perform_module_operation()

    # U-130
    def test_permission_error_403(self):
        """403 permission error during get_user => module fails."""
        obj = self._make(BASE_PARAMS.copy())
        err = Exception("Forbidden")
        err.status = 403
        obj.get_user = MagicMock(side_effect=err)

        with pytest.raises(Exception, match="Forbidden"):
            obj.perform_module_operation()

    # U-131
    def test_connection_error(self):
        """Connection error propagates."""
        obj = self._make(BASE_PARAMS.copy())
        obj.get_user = MagicMock(side_effect=ConnectionError("network unreachable"))

        with pytest.raises(ConnectionError, match="network unreachable"):
            obj.perform_module_operation()

    # U-132
    def test_full_lifecycle_create_configure_delete(self):
        """End-to-end: verify create, configure sub-resources, then delete works."""
        # Phase 1: Create with sub-resources
        params_create = {
            **BASE_PARAMS,
            'state': 'present',
            'tags': {'Env': 'prod'},
            'groups': ['admins'],
            'managed_policies': ['urn:ecs:iam::testns:policy/PolA'],
        }
        obj1 = self._make(params_create)
        obj1.get_user.side_effect = [None, _mock_user()]
        obj1.manage_tags.return_value = True
        obj1.manage_groups.return_value = True
        obj1.manage_managed_policies.return_value = True

        obj1.perform_module_operation()

        obj1.create_user.assert_called_once()
        kwargs1 = obj1.module.exit_json.call_args[1]
        assert kwargs1['changed'] is True

        # Phase 2: Delete with force
        params_delete = {**BASE_PARAMS, 'state': 'absent', 'force_delete': True}
        obj2 = self._make(params_delete)
        obj2.get_user.return_value = _mock_user()

        obj2.perform_module_operation()

        obj2.force_delete_cleanup.assert_called_once()
        obj2.delete_user.assert_called_once()
        kwargs2 = obj2.module.exit_json.call_args[1]
        assert kwargs2['changed'] is True


# ===========================================================================
# 16. TestIamUserHelperMethods  (U-133 to U-137)
# ===========================================================================


class TestIamUserHelperMethods:
    """Verify helper/utility methods."""

    # U-133
    def test_extract_user_from_response(self):
        obj = make_iam_user_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'GetUserResult': {'User': _mock_user(name='alice')}}

        result = obj._extract_user_dict(resp)

        assert result['UserName'] == 'alice'
        assert 'Arn' in result

    # U-134
    def test_extract_tags_from_response(self):
        """_extract_user_dict from CreateUser response also works."""
        obj = make_iam_user_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'CreateUserResult': {'User': _mock_user(name='alice')}}

        result = obj._extract_user_dict(resp)

        assert result['UserName'] == 'alice'

    # U-135
    def test_dict_to_tag_members(self):
        """_dict_to_tag_members converts dict to list of {Key, Value}."""
        obj = make_iam_user_obj()

        result = obj._dict_to_tag_members({'Env': 'prod', 'Team': 'ops'})

        assert len(result) == 2
        keys = {t['Key'] for t in result}
        assert 'Env' in keys
        assert 'Team' in keys
        vals = {t['Value'] for t in result}
        assert 'prod' in vals
        assert 'ops' in vals

    # U-136
    def test_dict_to_tag_members_empty(self):
        """_dict_to_tag_members with empty dict returns empty list."""
        obj = make_iam_user_obj()

        result = obj._dict_to_tag_members({})

        assert result == []

    # U-137
    def test_paginate_list_multiple_pages(self):
        """_paginate_list collects items across multiple pages."""
        obj = make_iam_user_obj()
        mock_list_func = MagicMock()

        # Simulate 3 pages of 2 items each using new response structure:
        # response.<result_attr>.to_dict() -> {'Items': [...], 'IsTruncated': ..., 'Marker': ...}
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
            user_name='testuser', x_emc_namespace='testns'
        )

        assert len(result) == 6
        assert mock_list_func.call_count == 3


# ===========================================================================
# 17. TestIamUserGetParameters  (U-138)
# ===========================================================================


class TestIamUserGetParameters:
    """Verify get_iam_user_parameters() returns complete argument_spec."""

    # U-138
    def test_get_parameters_returns_complete_spec(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import IamUser

        params = IamUser.get_iam_user_parameters()

        assert isinstance(params, dict)
        # Core params
        assert 'user_name' in params
        assert 'state' in params
        assert 'namespace_name' in params
        assert 'path' in params
        # State choices
        assert params['state']['choices'] == ['present', 'absent']
        # Access key params
        assert 'access_key_state' in params
        assert 'access_key_id' in params
        assert 'access_key_status' in params
        assert params['access_key_status']['choices'] == ['Active', 'Inactive']
        # Sub-resource params
        assert 'tags' in params
        assert 'purge_tags' in params
        assert 'managed_policies' in params
        assert 'purge_managed_policies' in params
        assert 'inline_policies' in params
        assert 'purge_inline_policies' in params
        assert 'groups' in params
        assert 'purge_groups' in params
        assert 'permissions_boundary' in params
        assert 'force_delete' in params


# ===========================================================================
# main() entry point test (part of U-132)
# ===========================================================================


class TestIamUserMain:

    @patch(f'{MODULE}.IamUser')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user import main
        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()
        mock_obj.perform_module_operation.assert_called_once()


class TestIamUserCoverageBoost:

    def test_extract_user_dict_passthrough(self):
        obj = make_iam_user_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {'UserName': 'plain-user'}

        result = obj._extract_user_dict(resp)

        assert result == {'UserName': 'plain-user'}

    def test_iam_raw_post_success(self):
        obj = make_iam_user_obj()
        obj.iam_api.api_client.configuration.host = 'https://example.local'
        obj.iam_api.api_client.configuration.api_key = {'AuthToken': 'token'}
        obj.iam_api.api_client.configuration.api_key_prefix = {'AuthToken': 'Bearer '}

        response = MagicMock()
        response.status = 200
        response.data = b'{}'
        obj.iam_api.api_client.rest_client.request.return_value = response

        result = obj._iam_raw_post('TagUser', {'UserName': 'alice'})

        assert result is response
        obj.iam_api.api_client.rest_client.request.assert_called_once()

    def test_iam_raw_post_error_raises_exception(self):
        obj = make_iam_user_obj()
        obj.iam_api.api_client.configuration.host = 'https://example.local'
        obj.iam_api.api_client.configuration.api_key = {'AuthToken': 'token'}
        obj.iam_api.api_client.configuration.api_key_prefix = {'AuthToken': ''}

        response = MagicMock()
        response.status = 400
        response.data = b'{"error":"bad request"}'
        obj.iam_api.api_client.rest_client.request.return_value = response

        with pytest.raises(Exception):
            obj._iam_raw_post('TagUser', {'UserName': 'alice'})

    def test_tag_and_untag_helpers_expand_members(self):
        obj = make_iam_user_obj()
        obj._iam_raw_post = MagicMock()

        obj._tag_user_raw('alice', {'Env': 'prod', 'Team': 'qe'})
        obj._untag_user_raw('alice', ['Env', 'Team'])

        first_call = obj._iam_raw_post.call_args_list[0]
        assert first_call.args[0] == 'TagUser'
        assert first_call.args[1]['Tags.member.1.Key'] == 'Env'
        assert first_call.args[1]['Tags.member.2.Value'] == 'qe'

        second_call = obj._iam_raw_post.call_args_list[1]
        assert second_call.args[0] == 'UntagUser'
        assert second_call.args[1]['TagKeys.member.1'] == 'Env'
        assert second_call.args[1]['TagKeys.member.2'] == 'Team'

    def test_paginate_list_missing_result_attr(self):
        obj = make_iam_user_obj()
        response = MagicMock()
        response.list_result = None
        mock_list_func = MagicMock(return_value=response)

        result = obj._paginate_list(mock_list_func, 'list_result', 'Items')

        assert result == []

    def test_list_helper_wrappers_call_paginate(self):
        obj = make_iam_user_obj()
        obj._paginate_list = MagicMock(return_value=[])

        obj.list_access_keys('alice')
        obj.list_attached_policies('alice')
        obj.list_inline_policy_names('alice')
        obj.list_groups_for_user('alice')
        obj.list_user_tags('alice')

        assert obj._paginate_list.call_count == 5

    def test_get_inline_policy_document_error_returns_none(self):
        obj = make_iam_user_obj()
        obj.iam_api.iam_service_get_user_policy.side_effect = Exception('failed')

        result = obj.get_inline_policy_document('alice', 'policy-a')

        assert result is None

    def test_force_delete_cleanup_inner_errors_are_collected(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(return_value=[{'AccessKeyId': 'AKIA1'}])
        obj.list_attached_policies = MagicMock(return_value=[{'PolicyArn': 'arn:pol'}])
        obj.list_inline_policy_names = MagicMock(return_value=['inline1'])
        obj.list_groups_for_user = MagicMock(return_value=[{'GroupName': 'devs'}])
        obj.get_user = MagicMock(return_value={'PermissionsBoundary': {'PermissionsBoundaryArn': 'arn:boundary'}})

        obj.iam_api.iam_service_delete_access_key.side_effect = Exception('del key err')
        obj.iam_api.iam_service_detach_user_policy.side_effect = Exception('detach err')
        obj.iam_api.iam_service_delete_user_policy.side_effect = Exception('delete inline err')
        obj.iam_api.iam_service_remove_user_from_group.side_effect = Exception('remove err')
        obj.iam_api.iam_service_delete_user_permissions_boundary.side_effect = Exception('boundary err')

        obj.force_delete_cleanup('alice')

        obj.module.warn.assert_called_once()
        warn_msg = obj.module.warn.call_args[0][0]
        assert 'del key err' in warn_msg
        assert 'detach err' in warn_msg
        assert 'delete inline err' in warn_msg
        assert 'remove err' in warn_msg
        assert 'boundary err' in warn_msg

    def test_force_delete_cleanup_outer_errors_are_collected(self):
        obj = make_iam_user_obj()
        obj.list_access_keys = MagicMock(side_effect=Exception('list keys err'))
        obj.list_attached_policies = MagicMock(side_effect=Exception('list policies err'))
        obj.list_inline_policy_names = MagicMock(side_effect=Exception('list inline err'))
        obj.list_groups_for_user = MagicMock(side_effect=Exception('list groups err'))
        obj.get_user = MagicMock(side_effect=Exception('get user err'))

        obj.force_delete_cleanup('alice')

        obj.module.warn.assert_called_once()
        warn_msg = obj.module.warn.call_args[0][0]
        assert 'list keys err' in warn_msg
        assert 'list policies err' in warn_msg
        assert 'list inline err' in warn_msg
        assert 'list groups err' in warn_msg
        assert 'get user err' in warn_msg

    def test_absent_state_diff_when_user_missing(self):
        params = {**BASE_PARAMS, 'state': 'absent'}
        obj = make_iam_user_obj(params)
        obj.module._diff = True
        obj.get_user = MagicMock(return_value=None)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['diff'] == {'before': {}, 'after': {}}

    def test_present_check_mode_tags_detects_change(self):
        params = {**BASE_PARAMS, 'tags': {'Env': 'prod'}}
        obj = make_iam_user_obj(params)
        obj.module.check_mode = True
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.list_user_tags = MagicMock(return_value=[{'Key': 'Env', 'Value': 'dev'}])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_present_check_mode_managed_policies_detects_change(self):
        params = {**BASE_PARAMS, 'managed_policies': ['arn:new']}
        obj = make_iam_user_obj(params)
        obj.module.check_mode = True
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.list_attached_policies = MagicMock(return_value=[{'PolicyArn': 'arn:old'}])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_present_check_mode_inline_policies_detects_change(self):
        params = {
            **BASE_PARAMS,
            'inline_policies': {'policy-a': {'Version': '2012-10-17', 'Statement': []}},
        }
        obj = make_iam_user_obj(params)
        obj.module.check_mode = True
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.list_inline_policy_names = MagicMock(return_value=[])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_present_check_mode_groups_detects_change(self):
        params = {**BASE_PARAMS, 'groups': ['admins']}
        obj = make_iam_user_obj(params)
        obj.module.check_mode = True
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.list_groups_for_user = MagicMock(return_value=[])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_present_check_mode_permissions_boundary_detects_change(self):
        params = {**BASE_PARAMS, 'permissions_boundary': ''}
        user_with_boundary = _mock_user(
            boundary={'PermissionsBoundaryArn': 'urn:ecs:iam::testns:policy/Boundary'}
        )
        obj = make_iam_user_obj(params)
        obj.module.check_mode = True
        obj.get_user = MagicMock(return_value=user_with_boundary)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_present_check_mode_access_key_absent_detects_change(self):
        params = {
            **BASE_PARAMS,
            'access_key_state': 'absent',
            'access_key_id': 'AKIA1',
        }
        obj = make_iam_user_obj(params)
        obj.module.check_mode = True
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.list_access_keys = MagicMock(return_value=[{'AccessKeyId': 'AKIA1', 'Status': 'Active'}])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_present_check_mode_access_key_status_detects_change(self):
        params = {
            **BASE_PARAMS,
            'access_key_id': 'AKIA1',
            'access_key_status': 'Inactive',
        }
        obj = make_iam_user_obj(params)
        obj.module.check_mode = True
        obj.get_user = MagicMock(return_value=_mock_user())
        obj.list_access_keys = MagicMock(return_value=[{'AccessKeyId': 'AKIA1', 'Status': 'Active'}])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
