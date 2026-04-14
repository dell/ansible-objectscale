# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.tests.unit.plugins.module_utils.mock_iam_policy_api import (
    BASE_PARAMS,
    SAMPLE_POLICY_DOCUMENT,
    SAMPLE_POLICY_DOCUMENT_V2,
    MOCK_POLICY_DETAILS,
    MOCK_CREATE_POLICY_RESPONSE,
    MOCK_POLICY_VERSION_RESPONSE,
)

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.iam_policy'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'


def make_policy_obj(params=None, has_client=True):
    """Helper: return an IamPolicy instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy import IamPolicy

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.IamApi'):
        obj = IamPolicy()

    obj.module = module_mock
    obj.iam_api = MagicMock()
    return obj


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestIamPolicyInit:

    @patch(f'{MODULE}.IamApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_iam_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy import IamPolicy
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        obj = IamPolicy()
        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy import IamPolicy
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        IamPolicy()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'objectscale_client' in call_kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_failure(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.iam_policy import IamPolicy
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        with patch(f'{MODULE}.utils.get_objectscale_connection',
                   side_effect=Exception("conn failed")):
            IamPolicy()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['failed'] is True
        assert 'conn failed' in call_kwargs['msg']


# ---------------------------------------------------------------------------
# get_policy_details
# ---------------------------------------------------------------------------

class TestGetPolicyDetails:

    def test_success(self):
        obj = make_policy_obj()
        resp = MagicMock()
        resp.to_dict.return_value = MOCK_POLICY_DETAILS
        obj.iam_api.iam_service_get_policy.return_value = resp

        result = obj.get_policy_details('urn:ecs:iam::testns:policy/TestPolicy')

        assert result is not None
        assert result == MOCK_POLICY_DETAILS

    def test_404_returns_none(self):
        obj = make_policy_obj()
        err = Exception("not found")
        err.status = 404
        obj.iam_api.iam_service_get_policy.side_effect = err

        result = obj.get_policy_details('urn:ecs:iam::testns:policy/NonExistent')

        assert result is None

    def test_400_returns_none(self):
        obj = make_policy_obj()
        err = Exception("bad request")
        err.status = 400
        obj.iam_api.iam_service_get_policy.side_effect = err

        result = obj.get_policy_details('urn:ecs:iam::testns:policy/NonExistent')

        assert result is None

    def test_other_exception_calls_exit_json(self):
        obj = make_policy_obj()
        err = Exception("server error")
        err.status = 500
        obj.iam_api.iam_service_get_policy.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_policy_details('urn:ecs:iam::testns:policy/TestPolicy')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'TestPolicy' in kwargs['msg']


# ---------------------------------------------------------------------------
# create_policy
# ---------------------------------------------------------------------------

class TestCreatePolicy:

    def test_success(self):
        obj = make_policy_obj()
        mock_resp = MagicMock()
        mock_resp.to_dict.return_value = MOCK_CREATE_POLICY_RESPONSE
        obj.iam_api.iam_service_create_policy.return_value = mock_resp

        result = obj.create_policy('TestPolicy', SAMPLE_POLICY_DOCUMENT, 'Test', '/')

        assert result is not None
        obj.iam_api.iam_service_create_policy.assert_called_once()

    def test_missing_document_fails(self):
        obj = make_policy_obj()
        obj.create_policy('TestPolicy', None, 'Test', '/')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_missing_name_fails(self):
        obj = make_policy_obj()
        obj.create_policy(None, SAMPLE_POLICY_DOCUMENT, 'Test', '/')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True

    def test_api_error_fails(self):
        obj = make_policy_obj()
        obj.iam_api.iam_service_create_policy.side_effect = Exception("create err")

        with patch(f'{UTILS}.determine_error', return_value='create err'):
            obj.create_policy('TestPolicy', SAMPLE_POLICY_DOCUMENT, 'Test', '/')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# delete_policy
# ---------------------------------------------------------------------------

class TestDeletePolicy:

    def test_success(self):
        obj = make_policy_obj()
        result = obj.delete_policy('urn:ecs:iam::testns:policy/TestPolicy')
        assert result is True
        obj.iam_api.iam_service_delete_policy.assert_called_once()

    def test_api_error_fails(self):
        obj = make_policy_obj()
        obj.iam_api.iam_service_delete_policy.side_effect = Exception("del err")

        with patch(f'{UTILS}.determine_error', return_value='del err'):
            obj.delete_policy('urn:ecs:iam::testns:policy/TestPolicy')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# attach_entity
# ---------------------------------------------------------------------------

class TestAttachEntity:

    def test_attach_user(self):
        obj = make_policy_obj()
        result = obj.attach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'user', 'alice')
        assert result is True
        obj.iam_api.iam_service_attach_user_policy.assert_called_once()

    def test_attach_group(self):
        obj = make_policy_obj()
        result = obj.attach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'group', 'developers')
        assert result is True
        obj.iam_api.iam_service_attach_group_policy.assert_called_once()

    def test_attach_role(self):
        obj = make_policy_obj()
        result = obj.attach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'role', 'myrole')
        assert result is True
        obj.iam_api.iam_service_attach_role_policy.assert_called_once()

    def test_attach_user_api_error(self):
        obj = make_policy_obj()
        obj.iam_api.iam_service_attach_user_policy.side_effect = Exception("attach err")

        with patch(f'{UTILS}.determine_error', return_value='attach err'):
            obj.attach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'user', 'alice')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# detach_entity
# ---------------------------------------------------------------------------

class TestDetachEntity:

    def test_detach_user(self):
        obj = make_policy_obj()
        result = obj.detach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'user', 'alice')
        assert result is True
        obj.iam_api.iam_service_detach_user_policy.assert_called_once()

    def test_detach_group(self):
        obj = make_policy_obj()
        result = obj.detach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'group', 'developers')
        assert result is True
        obj.iam_api.iam_service_detach_group_policy.assert_called_once()

    def test_detach_role(self):
        obj = make_policy_obj()
        result = obj.detach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'role', 'myrole')
        assert result is True
        obj.iam_api.iam_service_detach_role_policy.assert_called_once()

    def test_detach_user_api_error(self):
        obj = make_policy_obj()
        obj.iam_api.iam_service_detach_user_policy.side_effect = Exception("detach err")

        with patch(f'{UTILS}.determine_error', return_value='detach err'):
            obj.detach_entity('urn:ecs:iam::testns:policy/TestPolicy', 'user', 'alice')

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# validate_policy_document
# ---------------------------------------------------------------------------

class TestValidatePolicyDocument:

    def test_valid_json(self):
        obj = make_policy_obj()
        # Should not raise or call fail_json
        obj.validate_policy_document(SAMPLE_POLICY_DOCUMENT)
        obj.module.exit_json.assert_not_called()

    def test_invalid_json(self):
        obj = make_policy_obj()
        obj.validate_policy_document('not-valid-json{')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True
        assert 'JSON' in kwargs['msg'] or 'json' in kwargs['msg']

    def test_empty_string(self):
        obj = make_policy_obj()
        obj.validate_policy_document('')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['failed'] is True


# ---------------------------------------------------------------------------
# is_policy_document_modified
# ---------------------------------------------------------------------------

class TestIsPolicyDocumentModified:

    def test_same_document_returns_false(self):
        obj = make_policy_obj()
        mock_version_resp = MagicMock()
        mock_version_resp.to_dict.return_value = MOCK_POLICY_VERSION_RESPONSE
        obj.iam_api.iam_service_get_policy_version.return_value = mock_version_resp

        current_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        result = obj.is_policy_document_modified(
            'urn:ecs:iam::testns:policy/TestPolicy',
            current_details,
            SAMPLE_POLICY_DOCUMENT
        )

        assert result is False

    def test_different_document_returns_true(self):
        obj = make_policy_obj()
        mock_version_resp = MagicMock()
        mock_version_resp.to_dict.return_value = MOCK_POLICY_VERSION_RESPONSE
        obj.iam_api.iam_service_get_policy_version.return_value = mock_version_resp

        current_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        result = obj.is_policy_document_modified(
            'urn:ecs:iam::testns:policy/TestPolicy',
            current_details,
            SAMPLE_POLICY_DOCUMENT_V2
        )

        assert result is True


# ---------------------------------------------------------------------------
# perform_module_operation — state=present, create
# ---------------------------------------------------------------------------

class TestPerformModuleOperationCreate:

    def test_create_new_policy(self):
        """When policy does not exist, it should be created."""
        obj = make_policy_obj()
        # get_policy_details returns None (not found)
        obj.get_policy_details = MagicMock(return_value=None)
        obj.validate_policy_document = MagicMock()
        create_resp = MOCK_CREATE_POLICY_RESPONSE
        obj.create_policy = MagicMock(return_value=create_resp)

        obj.perform_module_operation()

        obj.create_policy.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_create_check_mode(self):
        """In check mode, create should set changed=True but not call API."""
        obj = make_policy_obj()
        obj.module.check_mode = True
        obj.get_policy_details = MagicMock(return_value=None)
        obj.validate_policy_document = MagicMock()
        obj.create_policy = MagicMock()

        obj.perform_module_operation()

        obj.create_policy.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_create_missing_policy_document(self):
        """policy_document is required to create a new policy."""
        params = BASE_PARAMS.copy()
        params['policy_document'] = None
        obj = make_policy_obj(params=params)
        obj.get_policy_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        fail_calls = [c for c in obj.module.exit_json.call_args_list
                      if c[1].get('failed') is True]
        assert len(fail_calls) >= 1

    def test_create_missing_policy_name(self):
        """policy_name is required to create a new policy."""
        params = BASE_PARAMS.copy()
        params['policy_name'] = None
        params['policy_arn'] = None
        obj = make_policy_obj(params=params)

        obj.perform_module_operation()

        fail_calls = [c for c in obj.module.exit_json.call_args_list
                      if c[1].get('failed') is True]
        assert len(fail_calls) >= 1

    def test_create_empty_policy_name(self):
        """Empty string policy_name should be rejected."""
        params = BASE_PARAMS.copy()
        params['policy_name'] = ''
        obj = make_policy_obj(params=params)

        obj.perform_module_operation()

        fail_calls = [c for c in obj.module.exit_json.call_args_list
                      if c[1].get('failed') is True]
        assert len(fail_calls) >= 1

    def test_create_invalid_json_document(self):
        """Invalid JSON in policy_document should fail."""
        params = BASE_PARAMS.copy()
        params['policy_document'] = 'not-valid-json{'
        obj = make_policy_obj(params=params)
        obj.get_policy_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        # validate_policy_document calls exit_json(failed=True) first;
        # mock does not halt execution so check call_args_list.
        fail_calls = [c for c in obj.module.exit_json.call_args_list
                      if c[1].get('failed') is True]
        assert len(fail_calls) >= 1
        assert 'JSON' in fail_calls[0][1]['msg'] or 'json' in fail_calls[0][1]['msg']

    def test_create_empty_policy_document(self):
        """Empty string policy_document should fail."""
        params = BASE_PARAMS.copy()
        params['policy_document'] = ''
        obj = make_policy_obj(params=params)
        obj.get_policy_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        fail_calls = [c for c in obj.module.exit_json.call_args_list
                      if c[1].get('failed') is True]
        assert len(fail_calls) >= 1


# ---------------------------------------------------------------------------
# perform_module_operation — state=present, existing (idempotent / update)
# ---------------------------------------------------------------------------

class TestPerformModuleOperationUpdate:

    def test_no_changes_idempotent(self):
        """When policy exists and no changes needed, changed should be False."""
        obj = make_policy_obj()
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.validate_policy_document = MagicMock()
        obj.is_policy_document_modified = MagicMock(return_value=False)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_update_policy_document(self):
        """When policy_document differs, a new version should be created."""
        params = BASE_PARAMS.copy()
        params['policy_document'] = SAMPLE_POLICY_DOCUMENT_V2
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.validate_policy_document = MagicMock()
        obj.is_policy_document_modified = MagicMock(return_value=True)
        obj.create_policy_version = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.create_policy_version.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_update_document_check_mode(self):
        """In check mode, update should report changed but not call API."""
        params = BASE_PARAMS.copy()
        params['policy_document'] = SAMPLE_POLICY_DOCUMENT_V2
        obj = make_policy_obj(params=params)
        obj.module.check_mode = True
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.validate_policy_document = MagicMock()
        obj.is_policy_document_modified = MagicMock(return_value=True)
        obj.create_policy_version = MagicMock()

        obj.perform_module_operation()

        obj.create_policy_version.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_existing_policy_by_arn(self):
        """When policy_arn is provided, use it for lookup."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_name'] = None
        params['policy_document'] = None
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs.get('policy_details') is not None


# ---------------------------------------------------------------------------
# perform_module_operation — state=absent
# ---------------------------------------------------------------------------

class TestPerformModuleOperationDelete:

    def test_delete_existing_policy(self):
        """Delete a policy that exists."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.delete_policy = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.delete_policy.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_delete_non_existent_policy(self):
        """Delete a policy that doesn't exist should be idempotent."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        obj = make_policy_obj(params=params)
        obj.get_policy_details = MagicMock(return_value=None)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_delete_check_mode(self):
        """In check mode, delete should set changed but not call API."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        obj = make_policy_obj(params=params)
        obj.module.check_mode = True
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.delete_policy = MagicMock()

        obj.perform_module_operation()

        obj.delete_policy.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_delete_ignores_attach_entities(self):
        """attach_entities should be ignored when state=absent."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['attach_entities'] = [{'entity_type': 'user', 'entity_name': 'alice'}]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.delete_policy = MagicMock(return_value=True)
        obj.attach_entity = MagicMock()

        obj.perform_module_operation()

        obj.attach_entity.assert_not_called()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True


# ---------------------------------------------------------------------------
# perform_module_operation — attach / detach
# ---------------------------------------------------------------------------

class TestPerformModuleOperationAttachDetach:

    def test_attach_user(self):
        """Attach policy to a user."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_document'] = None
        params['attach_entities'] = [{'entity_type': 'user', 'entity_name': 'alice'}]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.attach_entity = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.attach_entity.assert_called_once_with(
            'urn:ecs:iam::testns:policy/TestPolicy', 'user', 'alice')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_attach_group(self):
        """Attach policy to a group."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_document'] = None
        params['attach_entities'] = [{'entity_type': 'group', 'entity_name': 'developers'}]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.attach_entity = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.attach_entity.assert_called_once_with(
            'urn:ecs:iam::testns:policy/TestPolicy', 'group', 'developers')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_attach_role(self):
        """Attach policy to a role."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_document'] = None
        params['attach_entities'] = [{'entity_type': 'role', 'entity_name': 'myrole'}]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.attach_entity = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.attach_entity.assert_called_once_with(
            'urn:ecs:iam::testns:policy/TestPolicy', 'role', 'myrole')

    def test_attach_multiple_entities(self):
        """Attach to multiple entities in one call."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_document'] = None
        params['attach_entities'] = [
            {'entity_type': 'user', 'entity_name': 'alice'},
            {'entity_type': 'group', 'entity_name': 'devs'},
        ]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.attach_entity = MagicMock(return_value=True)

        obj.perform_module_operation()

        assert obj.attach_entity.call_count == 2
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_detach_user(self):
        """Detach policy from a user."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_document'] = None
        params['detach_entities'] = [{'entity_type': 'user', 'entity_name': 'alice'}]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.detach_entity = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.detach_entity.assert_called_once_with(
            'urn:ecs:iam::testns:policy/TestPolicy', 'user', 'alice')
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_detach_group(self):
        """Detach policy from a group."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_document'] = None
        params['detach_entities'] = [{'entity_type': 'group', 'entity_name': 'devs'}]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.detach_entity = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.detach_entity.assert_called_once_with(
            'urn:ecs:iam::testns:policy/TestPolicy', 'group', 'devs')

    def test_detach_role(self):
        """Detach policy from a role."""
        params = BASE_PARAMS.copy()
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        params['policy_document'] = None
        params['detach_entities'] = [{'entity_type': 'role', 'entity_name': 'myrole'}]
        obj = make_policy_obj(params=params)
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.detach_entity = MagicMock(return_value=True)

        obj.perform_module_operation()

        obj.detach_entity.assert_called_once_with(
            'urn:ecs:iam::testns:policy/TestPolicy', 'role', 'myrole')


# ---------------------------------------------------------------------------
# perform_module_operation — diff mode
# ---------------------------------------------------------------------------

class TestPerformModuleOperationDiff:

    def test_diff_mode_create(self):
        """Diff mode on create should show before=None, after=details."""
        obj = make_policy_obj()
        obj.module._diff = True
        obj.get_policy_details = MagicMock(side_effect=[None, MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']])
        obj.validate_policy_document = MagicMock()
        obj.create_policy = MagicMock(return_value=MOCK_CREATE_POLICY_RESPONSE)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in kwargs
        assert kwargs['diff']['before'] is None or kwargs['diff']['before'] == {}

    def test_diff_mode_delete(self):
        """Diff mode on delete should show before=details, after=None."""
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        params['policy_arn'] = 'urn:ecs:iam::testns:policy/TestPolicy'
        obj = make_policy_obj(params=params)
        obj.module._diff = True
        policy_details = MOCK_POLICY_DETAILS['GetPolicyResult']['Policy']
        obj.get_policy_details = MagicMock(return_value=policy_details)
        obj.delete_policy = MagicMock(return_value=True)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in kwargs
        assert kwargs['diff']['after'] is None or kwargs['diff']['after'] == {}
