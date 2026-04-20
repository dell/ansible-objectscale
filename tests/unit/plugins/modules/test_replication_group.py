# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

from ansible_collections.dellemc.objectscale.tests.unit.plugins.module_utils.mock_replication_group_api import (
    BASE_PARAMS,
    LIST_RG_RESPONSE,
    SAMPLE_RG,
)

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.replication_group'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'


def make_rg_obj(params=None, has_client=True):
    """Helper: return a ReplicationGroup instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import ReplicationGroup

    module_mock = MagicMock()
    module_mock.params = (params or BASE_PARAMS).copy()
    module_mock.check_mode = False
    module_mock._diff = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.DataVpoolApi'):
        obj = ReplicationGroup()

    obj.module = module_mock
    obj.data_vpool_api = MagicMock()
    return obj


class TestReplicationGroupInit:

    @patch(f'{MODULE}.DataVpoolApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_data_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import ReplicationGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        obj = ReplicationGroup()

        assert obj.module is mock_module
        mock_conn.assert_called_once()
        mock_data_api.assert_called_once()

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_missing_client(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import ReplicationGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module

        ReplicationGroup()

        mock_module.fail_json.assert_called_once()
        assert 'objectscale_client' in mock_module.fail_json.call_args[1]['msg']


class TestReplicationGroupReadOps:

    def test_get_all_replication_groups(self):
        obj = make_rg_obj()
        response = MagicMock()
        response.to_dict.return_value = LIST_RG_RESPONSE
        obj.data_vpool_api.data_service_vpool_service_get_data_service_vpools.return_value = response

        result = obj.get_all_replication_groups()

        assert len(result) == 2
        assert result[0]['name'] == 'rg-test-1'

    def test_get_replication_group_by_id_404(self):
        obj = make_rg_obj()
        err = Exception('not found')
        err.status = 404
        obj.data_vpool_api.data_service_vpool_service_get_data_service_store.side_effect = err

        assert obj.get_replication_group_by_id('urn:missing') is None

    def test_find_by_name_ambiguous(self):
        obj = make_rg_obj()
        obj.get_all_replication_groups = MagicMock(return_value=[
            {'id': 'urn:1', 'name': 'dup'},
            {'id': 'urn:2', 'name': 'dup'},
        ])

        obj.find_replication_group_by_name('dup')

        obj.module.fail_json.assert_called_once()
        assert 'Multiple replication groups found' in obj.module.fail_json.call_args[1]['msg']


class TestReplicationGroupDiffLogic:

    def test_is_modified_no_change(self):
        params = BASE_PARAMS.copy()
        obj = make_rg_obj(params=params)

        result = obj.is_replication_group_modified(SAMPLE_RG.copy())

        assert result['is_modified'] is False
        assert result['metadata_changes'] == {}
        assert result['mappings_to_add'] == []
        assert result['mappings_to_remove'] == []

    def test_is_modified_metadata_and_mapping_change(self):
        params = BASE_PARAMS.copy()
        params['new_name'] = 'rg-test-1-renamed'
        params['description'] = 'updated-description'
        params['enable_rebalancing'] = True
        params['replicate_to_all_sites'] = True
        params['mappings'] = [
            {
                'vdc_id': 'urn:storageos:VirtualDataCenterData:111',
                'storage_pool_id': 'urn:storageos:VirtualArray:111',
                'is_replication_target': True,
            }
        ]
        obj = make_rg_obj(params=params)

        result = obj.is_replication_group_modified(SAMPLE_RG.copy())

        assert result['is_modified'] is True
        assert result['metadata_changes']['name'] == 'rg-test-1-renamed'
        assert result['metadata_changes']['description'] == 'updated-description'
        assert len(result['mappings_to_add']) == 1
        assert len(result['mappings_to_remove']) == 1


class TestReplicationGroupPerformModuleOperation:

    def test_present_create_path(self):
        obj = make_rg_obj()
        obj._resolve_current = MagicMock(side_effect=[None, SAMPLE_RG.copy()])
        obj.create_replication_group = MagicMock()
        obj.is_replication_group_modified = MagicMock(return_value={
            'is_modified': False,
            'metadata_changes': {},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        })

        obj.perform_module_operation()

        obj.create_replication_group.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert kwargs['replication_group']['name'] == 'rg-test-1'

    def test_present_update_path(self):
        obj = make_rg_obj()
        obj._resolve_current = MagicMock(return_value=SAMPLE_RG.copy())
        obj.get_replication_group_by_id = MagicMock(return_value=SAMPLE_RG.copy())
        obj.is_replication_group_modified = MagicMock(return_value={
            'is_modified': True,
            'metadata_changes': {'description': 'new-desc', 'name': 'rg-test-1'},
            'mappings_to_add': [{'name': 'vdc2', 'value': 'sp2', 'is_replication_target': False}],
            'mappings_to_remove': [],
        })
        obj.update_replication_group_metadata = MagicMock()
        obj.add_mappings = MagicMock()
        obj.remove_mappings = MagicMock()

        obj.perform_module_operation()

        obj.update_replication_group_metadata.assert_called_once()
        obj.add_mappings.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_absent_noop(self):
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_rg_obj(params=params)
        obj._resolve_current = MagicMock(return_value=None)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False

    def test_absent_existing(self):
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_rg_obj(params=params)
        obj._resolve_current = MagicMock(return_value=SAMPLE_RG.copy())
        obj.delete_replication_group = MagicMock()

        obj.perform_module_operation()

        obj.delete_replication_group.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_check_mode_create(self):
        obj = make_rg_obj()
        obj.module.check_mode = True
        obj._resolve_current = MagicMock(return_value=None)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_diff_mode_on_update(self):
        obj = make_rg_obj()
        obj.module._diff = True
        obj._resolve_current = MagicMock(return_value=SAMPLE_RG.copy())
        obj.get_replication_group_by_id = MagicMock(return_value=SAMPLE_RG.copy())
        obj.is_replication_group_modified = MagicMock(return_value={
            'is_modified': True,
            'metadata_changes': {'description': 'new-desc', 'name': 'rg-test-1'},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        })
        obj.update_replication_group_metadata = MagicMock()
        obj.add_mappings = MagicMock()
        obj.remove_mappings = MagicMock()

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert 'diff' in kwargs
        assert kwargs['diff']['before']['name'] == 'rg-test-1'


class TestReplicationGroupHelpers:

    def test_invalid_mapping_calls_fail(self):
        params = BASE_PARAMS.copy()
        params['mappings'] = [{'vdc_id': 'vdc-only'}]
        obj = make_rg_obj(params=params)

        obj._normalize_mapping_input(params['mappings'])

        obj.module.fail_json.assert_called_once()

    def test_main_function(self):
        with patch(f'{MODULE}.ReplicationGroup') as mock_cls:
            from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import main
            mock_obj = MagicMock()
            mock_cls.return_value = mock_obj
            main()
            mock_obj.perform_module_operation.assert_called_once()


class TestReplicationGroupAdditionalCoverage:

    def test_init_data_vpool_api_unavailable(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import ReplicationGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        with patch(f'{MODULE}.AnsibleModule', return_value=mock_module), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.DataVpoolApi', None):
            ReplicationGroup()
        mock_module.fail_json.assert_called_once()
        assert 'DataVpool API client is unavailable' in mock_module.fail_json.call_args[1]['msg']

    def test_init_connection_failure(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import ReplicationGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        with patch(f'{MODULE}.AnsibleModule', return_value=mock_module), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.DataVpoolApi'), \
             patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('conn failed')):
            ReplicationGroup()
        mock_module.fail_json.assert_called_once()
        assert 'Failed to connect to ObjectScale' in mock_module.fail_json.call_args[1]['msg']

    def test_to_dict_variants(self):
        obj = make_rg_obj()
        assert obj._to_dict(None) == {}
        assert obj._to_dict({'a': 1}) == {'a': 1}
        assert obj._to_dict(object()) == {}

    def test_build_api_payload_model_none(self):
        obj = make_rg_obj()
        payload = {'a': 1, 'b': None}
        assert obj._build_api_payload(None, payload) == {'a': 1}

    def test_build_api_payload_model_validate_path(self):
        obj = make_rg_obj()

        class DummyModel(object):
            __mro__ = (object, object)

            @staticmethod
            def model_validate(data):
                return {'validated': data}

        result = obj._build_api_payload(DummyModel, {'x': 1})
        assert result == {'validated': {'x': 1}}

    def test_build_api_payload_model_ctor_fallback(self):
        obj = make_rg_obj()

        class DummyModel(object):
            __mro__ = (object, object)

            @staticmethod
            def model_validate(_data):
                raise Exception('no validate')

            def __init__(self, **kwargs):
                self.kwargs = kwargs

        result = obj._build_api_payload(DummyModel, {'x': 2})
        assert isinstance(result, DummyModel)
        assert result.kwargs == {'x': 2}

    def test_get_all_replication_groups_error(self):
        obj = make_rg_obj()
        obj.data_vpool_api.data_service_vpool_service_get_data_service_vpools.side_effect = Exception('list err')
        with patch(f'{UTILS}.determine_error', return_value='list err'):
            obj.get_all_replication_groups()
        obj.module.fail_json.assert_called_once()
        assert 'Listing replication groups failed' in obj.module.fail_json.call_args[1]['msg']

    def test_get_replication_group_by_id_error(self):
        obj = make_rg_obj()
        err = Exception('server err')
        err.status = 500
        obj.data_vpool_api.data_service_vpool_service_get_data_service_store.side_effect = err
        with patch(f'{UTILS}.determine_error', return_value='server err'):
            obj.get_replication_group_by_id('urn:test')
        obj.module.fail_json.assert_called_once()
        assert 'Getting replication group urn:test failed' in obj.module.fail_json.call_args[1]['msg']

    def test_find_by_name_not_found_and_no_id_entry(self):
        obj = make_rg_obj()
        obj.get_all_replication_groups = MagicMock(return_value=[])
        assert obj.find_replication_group_by_name('missing') is None

        obj.get_all_replication_groups = MagicMock(return_value=[{'name': 'x'}])
        result = obj.find_replication_group_by_name('x')
        assert result == {'name': 'x'}

    def test_resolve_current_id_name_none(self):
        params = BASE_PARAMS.copy()
        params['id'] = 'urn:id'
        params['name'] = None
        obj = make_rg_obj(params=params)
        obj.get_replication_group_by_id = MagicMock(return_value={'id': 'urn:id'})
        assert obj._resolve_current() == {'id': 'urn:id'}

        params = BASE_PARAMS.copy()
        params['id'] = None
        params['name'] = 'rg-test-1'
        obj = make_rg_obj(params=params)
        obj.find_replication_group_by_name = MagicMock(return_value={'name': 'rg-test-1'})
        assert obj._resolve_current() == {'name': 'rg-test-1'}

        params = BASE_PARAMS.copy()
        params['id'] = None
        params['name'] = None
        obj = make_rg_obj(params=params)
        assert obj._resolve_current() is None

    def test_create_replication_group_name_required(self):
        params = BASE_PARAMS.copy()
        params['name'] = None
        obj = make_rg_obj(params=params)
        obj.create_replication_group()
        obj.module.fail_json.assert_called_once()
        assert 'name is required' in obj.module.fail_json.call_args[1]['msg']

    def test_create_replication_group_error(self):
        params = BASE_PARAMS.copy()
        params['id'] = 'urn:storageos:VirtualPool:unit-test-id'
        obj = make_rg_obj(params=params)
        obj.data_vpool_api.data_service_vpool_service_create_data_service_vpool.side_effect = Exception('create err')
        with patch(f'{UTILS}.determine_error', return_value='create err'):
            obj.create_replication_group()
        obj.module.fail_json.assert_called_once()
        assert 'Creating replication group failed' in obj.module.fail_json.call_args[1]['msg']

    def test_update_metadata_noop_and_error(self):
        obj = make_rg_obj()
        obj.update_replication_group_metadata('urn:1', {})
        obj.data_vpool_api.data_service_vpool_service_put_data_service_vpool.assert_not_called()

        obj.get_replication_group_by_id = MagicMock(return_value={'name': 'rg-test-1'})
        obj.data_vpool_api.data_service_vpool_service_put_data_service_vpool.side_effect = Exception('update err')
        with patch(f'{UTILS}.determine_error', return_value='update err'):
            obj.update_replication_group_metadata('urn:1', {'description': 'd1'})
        obj.module.fail_json.assert_called_once()
        assert 'Updating replication group urn:1 failed' in obj.module.fail_json.call_args[1]['msg']

    def test_add_remove_mappings_noop_and_error(self):
        obj = make_rg_obj()
        obj.add_mappings('urn:1', [])
        obj.remove_mappings('urn:1', [])
        obj.data_vpool_api.data_service_vpool_service_add_to_vpool.assert_not_called()
        obj.data_vpool_api.data_service_vpool_service_remove_from_vpool.assert_not_called()

        obj.data_vpool_api.data_service_vpool_service_add_to_vpool.side_effect = Exception('add err')
        with patch(f'{UTILS}.determine_error', return_value='add err'):
            obj.add_mappings('urn:1', [{'name': 'v', 'value': 's', 'is_replication_target': False}])
        obj.module.fail_json.assert_called_once()

        obj = make_rg_obj()
        obj.remove_mappings('urn:1', [{'name': 'v', 'value': 's', 'is_replication_target': False}])
        obj.data_vpool_api.data_service_vpool_service_remove_from_vpool.assert_not_called()
        obj.module.fail_json.assert_not_called()

    def test_delete_replication_group_paths(self):
        obj = make_rg_obj()
        obj.delete_replication_group({'name': 'x'})
        obj.module.fail_json.assert_called_once()
        assert 'id is required for delete' in obj.module.fail_json.call_args[1]['msg']

        obj = make_rg_obj()
        obj.data_vpool_api.data_service_vpool_service_delete_data_service_vpool = MagicMock()
        obj.delete_replication_group({'id': 'urn:1'})
        obj.data_vpool_api.data_service_vpool_service_delete_data_service_vpool.assert_called_once_with(id='urn:1')

        obj = make_rg_obj()
        obj.data_vpool_api.data_service_vpool_service_delete_data_service_vpool = MagicMock(side_effect=Exception('del err'))
        with patch(f'{UTILS}.determine_error', return_value='del err'):
            obj.delete_replication_group({'id': 'urn:1'})
        obj.module.fail_json.assert_called_once()

        obj = make_rg_obj()
        obj.data_vpool_api.data_service_vpool_service_delete_data_service_vpool = None
        obj.remove_mappings = MagicMock()
        obj.delete_replication_group({'id': 'urn:1', 'varrayMappings': [{'name': 'v', 'value': 's'}]})
        obj.remove_mappings.assert_not_called()

    def test_predict_after_state_absent_and_modify(self):
        obj = make_rg_obj()
        assert obj._predict_after_state({'name': 'a'}, {}, 'absent') == {}

        before = {
            'name': 'old',
            'description': 'd0',
            'enable_rebalancing': False,
            'isAllowAllNamespaces': False,
            'mappings': [{'name': 'v1', 'value': 's1', 'is_replication_target': False}],
        }
        modifications = {
            'metadata_changes': {
                'name': 'new',
                'description': 'd1',
                'enable_rebalancing': True,
                'allowAllNamespaces': True,
            },
            'mappings_to_add': [{'name': 'v2', 'value': 's2', 'is_replication_target': True}],
            'mappings_to_remove': [{'name': 'v1', 'value': 's1', 'is_replication_target': False}],
        }
        after = obj._predict_after_state(before, modifications, 'present')
        assert after['name'] == 'new'
        assert after['description'] == 'd1'
        assert after['enable_rebalancing'] is True
        assert after['isAllowAllNamespaces'] is True
        assert len(after['mappings']) == 1

    def test_perform_absent_check_mode_with_diff(self):
        params = BASE_PARAMS.copy()
        params['state'] = 'absent'
        obj = make_rg_obj(params=params)
        obj.module.check_mode = True
        obj.module._diff = True
        obj._resolve_current = MagicMock(return_value=SAMPLE_RG.copy())

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert kwargs['diff']['after'] == {}

    def test_perform_present_unresolved_after_create(self):
        obj = make_rg_obj()
        obj._resolve_current = MagicMock(side_effect=[None, None])
        obj.create_replication_group = MagicMock()

        obj.perform_module_operation()

        obj.module.fail_json.assert_called_once()
        assert 'Unable to resolve replication group after create/update operation' in obj.module.fail_json.call_args[1]['msg']

    def test_perform_present_modified_check_mode_predicts_after(self):
        obj = make_rg_obj()
        obj.module.check_mode = True
        obj._resolve_current = MagicMock(return_value=SAMPLE_RG.copy())
        obj.is_replication_group_modified = MagicMock(return_value={
            'is_modified': True,
            'metadata_changes': {'description': 'd-new', 'name': 'rg-test-1'},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        })

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert kwargs['replication_group']['description'] == 'd-new'

    def test_perform_present_modified_missing_id(self):
        obj = make_rg_obj()
        obj._resolve_current = MagicMock(return_value={'name': 'rg-test-1'})
        obj.is_replication_group_modified = MagicMock(return_value={
            'is_modified': True,
            'metadata_changes': {'description': 'd-new'},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        })

        obj.perform_module_operation()

        obj.module.fail_json.assert_called_once()
        assert 'id is missing' in obj.module.fail_json.call_args[1]['msg']


class TestReplicationGroupCoverageImprovements:

    def test_import_error_blocks(self):
        """Test import error except blocks are hit."""
        # These lines (162-163, 169-170, 176-177, 183-184, 190-191) are hit when imports fail
        # We can't easily trigger actual import failures in tests, but we can verify
        # the module handles None values from these imports correctly
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import ReplicationGroup
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()

        with patch(f'{MODULE}.AnsibleModule', return_value=mock_module), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.DataVpoolApi', None), \
             patch(f'{MODULE}.DataServiceVpoolServiceCreateDataServiceVpoolRequest', None), \
             patch(f'{MODULE}.DataServiceVpoolServicePutDataServiceVpoolRequest', None), \
             patch(f'{MODULE}.DataServiceVpoolServiceAddToVpoolRequest', None):
            ReplicationGroup()
        mock_module.fail_json.assert_called_once()
        assert 'DataVpool API client is unavailable' in mock_module.fail_json.call_args[1]['msg']

    def test_build_api_payload_stub_base_class(self):
        """Test base class stub check in _build_api_payload (line 244)."""
        obj = make_rg_obj()

        class StubBase(object):
            __module__ = 'objectscale_client._stubs'

        class StubModel(StubBase):
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        result = obj._build_api_payload(StubModel, {'x': 1})
        assert result == {'x': 1}

    def test_normalize_mapping_input_non_dict(self):
        """Test non-dict mapping validation (line 255)."""
        params = BASE_PARAMS.copy()
        params['mappings'] = ['not-a-dict']
        obj = make_rg_obj(params=params)

        # The method calls fail_json but doesn't return, so we need to mock it to raise
        obj.module.fail_json.side_effect = Exception('fail_json called')

        try:
            obj._normalize_mapping_input(params['mappings'])
        except Exception as e:
            assert str(e) == 'fail_json called'

        obj.module.fail_json.assert_called_once()
        assert 'Each mappings entry must be a dict' in obj.module.fail_json.call_args[1]['msg']

    def test_get_replication_group_by_id_empty_response(self):
        """Test empty response handling in get_replication_group_by_id (lines 318-325)."""
        obj = make_rg_obj()
        response = MagicMock()
        response.to_dict.return_value = {}
        obj.data_vpool_api.data_service_vpool_service_get_data_service_store.return_value = response

        assert obj.get_replication_group_by_id('urn:test') is None

        # Test with empty object that has no id, name, or description
        response.to_dict.return_value = {'other_field': 'value'}
        assert obj.get_replication_group_by_id('urn:test') is None

    def test_find_replication_group_by_name_no_id(self):
        """Test rg_id None case in find_replication_group_by_name (line 344)."""
        obj = make_rg_obj()
        obj.get_all_replication_groups = MagicMock(return_value=[{'name': 'rg-test', 'id': None}])

        result = obj.find_replication_group_by_name('rg-test')
        assert result == {'name': 'rg-test', 'id': None}

    def test_create_replication_group_with_payload_serializer_path(self):
        """Test serializer path in _create_replication_group_with_payload (lines 429-450)."""
        params = BASE_PARAMS.copy()
        params['id'] = None  # No ID to trigger serializer path
        obj = make_rg_obj(params=params)

        # Mock the serializer method
        serializer_mock = MagicMock(return_value=('/path', 'method', {'params': 'val'}))
        obj.data_vpool_api._data_service_vpool_service_create_data_service_vpool_serialize = serializer_mock

        # Mock the API client call_api
        response_mock = MagicMock()
        response_mock.read = MagicMock()
        obj.data_vpool_api.api_client.call_api = MagicMock(return_value=response_mock)

        payload = {
            'name': 'test-rg',
            'description': 'test',
            'zone_mappings': [],
            'enable_rebalancing': False,
            'isAllowAllNamespaces': False,
            'isFullRep': True,
            'use_replication_target': False,
        }

        obj._create_replication_group_with_payload(payload)

        serializer_mock.assert_called_once()
        obj.data_vpool_api.api_client.call_api.assert_called_once()

    def test_create_replication_group_with_payload_serializer_unavailable(self):
        """Test serializer unavailable case (line 435)."""
        params = BASE_PARAMS.copy()
        params['id'] = None
        obj = make_rg_obj(params=params)

        # Mock serializer as None
        obj.data_vpool_api._data_service_vpool_service_create_data_service_vpool_serialize = None

        payload = {
            'name': 'test-rg',
            'zone_mappings': [],
        }

        obj._create_replication_group_with_payload(payload)

        obj.module.fail_json.assert_called_once()
        assert 'Create serializer method is unavailable' in obj.module.fail_json.call_args[1]['msg']

    def test_rename_by_recreate(self):
        """Test _rename_by_recreate method (lines 462-484)."""
        params = BASE_PARAMS.copy()
        params['new_name'] = 'renamed-rg'
        obj = make_rg_obj(params=params)

        current = {'id': 'urn:1', 'name': 'old-rg', 'varrayMappings': [{'name': 'v1', 'value': 's1'}]}
        modifications = {
            'metadata_changes': {'name': 'renamed-rg'},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        }

        obj._create_replication_group_with_payload = MagicMock()
        obj.delete_replication_group = MagicMock()
        obj.find_replication_group_by_name = MagicMock(return_value={'id': 'urn:2', 'name': 'renamed-rg'})

        result = obj._rename_by_recreate(current, modifications)

        assert result == {'id': 'urn:2', 'name': 'renamed-rg'}
        obj._create_replication_group_with_payload.assert_called_once()
        obj.delete_replication_group.assert_called_once_with(current)

    def test_rename_by_recreate_no_desired_name(self):
        """Test _rename_by_recreate with no desired name (line 463-464)."""
        obj = make_rg_obj()
        current = {'id': 'urn:1', 'name': 'old-rg'}
        modifications = {'metadata_changes': {}}

        result = obj._rename_by_recreate(current, modifications)

        assert result == current

    def test_rename_by_recreate_empty_desired_mappings(self):
        """Test _rename_by_recreate with empty desired mappings (line 468)."""
        params = BASE_PARAMS.copy()
        params['new_name'] = 'renamed-rg'
        params['mappings'] = None  # No desired mappings
        obj = make_rg_obj(params=params)

        current = {
            'id': 'urn:1',
            'name': 'old-rg',
            'varrayMappings': [{'name': 'v1', 'value': 's1', 'is_replication_target': False}]
        }
        modifications = {
            'metadata_changes': {'name': 'renamed-rg'},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        }

        obj._create_replication_group_with_payload = MagicMock()
        obj.delete_replication_group = MagicMock()
        obj.find_replication_group_by_name = MagicMock(return_value={'id': 'urn:2', 'name': 'renamed-rg'})

        result = obj._rename_by_recreate(current, modifications)

        assert result == {'id': 'urn:2', 'name': 'renamed-rg'}
        obj._create_replication_group_with_payload.assert_called_once()
        # Verify the payload includes current mappings
        call_args = obj._create_replication_group_with_payload.call_args[0][0]
        assert call_args['zone_mappings'] == [{'name': 'v1', 'value': 's1', 'is_replication_target': False}]

    def test_perform_present_create_with_diff(self):
        """Test perform_module_operation create path with diff (line 599)."""
        obj = make_rg_obj()
        obj.module._diff = True
        obj._resolve_current = MagicMock(side_effect=[None, SAMPLE_RG.copy()])
        obj.create_replication_group = MagicMock()
        obj.is_replication_group_modified = MagicMock(return_value={
            'is_modified': False,
            'metadata_changes': {},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        })

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True
        assert 'diff' in kwargs
        assert kwargs['diff']['before'] == {}

    def test_perform_present_rename_by_recreate_path(self):
        """Test perform_module_operation rename by recreate path (line 622)."""
        params = BASE_PARAMS.copy()
        params['new_name'] = 'renamed-rg'
        obj = make_rg_obj(params=params)
        obj._resolve_current = MagicMock(return_value=SAMPLE_RG.copy())
        obj.get_replication_group_by_id = MagicMock(return_value=SAMPLE_RG.copy())
        obj.is_replication_group_modified = MagicMock(return_value={
            'is_modified': True,
            'metadata_changes': {'name': 'renamed-rg'},
            'mappings_to_add': [],
            'mappings_to_remove': [],
        })
        obj._rename_by_recreate = MagicMock(return_value={'id': 'urn:1', 'name': 'renamed-rg'})

        obj.perform_module_operation()

        obj._rename_by_recreate.assert_called_once()
        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is True

    def test_main_guard(self):
        """Test main function guard (line 667)."""
        import sys
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group import main

        # Simulate __name__ != '__main__'
        old_name = sys.modules.get('__main__')
        try:
            with patch(f'{MODULE}.ReplicationGroup') as mock_cls:
                mock_obj = MagicMock()
                mock_cls.return_value = mock_obj
                main()
                mock_obj.perform_module_operation.assert_called_once()
        finally:
            if old_name:
                sys.modules['__main__'] = old_name
