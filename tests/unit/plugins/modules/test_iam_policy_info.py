# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.tests.unit.plugins.module_utils.mock_iam_policy_info_api import (
    BASE_PARAMS,
    SAMPLE_POLICY_DOCUMENT,
    MOCK_POLICY_1,
    MOCK_POLICY_2,
    MOCK_GET_POLICY_RESPONSE,
    MOCK_LIST_POLICIES_RESPONSE,
    MOCK_LIST_POLICIES_PAGE1,
    MOCK_LIST_POLICIES_PAGE2,
    MOCK_POLICY_VERSION_V1,
    MOCK_LIST_VERSIONS_RESPONSE,
)

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'


def make_info_obj(params=None):
    """Helper: return an IamPolicyInfo instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_info import IamPolicyInfo

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamPolicyInfo()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    obj.namespace = module_mock.params.get('namespace_name')
    return obj


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestIamPolicyInfoInit:

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_info import IamPolicyInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamPolicyInfo()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_info import IamPolicyInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamPolicyInfo()
        mock_module.fail_json.assert_called_once()
        assert 'objectscale_client' in mock_module.fail_json.call_args[1]['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy_info import IamPolicyInfo
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamPolicyInfo()
        mock_module.fail_json.assert_called_once()
        assert 'conn failed' in mock_module.fail_json.call_args[1]['msg']


# ---------------------------------------------------------------------------
# get_policy
# ---------------------------------------------------------------------------

class TestGetPolicy:

    def test_success(self):
        obj = make_info_obj()
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_GET_POLICY_RESPONSE
        obj.iam_api.iam_service_get_policy.return_value = resp

        result = obj.get_policy('urn:ecs:iam::testns:policy/TestPolicy1')

        assert result is not None
        assert result['PolicyName'] == 'TestPolicy1'
        assert result['Arn'] == 'urn:ecs:iam::testns:policy/TestPolicy1'

    def test_404_calls_fail_json(self):
        obj = make_info_obj()
        err = Exception("not found")
        err.status = 404
        obj.iam_api.iam_service_get_policy.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='not found'):
            obj.get_policy('urn:ecs:iam::testns:policy/Missing')

        obj.module.fail_json.assert_called_once()
        assert 'not found' in obj.module.fail_json.call_args[1]['msg']

    def test_400_calls_fail_json(self):
        obj = make_info_obj()
        err = Exception("bad request")
        err.status = 400
        obj.iam_api.iam_service_get_policy.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='bad request'):
            obj.get_policy('urn:ecs:iam::testns:policy/Bad')

        obj.module.fail_json.assert_called_once()
        assert 'not found' in obj.module.fail_json.call_args[1]['msg']

    def test_500_calls_fail_json(self):
        obj = make_info_obj()
        err = Exception("server error")
        err.status = 500
        obj.iam_api.iam_service_get_policy.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_policy('urn:ecs:iam::testns:policy/TestPolicy1')

        obj.module.fail_json.assert_called_once()
        assert 'server error' in obj.module.fail_json.call_args[1]['msg']


# ---------------------------------------------------------------------------
# list_all_policies
# ---------------------------------------------------------------------------

class TestListAllPolicies:

    def test_list_single_page(self):
        obj = make_info_obj()
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_LIST_POLICIES_RESPONSE
        obj.iam_api.iam_service_list_policies.return_value = resp

        result = obj.list_all_policies()

        assert len(result) == 2
        assert result[0]['PolicyName'] == 'TestPolicy1'
        assert result[1]['PolicyName'] == 'TestPolicy2'

    def test_list_with_pagination(self):
        obj = make_info_obj()
        resp1 = MagicMock()
        resp1.to_dict.return_value = MOCK_LIST_POLICIES_PAGE1
        resp2 = MagicMock()
        resp2.to_dict.return_value = MOCK_LIST_POLICIES_PAGE2
        obj.iam_api.iam_service_list_policies.side_effect = [resp1, resp2]

        result = obj.list_all_policies()

        assert len(result) == 2
        assert result[0]['PolicyName'] == 'TestPolicy1'
        assert result[1]['PolicyName'] == 'TestPolicy2'
        assert obj.iam_api.iam_service_list_policies.call_count == 2

    def test_list_empty(self):
        obj = make_info_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {
            'ListPoliciesResult': {
                'Policies': [],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_policies.return_value = resp

        result = obj.list_all_policies()

        assert result == []

    def test_list_error_calls_fail_json(self):
        obj = make_info_obj()
        obj.iam_api.iam_service_list_policies.side_effect = Exception("list err")

        with patch(f'{UTILS}.determine_error', return_value='list err'):
            obj.list_all_policies()

        obj.module.fail_json.assert_called_once()
        assert 'list err' in obj.module.fail_json.call_args[1]['msg']

    def test_list_with_policy_scope_filter(self):
        params = BASE_PARAMS.copy()
        params['policy_scope'] = 'Local'
        obj = make_info_obj(params=params)
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_LIST_POLICIES_RESPONSE
        obj.iam_api.iam_service_list_policies.return_value = resp

        obj.list_all_policies()

        call_kwargs = obj.iam_api.iam_service_list_policies.call_args[1]
        assert call_kwargs['policy_scope'] == 'Local'

    def test_list_with_only_attached_filter(self):
        params = BASE_PARAMS.copy()
        params['only_attached'] = True
        obj = make_info_obj(params=params)
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_LIST_POLICIES_RESPONSE
        obj.iam_api.iam_service_list_policies.return_value = resp

        obj.list_all_policies()

        call_kwargs = obj.iam_api.iam_service_list_policies.call_args[1]
        assert call_kwargs['only_attached'] is True


# ---------------------------------------------------------------------------
# get_policy_version_document
# ---------------------------------------------------------------------------

class TestGetPolicyVersionDocument:

    def test_success(self):
        obj = make_info_obj()
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_POLICY_VERSION_V1
        obj.iam_api.iam_service_get_policy_version.return_value = resp

        result = obj.get_policy_version_document(
            'urn:ecs:iam::testns:policy/TestPolicy1', 'v1'
        )

        assert isinstance(result, dict)
        assert result['Version'] == '2012-10-17'
        assert result['Statement'][0]['Effect'] == 'Allow'

    def test_url_encoded_document(self):
        """Document returned URL-encoded should be properly decoded."""
        obj = make_info_obj()
        import urllib.parse
        encoded_doc = urllib.parse.quote(SAMPLE_POLICY_DOCUMENT)
        resp = MagicMock()
        resp.to_dict.return_value = {
            'GetPolicyVersionResult': {
                'PolicyVersion': {
                    'Document': encoded_doc,
                    'VersionId': 'v1',
                    'IsDefaultVersion': True,
                }
            }
        }
        obj.iam_api.iam_service_get_policy_version.return_value = resp

        result = obj.get_policy_version_document(
            'urn:ecs:iam::testns:policy/TestPolicy1', 'v1'
        )

        assert isinstance(result, dict)
        assert 's3:GetObject' in result['Statement'][0]['Action']

    def test_non_json_document_returns_string(self):
        """Non-JSON document returns the raw decoded string."""
        obj = make_info_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {
            'GetPolicyVersionResult': {
                'PolicyVersion': {
                    'Document': 'not-json',
                    'VersionId': 'v1',
                }
            }
        }
        obj.iam_api.iam_service_get_policy_version.return_value = resp

        result = obj.get_policy_version_document(
            'urn:ecs:iam::testns:policy/TestPolicy1', 'v1'
        )

        assert result == 'not-json'


# ---------------------------------------------------------------------------
# list_policy_versions
# ---------------------------------------------------------------------------

class TestListPolicyVersions:

    def test_success(self):
        obj = make_info_obj()
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_LIST_VERSIONS_RESPONSE
        obj.iam_api.iam_service_list_policy_versions.return_value = resp

        result = obj.list_policy_versions('urn:ecs:iam::testns:policy/TestPolicy1')

        assert len(result) == 2
        assert result[0]['VersionId'] == 'v1'
        assert result[1]['VersionId'] == 'v2'

    def test_empty_versions(self):
        obj = make_info_obj()
        resp = MagicMock()
        resp.to_dict.return_value = {
            'ListPolicyVersionsResult': {
                'Versions': [],
                'IsTruncated': False,
            }
        }
        obj.iam_api.iam_service_list_policy_versions.return_value = resp

        result = obj.list_policy_versions('urn:ecs:iam::testns:policy/TestPolicy1')

        assert result == []


# ---------------------------------------------------------------------------
# enrich_policy
# ---------------------------------------------------------------------------

class TestEnrichPolicy:

    def test_no_enrichment(self):
        """With default params, no enrichment keys should be added."""
        obj = make_info_obj()
        policy = MOCK_POLICY_1.copy()

        result = obj.enrich_policy(policy)

        assert 'policy_document' not in result
        assert 'versions' not in result

    def test_include_policy_document(self):
        params = BASE_PARAMS.copy()
        params['include_policy_document'] = True
        obj = make_info_obj(params=params)
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_POLICY_VERSION_V1
        obj.iam_api.iam_service_get_policy_version.return_value = resp
        policy = MOCK_POLICY_1.copy()

        result = obj.enrich_policy(policy)

        assert 'policy_document' in result
        assert isinstance(result['policy_document'], dict)
        assert result['policy_document']['Version'] == '2012-10-17'

    def test_include_versions(self):
        params = BASE_PARAMS.copy()
        params['include_versions'] = True
        obj = make_info_obj(params=params)
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_LIST_VERSIONS_RESPONSE
        obj.iam_api.iam_service_list_policy_versions.return_value = resp
        policy = MOCK_POLICY_1.copy()

        result = obj.enrich_policy(policy)

        assert 'versions' in result
        assert len(result['versions']) == 2

    def test_include_both(self):
        params = BASE_PARAMS.copy()
        params['include_policy_document'] = True
        params['include_versions'] = True
        obj = make_info_obj(params=params)
        doc_resp = MagicMock()
        doc_resp.to_dict.return_value = MOCK_POLICY_VERSION_V1
        obj.iam_api.iam_service_get_policy_version.return_value = doc_resp
        ver_resp = MagicMock()
        ver_resp.to_dict.return_value = MOCK_LIST_VERSIONS_RESPONSE
        obj.iam_api.iam_service_list_policy_versions.return_value = ver_resp
        policy = MOCK_POLICY_1.copy()

        result = obj.enrich_policy(policy)

        assert 'policy_document' in result
        assert 'versions' in result

    def test_document_enrichment_error_warns(self):
        params = BASE_PARAMS.copy()
        params['include_policy_document'] = True
        obj = make_info_obj(params=params)
        obj.iam_api.iam_service_get_policy_version.side_effect = Exception("doc err")
        policy = MOCK_POLICY_1.copy()

        result = obj.enrich_policy(policy)

        assert 'error' in result['policy_document']
        obj.module.warn.assert_called_once()

    def test_versions_enrichment_error_warns(self):
        params = BASE_PARAMS.copy()
        params['include_versions'] = True
        obj = make_info_obj(params=params)
        obj.iam_api.iam_service_list_policy_versions.side_effect = Exception("ver err")
        policy = MOCK_POLICY_1.copy()

        result = obj.enrich_policy(policy)

        assert 'error' in result['versions']
        obj.module.warn.assert_called_once()

    def test_no_default_version_id_returns_none(self):
        """If policy has no DefaultVersionId, document should be None."""
        params = BASE_PARAMS.copy()
        params['include_policy_document'] = True
        obj = make_info_obj(params=params)
        policy = MOCK_POLICY_1.copy()
        policy['DefaultVersionId'] = None

        result = obj.enrich_policy(policy)

        assert result['policy_document'] is None


# ---------------------------------------------------------------------------
# _resolve_policy_arn
# ---------------------------------------------------------------------------

class TestResolvePolicyArn:

    def test_arn_takes_precedence(self):
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/ByArn'
        params['policy_name'] = 'ByName'
        obj = make_info_obj(params=params)

        result = obj._resolve_policy_arn()

        assert result == 'urn:ecs:iam::testns:policy/ByArn'

    def test_name_constructs_arn(self):
        params = BASE_PARAMS.copy()
        params['policy_name'] = 'MyPolicy'
        obj = make_info_obj(params=params)

        result = obj._resolve_policy_arn()

        assert result == 'urn:ecs:iam::testns:policy/MyPolicy'

    def test_neither_returns_none(self):
        obj = make_info_obj()

        result = obj._resolve_policy_arn()

        assert result is None


# ---------------------------------------------------------------------------
# perform_module_operation — get single policy
# ---------------------------------------------------------------------------

class TestPerformModuleOperationSingle:

    def test_get_single_by_arn(self):
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy1'
        obj = make_info_obj(params=params)
        obj.get_policy = MagicMock(return_value=MOCK_POLICY_1.copy())

        obj.perform_module_operation()

        obj.get_policy.assert_called_once_with('urn:ecs:iam::testns:policy/TestPolicy1')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['iam_policies']) == 1
        assert kwargs['iam_policies'][0]['PolicyName'] == 'TestPolicy1'

    def test_get_single_by_name(self):
        params = BASE_PARAMS.copy()
        params['policy_name'] = 'TestPolicy1'
        obj = make_info_obj(params=params)
        obj.get_policy = MagicMock(return_value=MOCK_POLICY_1.copy())

        obj.perform_module_operation()

        obj.get_policy.assert_called_once_with('urn:ecs:iam::testns:policy/TestPolicy1')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['iam_policies']) == 1

    def test_get_single_with_enrichment(self):
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy1'
        params['include_policy_document'] = True
        params['include_versions'] = True
        obj = make_info_obj(params=params)
        obj.get_policy = MagicMock(return_value=MOCK_POLICY_1.copy())
        doc_resp = MagicMock()
        doc_resp.to_dict.return_value = MOCK_POLICY_VERSION_V1
        obj.iam_api.iam_service_get_policy_version.return_value = doc_resp
        ver_resp = MagicMock()
        ver_resp.to_dict.return_value = MOCK_LIST_VERSIONS_RESPONSE
        obj.iam_api.iam_service_list_policy_versions.return_value = ver_resp

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        policy = kwargs['iam_policies'][0]
        assert 'policy_document' in policy
        assert 'versions' in policy


# ---------------------------------------------------------------------------
# perform_module_operation — list all policies
# ---------------------------------------------------------------------------

class TestPerformModuleOperationList:

    def test_list_all(self):
        obj = make_info_obj()
        obj.list_all_policies = MagicMock(return_value=[
            MOCK_POLICY_1.copy(), MOCK_POLICY_2.copy()
        ])

        obj.perform_module_operation()

        obj.list_all_policies.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['iam_policies']) == 2

    def test_list_empty_namespace(self):
        obj = make_info_obj()
        obj.list_all_policies = MagicMock(return_value=[])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['iam_policies'] == []

    def test_list_with_enrichment(self):
        params = BASE_PARAMS.copy()
        params['include_versions'] = True
        obj = make_info_obj(params=params)
        obj.list_all_policies = MagicMock(return_value=[MOCK_POLICY_1.copy()])
        ver_resp = MagicMock()
        ver_resp.to_dict.return_value = MOCK_LIST_VERSIONS_RESPONSE
        obj.iam_api.iam_service_list_policy_versions.return_value = ver_resp

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'versions' in kwargs['iam_policies'][0]

    def test_always_returns_changed_false(self):
        """Info modules must always return changed=False."""
        obj = make_info_obj()
        obj.list_all_policies = MagicMock(return_value=[MOCK_POLICY_1.copy()])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
