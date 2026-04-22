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

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.replication_group_info'


def make_info_obj(params=None, has_client=True):
    """Helper: return a ReplicationGroupInfo instance with all I/O mocked."""
    from ansible_collections.dellemc.objectscale.plugins.modules.replication_group_info import ReplicationGroupInfo

    info_params = BASE_PARAMS.copy()
    info_params.pop('state', None)
    info_params.pop('new_name', None)
    info_params.pop('description', None)
    info_params.pop('replication_type', None)
    info_params.pop('mappings', None)
    info_params.pop('replicate_to_all_sites', None)
    info_params.pop('enable_rebalancing', None)
    info_params.pop('skip_bootstrap_check', None)
    info_params.pop('force_pso_zones', None)
    info_params.update(dict(id=None, name=None, fetch_full_details=True))

    if params:
        info_params.update(params)

    module_mock = MagicMock()
    module_mock.params = info_params
    module_mock.check_mode = False
    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.DataVpoolApi'):
        obj = ReplicationGroupInfo()

    obj.module = module_mock
    obj.data_vpool_api = MagicMock()
    return obj


class TestReplicationGroupInfoInit:

    @patch(f'{MODULE}.DataVpoolApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_data_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group_info import ReplicationGroupInfo
        mock_module = MagicMock()
        params = BASE_PARAMS.copy()
        params.update(dict(id=None, name=None, fetch_full_details=True))
        mock_module.params = params
        mock_am.return_value = mock_module

        obj = ReplicationGroupInfo()

        assert obj.module is mock_module
        mock_conn.assert_called_once()
        mock_data_api.assert_called_once()

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_missing_client(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group_info import ReplicationGroupInfo
        mock_module = MagicMock()
        params = BASE_PARAMS.copy()
        params.update(dict(id=None, name=None, fetch_full_details=True))
        mock_module.params = params
        mock_am.return_value = mock_module

        ReplicationGroupInfo()

        mock_module.exit_json.assert_called_once()
        assert 'objectscale_client' in mock_module.exit_json.call_args[1]['msg']


class TestReplicationGroupInfoOperations:

    def test_list_all(self):
        obj = make_info_obj()
        response = MagicMock()
        response.to_dict.return_value = LIST_RG_RESPONSE
        obj.data_vpool_api.data_service_vpool_service_get_data_service_vpools.return_value = response

        result = obj.list_all()

        assert len(result) == 2
        assert result[0]['name'] == 'rg-test-1'

    def test_get_by_id(self):
        params = {'id': SAMPLE_RG['id']}
        obj = make_info_obj(params=params)
        response = MagicMock()
        response.to_dict.return_value = SAMPLE_RG.copy()
        obj.data_vpool_api.data_service_vpool_service_get_data_service_store.return_value = response

        result = obj.get_by_id(SAMPLE_RG['id'])

        assert result['id'] == SAMPLE_RG['id']

    def test_get_by_id_not_found(self):
        obj = make_info_obj(params={'id': 'urn:missing'})
        err = Exception('not found')
        err.status = 404
        obj.data_vpool_api.data_service_vpool_service_get_data_service_store.side_effect = err

        result = obj.get_by_id('urn:missing')

        assert result is None

    def test_perform_list_all_full_details(self):
        obj = make_info_obj(params={'fetch_full_details': True})
        obj.list_all = MagicMock(return_value=[
            {'id': 'urn:storageos:ReplicationGroupInfo:111:global', 'name': 'rg-test-1'},
            {'id': 'urn:storageos:ReplicationGroupInfo:222:global', 'name': 'rg-test-2'},
        ])
        obj.get_by_id = MagicMock(side_effect=[
            SAMPLE_RG.copy(),
            {'id': 'urn:storageos:ReplicationGroupInfo:222:global', 'name': 'rg-test-2'},
        ])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['replication_groups']) == 2

    def test_perform_get_by_name(self):
        obj = make_info_obj(params={'name': 'rg-test-1', 'fetch_full_details': False})
        obj.list_all = MagicMock(return_value=[
            {'id': 'urn:storageos:ReplicationGroupInfo:111:global', 'name': 'rg-test-1'},
            {'id': 'urn:storageos:ReplicationGroupInfo:222:global', 'name': 'rg-test-2'},
        ])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['replication_groups']) == 1
        assert kwargs['replication_groups'][0]['name'] == 'rg-test-1'

    def test_perform_get_by_id(self):
        obj = make_info_obj(params={'id': SAMPLE_RG['id']})
        obj.get_by_id = MagicMock(return_value=SAMPLE_RG.copy())

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert len(kwargs['replication_groups']) == 1
        assert kwargs['replication_groups'][0]['id'] == SAMPLE_RG['id']

    def test_id_and_name_mutually_exclusive(self):
        obj = make_info_obj(params={'id': 'urn:1', 'name': 'rg-test-1'})

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once()
        assert 'mutually exclusive' in obj.module.exit_json.call_args[1]['msg']

    def test_duplicate_name_failure(self):
        obj = make_info_obj(params={'name': 'dup'})
        obj.list_all = MagicMock(return_value=[
            {'id': 'urn:1', 'name': 'dup'},
            {'id': 'urn:2', 'name': 'dup'},
        ])

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once()
        assert 'Multiple replication groups found' in obj.module.exit_json.call_args[1]['msg']

    def test_main_function(self):
        with patch(f'{MODULE}.ReplicationGroupInfo') as mock_cls:
            from ansible_collections.dellemc.objectscale.plugins.modules.replication_group_info import main
            mock_obj = MagicMock()
            mock_cls.return_value = mock_obj
            main()
            mock_obj.perform_module_operation.assert_called_once()


class TestReplicationGroupInfoAdditionalCoverage:

    def test_init_data_vpool_api_unavailable(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group_info import ReplicationGroupInfo
        mock_module = MagicMock()
        params = BASE_PARAMS.copy()
        params.update(dict(id=None, name=None, fetch_full_details=True))
        mock_module.params = params

        with patch(f'{MODULE}.AnsibleModule', return_value=mock_module), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.DataVpoolApi', None):
            ReplicationGroupInfo()

        mock_module.exit_json.assert_called_once()
        assert 'DataVpool API client is unavailable' in mock_module.exit_json.call_args[1]['msg']

    def test_init_connection_failure(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.replication_group_info import ReplicationGroupInfo
        mock_module = MagicMock()
        params = BASE_PARAMS.copy()
        params.update(dict(id=None, name=None, fetch_full_details=True))
        mock_module.params = params

        with patch(f'{MODULE}.AnsibleModule', return_value=mock_module), \
             patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True), \
             patch(f'{MODULE}.DataVpoolApi'), \
             patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('conn err')):
            ReplicationGroupInfo()

        mock_module.exit_json.assert_called_once()
        assert 'Failed to connect to ObjectScale' in mock_module.exit_json.call_args[1]['msg']

    def test_to_dict_variants(self):
        obj = make_info_obj()
        assert obj._to_dict(None) == {}
        assert obj._to_dict({'a': 1}) == {'a': 1}
        assert obj._to_dict(object()) == {}

    def test_get_by_id_server_error(self):
        obj = make_info_obj(params={'id': 'urn:1'})
        err = Exception('server err')
        err.status = 500
        obj.data_vpool_api.data_service_vpool_service_get_data_service_store.side_effect = err

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.utils.determine_error', return_value='server err'):
            obj.get_by_id('urn:1')

        obj.module.exit_json.assert_called_once()
        assert 'Getting replication group urn:1 failed' in obj.module.exit_json.call_args[1]['msg']

    def test_list_all_error(self):
        obj = make_info_obj()
        obj.data_vpool_api.data_service_vpool_service_get_data_service_vpools.side_effect = Exception('list err')

        with patch('ansible_collections.dellemc.objectscale.plugins.module_utils.utils.determine_error', return_value='list err'):
            obj.list_all()

        obj.module.exit_json.assert_called_once()
        assert 'Listing replication groups failed' in obj.module.exit_json.call_args[1]['msg']

    def test_perform_fetch_full_details_false(self):
        obj = make_info_obj(params={'fetch_full_details': False})
        obj.list_all = MagicMock(return_value=[{'id': 'urn:1', 'name': 'rg1'}])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['replication_groups'] == [{'id': 'urn:1', 'name': 'rg1'}]

    def test_perform_fetch_full_details_true_with_missing_id(self):
        obj = make_info_obj(params={'fetch_full_details': True})
        obj.list_all = MagicMock(return_value=[{'name': 'rg-no-id'}])

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['replication_groups'] == [{'name': 'rg-no-id'}]

    def test_perform_get_by_id_not_found_returns_empty(self):
        obj = make_info_obj(params={'id': 'urn:missing'})
        obj.get_by_id = MagicMock(return_value=None)

        obj.perform_module_operation()

        kwargs = obj.module.exit_json.call_args[1]
        assert kwargs['changed'] is False
        assert kwargs['replication_groups'] == []
