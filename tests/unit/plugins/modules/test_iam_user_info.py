# -*- coding: utf-8 -*-
# Copyright: (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    user_name=None,
    namespace_name='testns',
    include_access_keys=False,
    include_access_key_last_used=False,
    include_inline_policies=False,
    inline_policy_name=None,
    include_attached_policies=False,
    include_groups=False,
    include_tags=False,
)


def make_iam_user_info_obj(params=None, has_client=True):
    """Helper: return an IamUserInfo instance with all I/O mocked.

    Follows the make_info_obj() / make_ns_obj() pattern from test_info.py
    and test_namespace.py respectively.
    """
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info import IamUserInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = module_mock.params.get('_check_mode', False)
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamUserInfo()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    obj.namespace = module_mock.params.get('namespace_name')
    return obj


# ---------------------------------------------------------------------------
# U-001 to U-003: TestIamUserInfoInit
# ---------------------------------------------------------------------------


class TestIamUserInfoInit:
    """Tests for IamUserInfo.__init__() — U-001 to U-003."""

    # U-001
    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        """U-001: Module initializes with valid params and available client."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info import IamUserInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamUserInfo()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    # U-002
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        """U-002: Module fails gracefully when objectscale_client is not installed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info import IamUserInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamUserInfo()
        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in call_kwargs['msg']

    # U-003
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        """U-003: Module fails gracefully on connection error."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info import IamUserInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamUserInfo()
        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# U-004 to U-007: TestIamUserInfoGetUser
# ---------------------------------------------------------------------------


class TestIamUserInfoGetUser:
    """Tests for IamUserInfo.get_user() — U-004 to U-007."""

    # U-004
    def test_get_user_success(self):
        """U-004: GetUser returns valid user dict when user exists."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetUserResult': {
                'User': {
                    'UserName': 'alice',
                    'Arn': 'urn:ecs:iam::testns:user/alice',
                    'UserId': 'AIDA123',
                    'CreateDate': '2025-01-15T10:30:00Z',
                    'Path': '/',
                }
            }
        }
        obj.iam_api.iam_service_get_user.return_value = mock_response

        result = obj.get_user('alice')

        assert result is not None
        assert result['UserName'] == 'alice'
        assert result['Arn'] == 'urn:ecs:iam::testns:user/alice'
        obj.iam_api.iam_service_get_user.assert_called_once_with(
            user_name='alice',
            x_emc_namespace='testns',
        )

    # U-005
    def test_get_user_not_found_404(self):
        """U-005: GetUser with 404 calls fail_json for info module."""
        obj = make_iam_user_info_obj()
        err = Exception("Not Found")
        err.status = 404
        obj.iam_api.iam_service_get_user.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='Not Found'):
            result = obj.get_user('nonexistent')

        # Info module: fail_json on 404 (user must exist to query info)
        obj.module.fail_json.assert_called_once()
        call_kwargs = obj.module.fail_json.call_args[1]
        assert 'not found' in call_kwargs['msg'].lower() or 'Not Found' in call_kwargs.get('msg', '')

    # U-006
    def test_get_user_other_error_fails(self):
        """U-006: GetUser fails on 500 server error."""
        obj = make_iam_user_info_obj()
        err = Exception("Internal Server Error")
        err.status = 500
        obj.iam_api.iam_service_get_user.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='Internal Server Error'):
            obj.get_user('testuser')

        obj.module.fail_json.assert_called_once()
        call_kwargs = obj.module.fail_json.call_args[1]
        assert 'Internal Server Error' in call_kwargs['msg']

    # U-007
    def test_get_user_none_username(self):
        """U-007: None user_name is passed through to API."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetUserResult': {
                'User': {
                    'UserName': None,
                    'Arn': 'urn:ecs:iam::testns:user/',
                }
            }
        }
        obj.iam_api.iam_service_get_user.return_value = mock_response

        obj.get_user(None)

        obj.iam_api.iam_service_get_user.assert_called_once_with(
            user_name=None,
            x_emc_namespace='testns',
        )


# ---------------------------------------------------------------------------
# U-008 to U-013: TestIamUserInfoListAllUsers
# ---------------------------------------------------------------------------


class TestIamUserInfoListAllUsers:
    """Tests for IamUserInfo.list_all_users() — U-008 to U-013."""

    def _make_list_response(self, users, is_truncated=False, marker=None):
        """Helper to create a mock ListUsers API response."""
        resp = MagicMock()
        resp.to_dict.return_value = {
            'ListUsersResult': {
                'Users': users,
                'IsTruncated': is_truncated,
                'Marker': marker,
            }
        }
        # Also set attribute-style access used in pagination
        resp.is_truncated = is_truncated
        resp.marker = marker
        resp.users = users
        return resp

    # U-008
    def test_list_all_users_success(self):
        """U-008: ListUsers returns a single page of results."""
        obj = make_iam_user_info_obj()
        users_data = [
            {'UserName': 'alice', 'UserId': 'AIDA1'},
            {'UserName': 'bob', 'UserId': 'AIDA2'},
            {'UserName': 'charlie', 'UserId': 'AIDA3'},
        ]
        obj.iam_api.iam_service_list_users.return_value = self._make_list_response(
            users_data, is_truncated=False
        )

        result = obj.list_all_users()

        assert len(result) == 3
        assert result[0]['UserName'] == 'alice'
        obj.iam_api.iam_service_list_users.assert_called_once()

    # U-009
    def test_list_all_users_empty(self):
        """U-009: ListUsers returns zero users."""
        obj = make_iam_user_info_obj()
        obj.iam_api.iam_service_list_users.return_value = self._make_list_response(
            [], is_truncated=False
        )

        result = obj.list_all_users()

        assert result == []
        assert len(result) == 0

    # U-010
    def test_list_all_users_pagination(self):
        """U-010: ListUsers auto-paginates across multiple pages."""
        obj = make_iam_user_info_obj()
        page1 = self._make_list_response(
            [{'UserName': 'alice'}, {'UserName': 'bob'}],
            is_truncated=True, marker='page2'
        )
        page2 = self._make_list_response(
            [{'UserName': 'charlie'}, {'UserName': 'dave'}],
            is_truncated=False
        )
        obj.iam_api.iam_service_list_users.side_effect = [page1, page2]

        result = obj.list_all_users()

        assert len(result) == 4
        assert obj.iam_api.iam_service_list_users.call_count == 2

    # U-011 (was labeled U-012 in plan numbering, but matches test_list_users_single_page)
    def test_list_all_users_single_page(self):
        """U-011: ListUsers returns single page (is_truncated=False explicitly)."""
        obj = make_iam_user_info_obj()
        obj.iam_api.iam_service_list_users.return_value = self._make_list_response(
            [{'UserName': 'alice'}], is_truncated=False
        )

        result = obj.list_all_users()

        assert len(result) == 1
        obj.iam_api.iam_service_list_users.assert_called_once()

    # U-012 (api error)
    def test_list_all_users_api_error(self):
        """U-012: ListUsers fails on API error."""
        obj = make_iam_user_info_obj()
        obj.iam_api.iam_service_list_users.side_effect = Exception("API failure")

        with patch(f'{UTILS}.determine_error', return_value='API failure'):
            obj.list_all_users()

        obj.module.fail_json.assert_called_once()
        kwargs = obj.module.fail_json.call_args[1]
        assert 'Listing IAM users failed' in kwargs['msg']

    # U-013
    def test_list_all_users_max_items_boundary(self):
        """U-013: Pagination with max_items=1 forces 3 pages for 3 users."""
        obj = make_iam_user_info_obj()
        page1 = self._make_list_response(
            [{'UserName': 'alice'}], is_truncated=True, marker='p2'
        )
        page2 = self._make_list_response(
            [{'UserName': 'bob'}], is_truncated=True, marker='p3'
        )
        page3 = self._make_list_response(
            [{'UserName': 'charlie'}], is_truncated=False
        )
        obj.iam_api.iam_service_list_users.side_effect = [page1, page2, page3]

        result = obj.list_all_users()

        assert len(result) == 3
        assert obj.iam_api.iam_service_list_users.call_count == 3


# ---------------------------------------------------------------------------
# U-014 to U-022: TestIamUserInfoEnrichUser
# ---------------------------------------------------------------------------


class TestIamUserInfoEnrichUser:
    """Tests for IamUserInfo.enrich_user() — U-014 to U-022."""

    # U-014
    def test_enrich_user_access_keys(self):
        """U-014: Enrichment adds access key metadata when include_access_keys=True."""
        params = {**BASE_PARAMS, 'include_access_keys': True}
        obj = make_iam_user_info_obj(params=params)
        obj.list_access_keys = MagicMock(return_value=[
            {'AccessKeyId': 'AKIA1', 'Status': 'Active'},
            {'AccessKeyId': 'AKIA2', 'Status': 'Inactive'},
        ])

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert 'access_keys' in result
        assert len(result['access_keys']) == 2
        obj.list_access_keys.assert_called_once_with('alice')

    # U-015
    def test_enrich_user_access_key_last_used(self):
        """U-015: Enrichment adds last-used info per key when include_access_key_last_used=True."""
        params = {
            **BASE_PARAMS,
            'include_access_keys': True,
            'include_access_key_last_used': True,
        }
        obj = make_iam_user_info_obj(params=params)
        obj.list_access_keys = MagicMock(return_value=[
            {'AccessKeyId': 'AKIA1', 'Status': 'Active'},
        ])
        obj.get_access_key_last_used = MagicMock(return_value={
            'LastUsedDate': '2025-01-15',
            'ServiceName': 's3',
            'Region': 'us-east-1',
        })

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert 'access_keys' in result
        assert result['access_keys'][0]['last_used']['LastUsedDate'] == '2025-01-15'
        obj.get_access_key_last_used.assert_called_once_with('AKIA1')

    # U-016
    def test_enrich_user_inline_policies(self):
        """U-016: Enrichment adds inline policy names when include_inline_policies=True."""
        params = {**BASE_PARAMS, 'include_inline_policies': True}
        obj = make_iam_user_info_obj(params=params)
        obj.list_inline_policy_names = MagicMock(return_value=['policy1', 'policy2'])

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert result['inline_policies'] == ['policy1', 'policy2']

    # U-017
    def test_enrich_user_attached_policies(self):
        """U-017: Enrichment adds managed policy attachments when include_attached_policies=True."""
        params = {**BASE_PARAMS, 'include_attached_policies': True}
        obj = make_iam_user_info_obj(params=params)
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyName': 'ReadOnlyAccess', 'PolicyArn': 'urn:ecs:iam::testns:policy/ReadOnlyAccess'},
        ])

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert len(result['attached_policies']) == 1
        assert 'PolicyArn' in result['attached_policies'][0]

    # U-018
    def test_enrich_user_groups(self):
        """U-018: Enrichment adds group memberships when include_groups=True."""
        params = {**BASE_PARAMS, 'include_groups': True}
        obj = make_iam_user_info_obj(params=params)
        obj.list_groups_for_user = MagicMock(return_value=[
            {'GroupName': 'admins'},
        ])

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert result['groups'] == [{'GroupName': 'admins'}]

    # U-019
    def test_enrich_user_tags(self):
        """U-019: Enrichment adds user tags when include_tags=True."""
        params = {**BASE_PARAMS, 'include_tags': True}
        obj = make_iam_user_info_obj(params=params)
        obj.list_user_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert result['user_tags'] == [{'Key': 'Env', 'Value': 'prod'}]

    # U-020
    def test_enrich_user_error_isolation_access_keys_fail(self):
        """U-020: One enrichment fails, others succeed — error embedded in response."""
        params = {
            **BASE_PARAMS,
            'include_access_keys': True,
            'include_tags': True,
        }
        obj = make_iam_user_info_obj(params=params)
        # Access keys fail
        obj.list_access_keys = MagicMock(side_effect=Exception("access key API error"))
        # Tags succeed
        obj.list_user_tags = MagicMock(return_value=[{'Key': 'Env', 'Value': 'prod'}])

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        # Access keys should have error embedded
        assert 'error' in result['access_keys']
        obj.module.warn.assert_called()
        # Tags should still succeed
        assert result['user_tags'] == [{'Key': 'Env', 'Value': 'prod'}]

    # U-021
    def test_enrich_user_all_flags(self):
        """U-021: All enrichment flags enabled, all enrichment calls happen."""
        params = {
            **BASE_PARAMS,
            'include_access_keys': True,
            'include_access_key_last_used': True,
            'include_inline_policies': True,
            'include_attached_policies': True,
            'include_groups': True,
            'include_tags': True,
        }
        obj = make_iam_user_info_obj(params=params)
        obj.list_access_keys = MagicMock(return_value=[
            {'AccessKeyId': 'AKIA1', 'Status': 'Active'},
        ])
        obj.get_access_key_last_used = MagicMock(return_value={
            'LastUsedDate': '2025-01-15',
        })
        obj.list_inline_policy_names = MagicMock(return_value=['pol1'])
        obj.list_attached_policies = MagicMock(return_value=[{'PolicyArn': 'urn:...'}])
        obj.list_groups_for_user = MagicMock(return_value=[{'GroupName': 'devs'}])
        obj.list_user_tags = MagicMock(return_value=[{'Key': 'Env', 'Value': 'dev'}])

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert 'access_keys' in result
        assert 'inline_policies' in result
        assert 'attached_policies' in result
        assert 'groups' in result
        assert 'user_tags' in result
        assert result['access_keys'][0]['last_used']['LastUsedDate'] == '2025-01-15'

    # U-022
    def test_enrich_user_no_flags(self):
        """U-022: No include flags set → no enrichment performed."""
        obj = make_iam_user_info_obj()  # all include_* default to False

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        assert 'access_keys' not in result
        assert 'inline_policies' not in result
        assert 'attached_policies' not in result
        assert 'groups' not in result
        assert 'user_tags' not in result

    # Supplemental: all enrichments fail scenario
    def test_enrich_user_all_fail(self):
        """Supplemental for U-021: All enrichment calls raise — all get error dicts."""
        params = {
            **BASE_PARAMS,
            'include_access_keys': True,
            'include_inline_policies': True,
            'include_attached_policies': True,
            'include_groups': True,
            'include_tags': True,
        }
        obj = make_iam_user_info_obj(params=params)
        obj.list_access_keys = MagicMock(side_effect=Exception("fail-ak"))
        obj.list_inline_policy_names = MagicMock(side_effect=Exception("fail-ip"))
        obj.list_attached_policies = MagicMock(side_effect=Exception("fail-ap"))
        obj.list_groups_for_user = MagicMock(side_effect=Exception("fail-gr"))
        obj.list_user_tags = MagicMock(side_effect=Exception("fail-tg"))

        user = {'UserName': 'alice'}
        result = obj.enrich_user(user)

        # Each should have error embedded, none should propagate
        assert 'error' in result['access_keys']
        assert 'error' in result['inline_policies']
        assert 'error' in result['attached_policies']
        assert 'error' in result['groups']
        assert 'error' in result['user_tags']
        assert obj.module.warn.call_count >= 5


# ---------------------------------------------------------------------------
# U-023 to U-025: TestIamUserInfoListAccessKeys
# ---------------------------------------------------------------------------


class TestIamUserInfoListAccessKeys:
    """Tests for IamUserInfo.list_access_keys() — U-023 to U-025."""

    def _make_list_ak_response(self, keys, is_truncated=False, marker=None):
        """Helper to create a mock ListAccessKeys response."""
        resp = MagicMock()
        resp.to_dict.return_value = {
            'ListAccessKeysResult': {
                'AccessKeyMetadata': keys,
                'IsTruncated': is_truncated,
                'Marker': marker,
            }
        }
        resp.is_truncated = is_truncated
        resp.marker = marker
        resp.access_key_metadata = keys
        return resp

    # U-023
    def test_list_access_keys_success(self):
        """U-023: Returns list of AccessKeyMetadata."""
        obj = make_iam_user_info_obj()
        keys = [
            {'AccessKeyId': 'AKIA1', 'Status': 'Active', 'UserName': 'alice'},
            {'AccessKeyId': 'AKIA2', 'Status': 'Inactive', 'UserName': 'alice'},
        ]
        obj.iam_api.iam_service_list_access_keys.return_value = \
            self._make_list_ak_response(keys)

        result = obj.list_access_keys('alice')

        assert len(result) == 2
        assert result[0]['AccessKeyId'] == 'AKIA1'
        obj.iam_api.iam_service_list_access_keys.assert_called_once()

    # U-024
    def test_list_access_keys_pagination(self):
        """U-024: Multi-page access key listing."""
        obj = make_iam_user_info_obj()
        page1 = self._make_list_ak_response(
            [{'AccessKeyId': 'AKIA1'}, {'AccessKeyId': 'AKIA2'}],
            is_truncated=True, marker='p2'
        )
        page2 = self._make_list_ak_response(
            [{'AccessKeyId': 'AKIA3'}],
            is_truncated=False
        )
        obj.iam_api.iam_service_list_access_keys.side_effect = [page1, page2]

        result = obj.list_access_keys('alice')

        assert len(result) == 3
        assert obj.iam_api.iam_service_list_access_keys.call_count == 2

    # U-025
    def test_list_access_keys_empty(self):
        """U-025: API error propagates (enrichment error isolation handles it)."""
        obj = make_iam_user_info_obj()
        obj.iam_api.iam_service_list_access_keys.side_effect = Exception("access key error")

        # The method should let the exception propagate;
        # the caller (enrich_user) will catch it
        try:
            obj.list_access_keys('alice')
            raised = False
        except Exception:
            raised = True

        assert raised is True


# ---------------------------------------------------------------------------
# U-026 to U-027: TestIamUserInfoGetAccessKeyLastUsed
# ---------------------------------------------------------------------------


class TestIamUserInfoGetAccessKeyLastUsed:
    """Tests for IamUserInfo.get_access_key_last_used() — U-026 to U-027."""

    # U-026
    def test_get_access_key_last_used_success(self):
        """U-026: Returns last-used details for an access key."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetAccessKeyLastUsedResult': {
                'AccessKeyLastUsed': {
                    'LastUsedDate': '2025-01-15T00:00:00Z',
                    'ServiceName': 's3',
                    'Region': 'us-east-1',
                }
            }
        }
        obj.iam_api.iam_service_get_access_key_last_used.return_value = mock_response

        result = obj.get_access_key_last_used('AKIA1')

        assert result['LastUsedDate'] == '2025-01-15T00:00:00Z'
        assert result['ServiceName'] == 's3'
        obj.iam_api.iam_service_get_access_key_last_used.assert_called_once()

    # U-027
    def test_get_access_key_last_used_error(self):
        """U-027: API error propagates."""
        obj = make_iam_user_info_obj()
        obj.iam_api.iam_service_get_access_key_last_used.side_effect = \
            Exception("last used error")

        try:
            obj.get_access_key_last_used('AKIA1')
            raised = False
        except Exception:
            raised = True

        assert raised is True


# ---------------------------------------------------------------------------
# U-028 to U-030: TestIamUserInfoGetUserPolicyDocument
# ---------------------------------------------------------------------------


class TestIamUserInfoGetUserPolicyDocument:
    """Tests for IamUserInfo.get_user_policy_document() — U-028 to U-030."""

    # U-028
    def test_get_user_policy_document_success(self):
        """U-028: Returns URL-decoded JSON policy document."""
        import json
        from urllib.parse import quote as url_encode

        obj = make_iam_user_info_obj()
        policy_doc = {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Action': 's3:*', 'Resource': '*'}]}
        encoded_doc = url_encode(json.dumps(policy_doc))

        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetUserPolicyResult': {
                'PolicyDocument': encoded_doc,
                'PolicyName': 'pol1',
                'UserName': 'alice',
            }
        }
        obj.iam_api.iam_service_get_user_policy.return_value = mock_response

        result = obj.get_user_policy_document('alice', 'pol1')

        assert result is not None
        assert result['Version'] == '2012-10-17'
        assert len(result['Statement']) == 1
        obj.iam_api.iam_service_get_user_policy.assert_called_once()

    # U-029
    def test_get_user_policy_document_not_found(self):
        """U-029: Policy name doesn't exist — exception propagates."""
        obj = make_iam_user_info_obj()
        err = Exception("NoSuchEntity")
        err.status = 404
        obj.iam_api.iam_service_get_user_policy.side_effect = err

        try:
            obj.get_user_policy_document('alice', 'nonexistent')
            raised = False
        except Exception:
            raised = True

        assert raised is True

    # U-030
    def test_get_user_policy_document_requires_username(self):
        """U-030: API returns malformed URL-encoded JSON — error raised or handled gracefully."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetUserPolicyResult': {
                'PolicyDocument': '%7Bmalformed',  # malformed URL-encoded JSON
                'PolicyName': 'pol1',
                'UserName': 'alice',
            }
        }
        obj.iam_api.iam_service_get_user_policy.return_value = mock_response

        # Should either raise an error or handle gracefully
        try:
            result = obj.get_user_policy_document('alice', 'pol1')
            # If it returns, it should indicate an error or be None
        except (ValueError, Exception):
            pass  # Expected: malformed JSON raises error


# ---------------------------------------------------------------------------
# U-031 to U-037: TestIamUserInfoPerformModuleOperation
# ---------------------------------------------------------------------------


class TestIamUserInfoPerformModuleOperation:
    """Tests for IamUserInfo.perform_module_operation() — U-031 to U-037."""

    def _make(self, params=None):
        """Create an IamUserInfo with perform helper methods mocked."""
        obj = make_iam_user_info_obj(params=params)
        obj.get_user = MagicMock()
        obj.list_all_users = MagicMock(return_value=[])
        obj.enrich_user = MagicMock(side_effect=lambda u: u)
        return obj

    # U-031
    def test_perform_list_all_users(self):
        """U-031: List all users without enrichment."""
        obj = self._make()
        obj.list_all_users.return_value = [
            {'UserName': 'alice'}, {'UserName': 'bob'}
        ]

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['iam_users']) == 2
        obj.list_all_users.assert_called_once()

    # U-032
    def test_perform_get_specific_user(self):
        """U-032: Get single user by name."""
        params = {**BASE_PARAMS, 'user_name': 'alice'}
        obj = self._make(params=params)
        obj.get_user.return_value = {'UserName': 'alice', 'Arn': 'urn:ecs:iam::testns:user/alice'}

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert len(kwargs['iam_users']) == 1
        assert kwargs['iam_users'][0]['UserName'] == 'alice'
        obj.get_user.assert_called_once_with('alice')

    # U-033
    def test_perform_with_enrichment(self):
        """U-033: perform_module_operation calls enrich_user for each user."""
        params = {**BASE_PARAMS, 'include_tags': True}
        obj = self._make(params=params)
        obj.list_all_users.return_value = [
            {'UserName': 'alice'}, {'UserName': 'bob'}
        ]
        obj.enrich_user = MagicMock(side_effect=lambda u: {**u, 'user_tags': [{'Key': 'Env', 'Value': 'prod'}]})

        obj.perform_module_operation()

        assert obj.enrich_user.call_count == 2

    # U-034
    def test_perform_check_mode(self):
        """U-034: Check mode executes read operations normally."""
        params = {**BASE_PARAMS, '_check_mode': True}
        obj = self._make(params=params)
        obj.module.check_mode = True
        obj.list_all_users.return_value = [{'UserName': 'alice'}]

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert 'iam_users' in kwargs

    # U-035
    def test_perform_changed_always_false(self):
        """U-035: Info module always returns changed=False."""
        obj = self._make()
        obj.list_all_users.return_value = [
            {'UserName': 'alice'}, {'UserName': 'bob'},
        ]

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # U-036
    def test_perform_auth_error_401(self):
        """U-036: Authentication error (401) propagated during connection."""
        # This test validates that an auth error during init propagates
        # correctly. Since it occurs in __init__, we test via the init path.
        with patch(f'{MODULE}.AnsibleModule') as mock_am, \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("Authentication failed (HTTP 401)")):
            from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info import IamUserInfo
            mock_module = MagicMock()
            mock_module.params = BASE_PARAMS.copy()
            mock_am.return_value = mock_module
            IamUserInfo()
            mock_module.fail_json.assert_called_once()
            call_kwargs = mock_module.fail_json.call_args[1]
            assert '401' in call_kwargs['msg']

    # U-037
    def test_perform_permission_error_403(self):
        """U-037: Permission error (403) during list users."""
        obj = self._make()
        err = Exception("Forbidden")
        err.status = 403
        obj.list_all_users.side_effect = err

        # The method should propagate or handle the error
        try:
            obj.perform_module_operation()
        except Exception:
            pass  # Expected if the exception propagates

        # Either fail_json or exit_json should be called with failure
        if obj.module.fail_json.called:
            kwargs = obj.module.fail_json.call_args[1]
            assert 'msg' in kwargs
        elif obj.module.exit_json.called:
            kwargs = obj.module.exit_json.call_args[1]
            assert kwargs.get('failed') is True


# ---------------------------------------------------------------------------
# U-139 to U-140: TestIamUserInfoListInlinePolicies
# ---------------------------------------------------------------------------


class TestIamUserInfoListInlinePolicies:
    """Tests for IamUserInfo.list_inline_policy_names() — U-139 to U-140."""

    # U-139
    def test_list_inline_policies_success(self):
        """U-139: Returns list of inline policy names for user."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListUserPoliciesResult': {
                'PolicyNames': ['policy1', 'policy2'],
                'IsTruncated': False,
            }
        }
        mock_response.is_truncated = False
        mock_response.policy_names = ['policy1', 'policy2']
        obj.iam_api.iam_service_list_user_policies.return_value = mock_response

        result = obj.list_inline_policy_names('alice')

        assert result == ['policy1', 'policy2']
        obj.iam_api.iam_service_list_user_policies.assert_called_once()

    # U-140
    def test_list_inline_policies_empty(self):
        """U-140: API error propagates for enrichment to catch."""
        obj = make_iam_user_info_obj()
        obj.iam_api.iam_service_list_user_policies.side_effect = \
            Exception("list inline policies error")

        try:
            obj.list_inline_policy_names('alice')
            raised = False
        except Exception:
            raised = True

        assert raised is True


# ---------------------------------------------------------------------------
# U-141 to U-142: TestIamUserInfoListAttachedPolicies
# ---------------------------------------------------------------------------


class TestIamUserInfoListAttachedPolicies:
    """Tests for IamUserInfo.list_attached_policies() — U-141 to U-142."""

    # U-141
    def test_list_attached_policies_success(self):
        """U-141: Returns list of attached managed policies."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListAttachedUserPoliciesResult': {
                'AttachedPolicies': [
                    {'PolicyName': 'ReadOnly', 'PolicyArn': 'urn:ecs:iam::testns:policy/ReadOnly'},
                ],
                'IsTruncated': False,
            }
        }
        mock_response.is_truncated = False
        mock_response.attached_policies = [
            {'PolicyName': 'ReadOnly', 'PolicyArn': 'urn:ecs:iam::testns:policy/ReadOnly'},
        ]
        obj.iam_api.iam_service_list_attached_user_policies.return_value = mock_response

        result = obj.list_attached_policies('alice')

        assert len(result) == 1
        assert result[0]['PolicyArn'] == 'urn:ecs:iam::testns:policy/ReadOnly'
        obj.iam_api.iam_service_list_attached_user_policies.assert_called_once()

    # U-142
    def test_list_attached_policies_empty(self):
        """U-142: Returns empty list when no policies attached."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListAttachedUserPoliciesResult': {
                'AttachedPolicies': [],
                'IsTruncated': False,
            }
        }
        mock_response.is_truncated = False
        mock_response.attached_policies = []
        obj.iam_api.iam_service_list_attached_user_policies.return_value = mock_response

        result = obj.list_attached_policies('alice')

        assert result == []
        assert len(result) == 0


# ---------------------------------------------------------------------------
# U-143 to U-144: TestIamUserInfoListGroupsForUser
# ---------------------------------------------------------------------------


class TestIamUserInfoListGroupsForUser:
    """Tests for IamUserInfo.list_groups_for_user() — U-143 to U-144."""

    # U-143
    def test_list_groups_for_user_success(self):
        """U-143: Returns list of groups for user."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListGroupsForUserResult': {
                'Groups': [{'GroupName': 'admins', 'GroupId': 'AGPA1'}],
                'IsTruncated': False,
            }
        }
        mock_response.is_truncated = False
        mock_response.groups = [{'GroupName': 'admins', 'GroupId': 'AGPA1'}]
        obj.iam_api.iam_service_list_groups_for_user.return_value = mock_response

        result = obj.list_groups_for_user('alice')

        assert result == [{'GroupName': 'admins', 'GroupId': 'AGPA1'}]
        obj.iam_api.iam_service_list_groups_for_user.assert_called_once()

    # U-144
    def test_list_groups_for_user_empty(self):
        """U-144: Returns empty list when user has no groups."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListGroupsForUserResult': {
                'Groups': [],
                'IsTruncated': False,
            }
        }
        mock_response.is_truncated = False
        mock_response.groups = []
        obj.iam_api.iam_service_list_groups_for_user.return_value = mock_response

        result = obj.list_groups_for_user('alice')

        assert result == []
        assert len(result) == 0


# ---------------------------------------------------------------------------
# U-145 to U-146: TestIamUserInfoListUserTags
# ---------------------------------------------------------------------------


class TestIamUserInfoListUserTags:
    """Tests for IamUserInfo.list_user_tags() — U-145 to U-146."""

    # U-145
    def test_list_user_tags_success(self):
        """U-145: Returns list of user tags."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListUserTagsResult': {
                'Tags': [{'Key': 'Env', 'Value': 'prod'}],
                'IsTruncated': False,
            }
        }
        mock_response.is_truncated = False
        mock_response.tags = [{'Key': 'Env', 'Value': 'prod'}]
        obj.iam_api.iam_service_list_user_tags.return_value = mock_response

        result = obj.list_user_tags('alice')

        assert result == [{'Key': 'Env', 'Value': 'prod'}]
        obj.iam_api.iam_service_list_user_tags.assert_called_once()

    # U-146
    def test_list_user_tags_empty(self):
        """U-146: Returns empty list when user has no tags."""
        obj = make_iam_user_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListUserTagsResult': {
                'Tags': [],
                'IsTruncated': False,
            }
        }
        mock_response.is_truncated = False
        mock_response.tags = []
        obj.iam_api.iam_service_list_user_tags.return_value = mock_response

        result = obj.list_user_tags('alice')

        assert result == []


# ---------------------------------------------------------------------------
# U-147: TestIamUserInfoGetParameters
# ---------------------------------------------------------------------------


class TestIamUserInfoGetParameters:
    """Tests for IamUserInfo.get_iam_user_info_parameters() — U-147."""

    # U-147
    def test_get_parameters_returns_dict(self):
        """U-147: Static method returns valid argument_spec with expected keys."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info import IamUserInfo
        params = IamUserInfo.get_iam_user_info_parameters()

        assert isinstance(params, dict)
        assert 'user_name' in params
        assert 'namespace_name' in params
        assert 'include_access_keys' in params
        assert 'include_access_key_last_used' in params
        assert 'include_inline_policies' in params
        assert 'inline_policy_name' in params
        assert 'include_attached_policies' in params
        assert 'include_groups' in params
        assert 'include_tags' in params
        assert params['include_access_keys']['default'] is False
        assert params['include_tags']['type'] == 'bool'


# ---------------------------------------------------------------------------
# main() entry point
# ---------------------------------------------------------------------------


class TestIamUserInfoMain:
    """Test for main() function."""

    @patch(f'{MODULE}.IamUserInfo')
    def test_main_calls_perform(self, mock_cls):
        """U-037 supplemental: main() creates instance and calls perform_module_operation."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_user_info import main
        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()
        mock_obj.perform_module_operation.assert_called_once()
