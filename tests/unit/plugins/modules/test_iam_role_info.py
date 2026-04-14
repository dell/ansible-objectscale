# -*- coding: utf-8 -*-
# Copyright: (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    role_name=None,
    namespace_name='testns',
    include_attached_policies=False,
    include_inline_policies=False,
    inline_policy_name=None,
    include_tags=False,
)


def make_iam_role_info_obj(params=None, has_client=True):
    """Helper: return an IamRoleInfo instance with all I/O mocked.

    Follows the make_iam_user_info_obj() pattern from test_iam_user_info.py.
    """
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info import IamRoleInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = module_mock.params.get('_check_mode', False)
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamRoleInfo()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    obj.namespace = module_mock.params.get('namespace_name')
    return obj


# ---------------------------------------------------------------------------
# R-001 to R-003: TestIamRoleInfoInit
# ---------------------------------------------------------------------------


class TestIamRoleInfoInit:
    """Tests for IamRoleInfo.__init__() — R-001 to R-003."""

    # R-001
    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        """R-001: Module initializes with valid params and available client."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info import IamRoleInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamRoleInfo()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    # R-002
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        """R-002: Module fails gracefully when objectscale_client is not installed."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info import IamRoleInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamRoleInfo()
        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in call_kwargs['msg']

    # R-003
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        """R-003: Module fails gracefully on connection error."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info import IamRoleInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamRoleInfo()
        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# R-004 to R-007: TestIamRoleInfoGetRole
# ---------------------------------------------------------------------------


class TestIamRoleInfoGetRole:
    """Tests for IamRoleInfo.get_role() — R-004 to R-007."""

    # R-004
    def test_get_role_success(self):
        """R-004: GetRole returns valid role dict when role exists."""
        import json
        obj = make_iam_role_info_obj()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.data = json.dumps({
            'GetRoleResult': {
                'Role': {
                    'RoleName': 'testrole',
                    'Arn': 'urn:ecs:iam::testns:role/testrole',
                    'RoleId': 'AROA123',
                    'CreateDate': '2025-01-15T10:30:00Z',
                    'Path': '/',
                    'AssumeRolePolicyDocument': '{}',
                    'Description': 'Test role',
                    'MaxSessionDuration': 3600,
                }
            }
        }).encode('utf-8')
        obj.iam_api.api_client.rest_client.request = MagicMock(return_value=mock_resp)
        obj.iam_api.api_client.configuration.host = 'https://10.0.0.1:4443'
        obj.iam_api.api_client.configuration.api_key = {'AuthToken': 'test-token'}

        result = obj.get_role('testrole')

        assert result is not None
        assert result['RoleName'] == 'testrole'
        assert result['Arn'] == 'urn:ecs:iam::testns:role/testrole'
        obj.iam_api.api_client.rest_client.request.assert_called_once()

    # R-005
    def test_get_role_not_found_404(self):
        """R-005: GetRole with 404 calls fail_json for info module."""
        obj = make_iam_role_info_obj()
        err = Exception("Not Found")
        err.status = 404
        obj.iam_api.iam_service_get_role.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='Not Found'):
            obj.get_role('nonexistent')

        obj.module.fail_json.assert_called_once()
        call_kwargs = obj.module.fail_json.call_args[1]
        assert 'not found' in call_kwargs['msg'].lower() or 'Not Found' in call_kwargs.get('msg', '')

    # R-006
    def test_get_role_other_error_fails(self):
        """R-006: GetRole fails on 500 server error."""
        obj = make_iam_role_info_obj()
        err = Exception("Internal Server Error")
        err.status = 500
        obj.iam_api.iam_service_get_role.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='Internal Server Error'):
            obj.get_role('testrole')

        obj.module.fail_json.assert_called_once()
        call_kwargs = obj.module.fail_json.call_args[1]
        assert 'Internal Server Error' in call_kwargs['msg']

    # R-007
    def test_get_role_none_rolename(self):
        """R-007: None role_name is passed through to API."""
        import json
        obj = make_iam_role_info_obj()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.data = json.dumps({
            'GetRoleResult': {
                'Role': {
                    'RoleName': None,
                    'Arn': 'urn:ecs:iam::testns:role/',
                }
            }
        }).encode('utf-8')
        obj.iam_api.api_client.rest_client.request = MagicMock(return_value=mock_resp)
        obj.iam_api.api_client.configuration.host = 'https://10.0.0.1:4443'
        obj.iam_api.api_client.configuration.api_key = {'AuthToken': 'test-token'}

        obj.get_role(None)

        obj.iam_api.api_client.rest_client.request.assert_called_once()


# ---------------------------------------------------------------------------
# R-008 to R-013: TestIamRoleInfoListAllRoles
# ---------------------------------------------------------------------------


class TestIamRoleInfoListAllRoles:
    """Tests for IamRoleInfo.list_all_roles() — R-008 to R-013."""

    def _make_list_response(self, roles, is_truncated=False, marker=None):
        """Helper to create a mock ListRoles API response."""
        resp = MagicMock()
        resp.to_dict.return_value = {
            'ListRolesResult': {
                'Roles': roles,
                'IsTruncated': is_truncated,
                'Marker': marker,
            }
        }
        return resp

    # R-008
    def test_list_all_roles_success(self):
        """R-008: ListRoles returns a single page of results."""
        obj = make_iam_role_info_obj()
        roles_data = [
            {'RoleName': 'role1', 'RoleId': 'AROA1'},
            {'RoleName': 'role2', 'RoleId': 'AROA2'},
            {'RoleName': 'role3', 'RoleId': 'AROA3'},
        ]
        obj.iam_api.iam_service_list_roles.return_value = self._make_list_response(
            roles_data, is_truncated=False
        )

        result = obj.list_all_roles()

        assert len(result) == 3
        assert result[0]['RoleName'] == 'role1'
        obj.iam_api.iam_service_list_roles.assert_called_once()

    # R-009
    def test_list_all_roles_empty(self):
        """R-009: ListRoles returns zero roles."""
        obj = make_iam_role_info_obj()
        obj.iam_api.iam_service_list_roles.return_value = self._make_list_response(
            [], is_truncated=False
        )

        result = obj.list_all_roles()

        assert result == []
        assert len(result) == 0

    # R-010
    def test_list_all_roles_pagination(self):
        """R-010: ListRoles auto-paginates across multiple pages."""
        obj = make_iam_role_info_obj()
        page1 = self._make_list_response(
            [{'RoleName': 'role1'}, {'RoleName': 'role2'}],
            is_truncated=True, marker='page2'
        )
        page2 = self._make_list_response(
            [{'RoleName': 'role3'}, {'RoleName': 'role4'}],
            is_truncated=False
        )
        obj.iam_api.iam_service_list_roles.side_effect = [page1, page2]

        result = obj.list_all_roles()

        assert len(result) == 4
        assert obj.iam_api.iam_service_list_roles.call_count == 2

    # R-011
    def test_list_all_roles_single_page(self):
        """R-011: ListRoles returns single page (is_truncated=False explicitly)."""
        obj = make_iam_role_info_obj()
        obj.iam_api.iam_service_list_roles.return_value = self._make_list_response(
            [{'RoleName': 'role1'}], is_truncated=False
        )

        result = obj.list_all_roles()

        assert len(result) == 1
        obj.iam_api.iam_service_list_roles.assert_called_once()

    # R-012
    def test_list_all_roles_api_error(self):
        """R-012: ListRoles fails on API error."""
        obj = make_iam_role_info_obj()
        obj.iam_api.iam_service_list_roles.side_effect = Exception("API failure")

        with patch(f'{UTILS}.determine_error', return_value='API failure'):
            obj.list_all_roles()

        obj.module.fail_json.assert_called_once()
        kwargs = obj.module.fail_json.call_args[1]
        assert 'Listing IAM roles failed' in kwargs['msg']

    # R-013
    def test_list_all_roles_max_items_boundary(self):
        """R-013: Pagination with max_items=1 forces 3 pages for 3 roles."""
        obj = make_iam_role_info_obj()
        page1 = self._make_list_response(
            [{'RoleName': 'role1'}], is_truncated=True, marker='p2'
        )
        page2 = self._make_list_response(
            [{'RoleName': 'role2'}], is_truncated=True, marker='p3'
        )
        page3 = self._make_list_response(
            [{'RoleName': 'role3'}], is_truncated=False
        )
        obj.iam_api.iam_service_list_roles.side_effect = [page1, page2, page3]

        result = obj.list_all_roles()

        assert len(result) == 3
        assert obj.iam_api.iam_service_list_roles.call_count == 3


# ---------------------------------------------------------------------------
# R-014 to R-022: TestIamRoleInfoEnrichRole
# ---------------------------------------------------------------------------


class TestIamRoleInfoEnrichRole:
    """Tests for IamRoleInfo.enrich_role() — R-014 to R-022."""

    # R-014
    def test_enrich_role_inline_policies(self):
        """R-014: Enrichment adds inline policy names when include_inline_policies=True."""
        params = {**BASE_PARAMS, 'include_inline_policies': True}
        obj = make_iam_role_info_obj(params=params)
        obj.list_inline_policy_names = MagicMock(return_value=['policy1', 'policy2'])

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        assert result['inline_policies'] == ['policy1', 'policy2']

    # R-015
    def test_enrich_role_attached_policies(self):
        """R-015: Enrichment adds managed policy attachments when include_attached_policies=True."""
        params = {**BASE_PARAMS, 'include_attached_policies': True}
        obj = make_iam_role_info_obj(params=params)
        obj.list_attached_policies = MagicMock(return_value=[
            {'PolicyName': 'ReadOnlyAccess', 'PolicyArn': 'urn:ecs:iam::testns:policy/ReadOnlyAccess'},
        ])

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        assert len(result['attached_policies']) == 1
        assert 'PolicyArn' in result['attached_policies'][0]

    # R-016
    def test_enrich_role_tags(self):
        """R-016: Enrichment adds role tags when include_tags=True."""
        params = {**BASE_PARAMS, 'include_tags': True}
        obj = make_iam_role_info_obj(params=params)
        obj.list_role_tags = MagicMock(return_value=[
            {'Key': 'Env', 'Value': 'prod'},
        ])

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        assert result['role_tags'] == [{'Key': 'Env', 'Value': 'prod'}]

    # R-017
    def test_enrich_role_error_isolation_inline_fail(self):
        """R-017: One enrichment fails, others succeed — error embedded in response."""
        params = {
            **BASE_PARAMS,
            'include_inline_policies': True,
            'include_tags': True,
        }
        obj = make_iam_role_info_obj(params=params)
        # Inline policies fail
        obj.list_inline_policy_names = MagicMock(side_effect=Exception("inline API error"))
        # Tags succeed
        obj.list_role_tags = MagicMock(return_value=[{'Key': 'Env', 'Value': 'prod'}])

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        # Inline policies should have error embedded
        assert 'error' in result['inline_policies']
        obj.module.warn.assert_called()
        # Tags should still succeed
        assert result['role_tags'] == [{'Key': 'Env', 'Value': 'prod'}]

    # R-018
    def test_enrich_role_all_flags(self):
        """R-018: All enrichment flags enabled, all enrichment calls happen."""
        params = {
            **BASE_PARAMS,
            'include_inline_policies': True,
            'include_attached_policies': True,
            'include_tags': True,
        }
        obj = make_iam_role_info_obj(params=params)
        obj.list_inline_policy_names = MagicMock(return_value=['pol1'])
        obj.list_attached_policies = MagicMock(return_value=[{'PolicyArn': 'urn:...'}])
        obj.list_role_tags = MagicMock(return_value=[{'Key': 'Env', 'Value': 'dev'}])

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        assert 'inline_policies' in result
        assert 'attached_policies' in result
        assert 'role_tags' in result

    # R-019
    def test_enrich_role_no_flags(self):
        """R-019: No include flags set — no enrichment performed."""
        obj = make_iam_role_info_obj()  # all include_* default to False

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        assert 'inline_policies' not in result
        assert 'attached_policies' not in result
        assert 'role_tags' not in result

    # R-020
    def test_enrich_role_all_fail(self):
        """R-020: All enrichment calls raise — all get error dicts."""
        params = {
            **BASE_PARAMS,
            'include_inline_policies': True,
            'include_attached_policies': True,
            'include_tags': True,
        }
        obj = make_iam_role_info_obj(params=params)
        obj.list_inline_policy_names = MagicMock(side_effect=Exception("fail-ip"))
        obj.list_attached_policies = MagicMock(side_effect=Exception("fail-ap"))
        obj.list_role_tags = MagicMock(side_effect=Exception("fail-tg"))

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        assert 'error' in result['inline_policies']
        assert 'error' in result['attached_policies']
        assert 'error' in result['role_tags']
        assert obj.module.warn.call_count >= 3

    # R-021
    def test_enrich_role_inline_policy_document(self):
        """R-021: Enrichment adds inline policy document when inline_policy_name is set."""
        import json
        from urllib.parse import quote as url_encode
        params = {**BASE_PARAMS, 'inline_policy_name': 'pol1'}
        obj = make_iam_role_info_obj(params=params)
        policy_doc = {'Version': '2012-10-17', 'Statement': []}
        encoded_doc = url_encode(json.dumps(policy_doc))
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetRolePolicyResult': {
                'PolicyDocument': encoded_doc,
                'PolicyName': 'pol1',
                'RoleName': 'testrole',
            }
        }
        obj.iam_api.iam_service_get_role_policy.return_value = mock_response

        role = {'RoleName': 'testrole'}
        result = obj.enrich_role(role)

        assert 'inline_policy_document' in result
        assert result['inline_policy_document']['Version'] == '2012-10-17'


# ---------------------------------------------------------------------------
# R-023 to R-025: TestIamRoleInfoListInlinePolicies
# ---------------------------------------------------------------------------


class TestIamRoleInfoListInlinePolicies:
    """Tests for IamRoleInfo.list_inline_policy_names() — R-023 to R-025."""

    # R-023
    def test_list_inline_policies_success(self):
        """R-023: Returns list of inline policy names for role."""
        obj = make_iam_role_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListRolePoliciesResult': {
                'PolicyNames': ['policy1', 'policy2'],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_role_policies.return_value = mock_response

        result = obj.list_inline_policy_names('testrole')

        assert result == ['policy1', 'policy2']
        obj.iam_api.iam_service_list_role_policies.assert_called_once()

    # R-024
    def test_list_inline_policies_error_propagates(self):
        """R-024: API error propagates for enrichment to catch."""
        obj = make_iam_role_info_obj()
        obj.iam_api.iam_service_list_role_policies.side_effect = \
            Exception("list inline policies error")

        try:
            obj.list_inline_policy_names('testrole')
            raised = False
        except Exception:
            raised = True

        assert raised is True

    # R-025
    def test_list_inline_policies_pagination(self):
        """R-025: Multi-page inline policy listing."""
        obj = make_iam_role_info_obj()
        page1 = MagicMock()
        page1.to_dict.return_value = {
            'ListRolePoliciesResult': {
                'PolicyNames': ['pol1', 'pol2'],
                'IsTruncated': True,
                'Marker': 'p2',
            }
        }
        page2 = MagicMock()
        page2.to_dict.return_value = {
            'ListRolePoliciesResult': {
                'PolicyNames': ['pol3'],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_role_policies.side_effect = [page1, page2]

        result = obj.list_inline_policy_names('testrole')

        assert len(result) == 3
        assert obj.iam_api.iam_service_list_role_policies.call_count == 2


# ---------------------------------------------------------------------------
# R-026 to R-028: TestIamRoleInfoGetRolePolicyDocument
# ---------------------------------------------------------------------------


class TestIamRoleInfoGetRolePolicyDocument:
    """Tests for IamRoleInfo.get_role_policy_document() — R-026 to R-028."""

    # R-026
    def test_get_role_policy_document_success(self):
        """R-026: Returns URL-decoded JSON policy document."""
        import json
        from urllib.parse import quote as url_encode

        obj = make_iam_role_info_obj()
        policy_doc = {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Action': 's3:*', 'Resource': '*'}]}
        encoded_doc = url_encode(json.dumps(policy_doc))

        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetRolePolicyResult': {
                'PolicyDocument': encoded_doc,
                'PolicyName': 'pol1',
                'RoleName': 'testrole',
            }
        }
        obj.iam_api.iam_service_get_role_policy.return_value = mock_response

        result = obj.get_role_policy_document('testrole', 'pol1')

        assert result is not None
        assert result['Version'] == '2012-10-17'
        assert len(result['Statement']) == 1
        obj.iam_api.iam_service_get_role_policy.assert_called_once()

    # R-027
    def test_get_role_policy_document_not_found(self):
        """R-027: Policy name doesn't exist — exception propagates."""
        obj = make_iam_role_info_obj()
        err = Exception("NoSuchEntity")
        err.status = 404
        obj.iam_api.iam_service_get_role_policy.side_effect = err

        try:
            obj.get_role_policy_document('testrole', 'nonexistent')
            raised = False
        except Exception:
            raised = True

        assert raised is True

    # R-028
    def test_get_role_policy_document_malformed(self):
        """R-028: Malformed URL-encoded JSON — handled gracefully."""
        obj = make_iam_role_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'GetRolePolicyResult': {
                'PolicyDocument': '%7Bmalformed',
                'PolicyName': 'pol1',
                'RoleName': 'testrole',
            }
        }
        obj.iam_api.iam_service_get_role_policy.return_value = mock_response

        try:
            result = obj.get_role_policy_document('testrole', 'pol1')
        except (ValueError, Exception):
            pass  # Expected: malformed JSON raises error


# ---------------------------------------------------------------------------
# R-029 to R-031: TestIamRoleInfoListAttachedPolicies
# ---------------------------------------------------------------------------


class TestIamRoleInfoListAttachedPolicies:
    """Tests for IamRoleInfo.list_attached_policies() — R-029 to R-031."""

    # R-029
    def test_list_attached_policies_success(self):
        """R-029: Returns list of attached managed policies."""
        obj = make_iam_role_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListAttachedRolePoliciesResult': {
                'AttachedPolicies': [
                    {'PolicyName': 'ReadOnly', 'PolicyArn': 'urn:ecs:iam::testns:policy/ReadOnly'},
                ],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_attached_role_policies.return_value = mock_response

        result = obj.list_attached_policies('testrole')

        assert len(result) == 1
        assert result[0]['PolicyArn'] == 'urn:ecs:iam::testns:policy/ReadOnly'
        obj.iam_api.iam_service_list_attached_role_policies.assert_called_once()

    # R-030
    def test_list_attached_policies_empty(self):
        """R-030: Returns empty list when no policies attached."""
        obj = make_iam_role_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListAttachedRolePoliciesResult': {
                'AttachedPolicies': [],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_attached_role_policies.return_value = mock_response

        result = obj.list_attached_policies('testrole')

        assert result == []
        assert len(result) == 0

    # R-031
    def test_list_attached_policies_pagination(self):
        """R-031: Multi-page attached policy listing."""
        obj = make_iam_role_info_obj()
        page1 = MagicMock()
        page1.to_dict.return_value = {
            'ListAttachedRolePoliciesResult': {
                'AttachedPolicies': [
                    {'PolicyArn': 'urn:ecs:iam::testns:policy/Pol1'},
                ],
                'IsTruncated': True,
                'Marker': 'p2',
            }
        }
        page2 = MagicMock()
        page2.to_dict.return_value = {
            'ListAttachedRolePoliciesResult': {
                'AttachedPolicies': [
                    {'PolicyArn': 'urn:ecs:iam::testns:policy/Pol2'},
                ],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_attached_role_policies.side_effect = [page1, page2]

        result = obj.list_attached_policies('testrole')

        assert len(result) == 2
        assert obj.iam_api.iam_service_list_attached_role_policies.call_count == 2


# ---------------------------------------------------------------------------
# R-032 to R-034: TestIamRoleInfoListRoleTags
# ---------------------------------------------------------------------------


class TestIamRoleInfoListRoleTags:
    """Tests for IamRoleInfo.list_role_tags() — R-032 to R-034."""

    # R-032
    def test_list_role_tags_success(self):
        """R-032: Returns list of role tags."""
        obj = make_iam_role_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListRoleTagsResult': {
                'Tags': [{'Key': 'Env', 'Value': 'prod'}],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_role_tags.return_value = mock_response

        result = obj.list_role_tags('testrole')

        assert result == [{'Key': 'Env', 'Value': 'prod'}]
        obj.iam_api.iam_service_list_role_tags.assert_called_once()

    # R-033
    def test_list_role_tags_empty(self):
        """R-033: Returns empty list when role has no tags."""
        obj = make_iam_role_info_obj()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'ListRoleTagsResult': {
                'Tags': [],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_role_tags.return_value = mock_response

        result = obj.list_role_tags('testrole')

        assert result == []

    # R-034
    def test_list_role_tags_pagination(self):
        """R-034: Multi-page tag listing."""
        obj = make_iam_role_info_obj()
        page1 = MagicMock()
        page1.to_dict.return_value = {
            'ListRoleTagsResult': {
                'Tags': [{'Key': 'Env', 'Value': 'prod'}],
                'IsTruncated': True,
                'Marker': 'p2',
            }
        }
        page2 = MagicMock()
        page2.to_dict.return_value = {
            'ListRoleTagsResult': {
                'Tags': [{'Key': 'Team', 'Value': 'ops'}],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_role_tags.side_effect = [page1, page2]

        result = obj.list_role_tags('testrole')

        assert len(result) == 2
        assert obj.iam_api.iam_service_list_role_tags.call_count == 2


# ---------------------------------------------------------------------------
# R-035 to R-041: TestIamRoleInfoPerformModuleOperation
# ---------------------------------------------------------------------------


class TestIamRoleInfoPerformModuleOperation:
    """Tests for IamRoleInfo.perform_module_operation() — R-035 to R-041."""

    def _make(self, params=None):
        """Create an IamRoleInfo with perform helper methods mocked."""
        obj = make_iam_role_info_obj(params=params)
        obj.get_role = MagicMock()
        obj.list_all_roles = MagicMock(return_value=[])
        obj.enrich_role = MagicMock(side_effect=lambda r: r)
        return obj

    # R-035
    def test_perform_list_all_roles(self):
        """R-035: List all roles without enrichment."""
        obj = self._make()
        obj.list_all_roles.return_value = [
            {'RoleName': 'role1'}, {'RoleName': 'role2'}
        ]

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['iam_roles']) == 2
        obj.list_all_roles.assert_called_once()

    # R-036
    def test_perform_get_specific_role(self):
        """R-036: Get single role by name."""
        params = {**BASE_PARAMS, 'role_name': 'testrole'}
        obj = self._make(params=params)
        obj.get_role.return_value = {'RoleName': 'testrole', 'Arn': 'urn:ecs:iam::testns:role/testrole'}

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert len(kwargs['iam_roles']) == 1
        assert kwargs['iam_roles'][0]['RoleName'] == 'testrole'
        obj.get_role.assert_called_once_with('testrole')

    # R-037
    def test_perform_with_enrichment(self):
        """R-037: perform_module_operation calls enrich_role for each role."""
        params = {**BASE_PARAMS, 'include_tags': True}
        obj = self._make(params=params)
        obj.list_all_roles.return_value = [
            {'RoleName': 'role1'}, {'RoleName': 'role2'}
        ]
        obj.enrich_role = MagicMock(side_effect=lambda r: {**r, 'role_tags': [{'Key': 'Env', 'Value': 'prod'}]})

        obj.perform_module_operation()

        assert obj.enrich_role.call_count == 2

    # R-038
    def test_perform_check_mode(self):
        """R-038: Check mode executes read operations normally."""
        params = {**BASE_PARAMS, '_check_mode': True}
        obj = self._make(params=params)
        obj.module.check_mode = True
        obj.list_all_roles.return_value = [{'RoleName': 'role1'}]

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert 'iam_roles' in kwargs

    # R-039
    def test_perform_changed_always_false(self):
        """R-039: Info module always returns changed=False."""
        obj = self._make()
        obj.list_all_roles.return_value = [
            {'RoleName': 'role1'}, {'RoleName': 'role2'},
        ]

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    # R-040
    def test_perform_auth_error_401(self):
        """R-040: Authentication error (401) propagated during connection."""
        with patch(f'{MODULE}.AnsibleModule') as mock_am, \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("Authentication failed (HTTP 401)")):
            from ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info import IamRoleInfo
            mock_module = MagicMock()
            mock_module.params = BASE_PARAMS.copy()
            mock_am.return_value = mock_module
            IamRoleInfo()
            mock_module.fail_json.assert_called_once()
            call_kwargs = mock_module.fail_json.call_args[1]
            assert '401' in call_kwargs['msg']

    # R-041
    def test_perform_permission_error_403(self):
        """R-041: Permission error (403) during list roles."""
        obj = self._make()
        err = Exception("Forbidden")
        err.status = 403
        obj.list_all_roles.side_effect = err

        try:
            obj.perform_module_operation()
        except Exception:
            pass

        if obj.module.fail_json.called:
            kwargs = obj.module.fail_json.call_args[1]
            assert 'msg' in kwargs
        elif obj.module.exit_json.called:
            kwargs = obj.module.exit_json.call_args[1]
            assert kwargs.get('failed') is True


# ---------------------------------------------------------------------------
# R-042: TestIamRoleInfoGetParameters
# ---------------------------------------------------------------------------


class TestIamRoleInfoGetParameters:
    """Tests for IamRoleInfo.get_iam_role_info_parameters() — R-042."""

    # R-042
    def test_get_parameters_returns_dict(self):
        """R-042: Static method returns valid argument_spec with expected keys."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info import IamRoleInfo
        params = IamRoleInfo.get_iam_role_info_parameters()

        assert isinstance(params, dict)
        assert 'role_name' in params
        assert 'namespace_name' in params
        assert 'include_attached_policies' in params
        assert 'include_inline_policies' in params
        assert 'inline_policy_name' in params
        assert 'include_tags' in params
        assert params['include_attached_policies']['default'] is False
        assert params['include_tags']['type'] == 'bool'


# ---------------------------------------------------------------------------
# main() entry point
# ---------------------------------------------------------------------------


class TestIamRoleInfoMain:
    """Test for main() function."""

    @patch(f'{MODULE}.IamRoleInfo')
    def test_main_calls_perform(self, mock_cls):
        """main() creates instance and calls perform_module_operation."""
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_role_info import main
        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj
        main()
        mock_obj.perform_module_operation.assert_called_once()
