# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.vdc_info'
UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    vdc_name=None,
    vdc_id=None,
    local_vdc=None,
)

VDC_DICT = {
    'id': 'urn:storageos:VirtualDataCenterData:abc123',
    'name': 'vdc-site-a',
    'vdcId': 'urn:storageos:VirtualDataCenterData:abc123',
    'vdcName': 'vdc-site-a',
    'local': True,
    'permanentlyFailed': False,
    'is_encryption_enabled': False,
    'managementEndPoints': '10.0.0.1',
    'interVdcEndPoints': '10.0.0.1:9095',
    'interVdcCmdEndPoints': '10.0.0.1:9096',
}

VDC_DICT_WITH_SECRET = dict(VDC_DICT, secretKeys='super-secret-key')


def make_obj(params=None, has_client=True):
    from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import VdcInfo

    module_mock = MagicMock()
    module_mock.params = params or PARAMS.copy()

    api_client_mock = MagicMock()

    with patch(f'{MODULE}.AnsibleModule', return_value=module_mock), \
         patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', has_client), \
         patch(f'{MODULE}.utils.get_objectscale_connection', return_value=api_client_mock), \
         patch(f'{MODULE}.ZoneInfoApi'):
        obj = VdcInfo()

    obj.module = module_mock
    obj.zone_info_api = MagicMock()
    return obj


class TestVdcInfoInit:

    @patch(f'{MODULE}.ZoneInfoApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_success(self, mock_am, mock_conn, mock_api):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import VdcInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        obj = VdcInfo()

        assert obj.module is mock_module
        mock_conn.assert_called_once()

    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', False)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_no_client(self, mock_am, mock_conn):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import VdcInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        VdcInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'objectscale_client' in kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.ZoneInfoApi', None)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_zone_api_unavailable(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import VdcInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        VdcInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'ZoneInfo API client is unavailable' in kwargs['msg']

    @patch(f'{MODULE}.HAS_OBJECTSCALE_CLIENT', True)
    @patch(f'{MODULE}.AnsibleModule')
    def test_init_connection_error(self, mock_am):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import VdcInfo

        mock_module = MagicMock()
        mock_module.params = PARAMS.copy()
        mock_am.return_value = mock_module

        with patch(f'{MODULE}.utils.get_objectscale_connection', side_effect=Exception('conn failed')):
            VdcInfo()

        mock_module.fail_json.assert_called_once()
        kwargs = mock_module.fail_json.call_args[1]
        assert 'Failed to connect to ObjectScale' in kwargs['msg']


class TestVdcInfoCompatibilityShim:

    def test_ensure_secretstr_compatibility(self):
        obj = make_obj()

        fake_api_client = type('ApiClientStub', (), {'SecretStr': str})
        fake_base_model = type('BaseModelStub', (), {})
        fake_stubs = type('StubsStub', (), {'BaseModel': fake_base_model})

        with patch(f'{MODULE}.objectscale_api_client', fake_api_client), \
             patch(f'{MODULE}.objectscale_client_stubs', fake_stubs):
            obj._ensure_secretstr_compatibility()

            compat_secret = fake_api_client.SecretStr('secret')
            assert hasattr(compat_secret, 'get_secret_value')
            assert compat_secret.get_secret_value() == 'secret'

            model = fake_base_model()
            model.foo = 'bar'
            assert model.model_dump() == {'foo': 'bar'}


class TestMaskSensitive:

    def test_mask_sensitive_removes_secret_keys(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import _mask_sensitive

        result = _mask_sensitive(VDC_DICT_WITH_SECRET)
        assert 'secretKeys' not in result
        assert result['id'] == VDC_DICT_WITH_SECRET['id']

    def test_mask_sensitive_no_secret_keys(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import _mask_sensitive

        result = _mask_sensitive(VDC_DICT)
        assert result == VDC_DICT

    def test_mask_sensitive_removes_snake_case_variant(self):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import _mask_sensitive

        d = dict(VDC_DICT, secret_keys='abc')
        result = _mask_sensitive(d)
        assert 'secret_keys' not in result


class TestVdcInfoListAll:

    def test_list_all_vdcs_success(self):
        obj = make_obj()
        vdc_mock = MagicMock()
        vdc_mock.to_dict.return_value = VDC_DICT_WITH_SECRET
        response = MagicMock()
        response.to_dict.return_value = {'vdc': [vdc_mock]}
        obj.zone_info_api.zone_info_service_list_all_vdc.return_value = response

        result = obj.list_all_vdcs()

        assert len(result) == 1
        assert 'secretKeys' not in result[0]
        assert result[0]['id'] == VDC_DICT['id']

    def test_list_all_vdcs_empty(self):
        obj = make_obj()
        response = MagicMock()
        response.to_dict.return_value = {'vdc': []}
        obj.zone_info_api.zone_info_service_list_all_vdc.return_value = response

        result = obj.list_all_vdcs()

        assert result == []

    def test_list_all_vdcs_none_vdc_key(self):
        obj = make_obj()
        response = MagicMock()
        response.to_dict.return_value = {}
        obj.zone_info_api.zone_info_service_list_all_vdc.return_value = response

        result = obj.list_all_vdcs()

        assert result == []

    def test_list_all_vdcs_api_error(self):
        obj = make_obj()
        obj.zone_info_api.zone_info_service_list_all_vdc.side_effect = Exception('API error')

        with patch(f'{UTILS}.determine_error', return_value='API error'):
            obj.list_all_vdcs()

        obj.module.fail_json.assert_called_once()
        assert 'API error' in obj.module.fail_json.call_args[1]['msg']


class TestVdcInfoGetLocal:

    def test_get_local_vdc_success(self):
        obj = make_obj()
        response = MagicMock()
        response.to_dict.return_value = VDC_DICT_WITH_SECRET
        obj.zone_info_api.zone_info_service_get_local_vdc.return_value = response

        result = obj.get_local_vdc()

        assert result is not None
        assert 'secretKeys' not in result
        assert result['local'] is True

    def test_get_local_vdc_api_error(self):
        obj = make_obj()
        obj.zone_info_api.zone_info_service_get_local_vdc.side_effect = Exception('error')

        with patch(f'{UTILS}.determine_error', return_value='error'):
            obj.get_local_vdc()

        obj.module.fail_json.assert_called_once()
        assert 'Getting local VDC failed' in obj.module.fail_json.call_args[1]['msg']


class TestVdcInfoGetByName:

    def test_get_vdc_by_name_success(self):
        obj = make_obj()
        response = MagicMock()
        response.to_dict.return_value = VDC_DICT_WITH_SECRET
        obj.zone_info_api.zone_info_service_get_vdc_by_name.return_value = response

        result = obj.get_vdc_by_name('vdc-site-a')

        obj.zone_info_api.zone_info_service_get_vdc_by_name.assert_called_once_with(vdc_name='vdc-site-a')
        assert result is not None
        assert 'secretKeys' not in result
        assert result['name'] == 'vdc-site-a'

    def test_get_vdc_by_name_not_found_404(self):
        obj = make_obj()
        err = Exception('not found')
        err.status = 404
        obj.zone_info_api.zone_info_service_get_vdc_by_name.side_effect = err

        result = obj.get_vdc_by_name('nonexistent')

        assert result is None
        obj.module.fail_json.assert_not_called()

    def test_get_vdc_by_name_not_found_400(self):
        obj = make_obj()
        err = Exception('bad request')
        err.status = 400
        obj.zone_info_api.zone_info_service_get_vdc_by_name.side_effect = err

        result = obj.get_vdc_by_name('nonexistent')

        assert result is None
        obj.module.fail_json.assert_not_called()

    def test_get_vdc_by_name_server_error(self):
        obj = make_obj()
        err = Exception('server error')
        err.status = 500
        obj.zone_info_api.zone_info_service_get_vdc_by_name.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='server error'):
            obj.get_vdc_by_name('vdc-site-a')

        obj.module.fail_json.assert_called_once()
        assert 'vdc-site-a' in obj.module.fail_json.call_args[1]['msg']


class TestVdcInfoGetById:

    def test_get_vdc_by_id_success(self):
        obj = make_obj()
        response = MagicMock()
        response.to_dict.return_value = VDC_DICT_WITH_SECRET
        obj.zone_info_api.zone_info_service_get_vdc_by_id.return_value = response

        result = obj.get_vdc_by_id('urn:storageos:VirtualDataCenterData:abc123')

        obj.zone_info_api.zone_info_service_get_vdc_by_id.assert_called_once_with(
            vdc_id='urn:storageos:VirtualDataCenterData:abc123'
        )
        assert result is not None
        assert 'secretKeys' not in result

    def test_get_vdc_by_id_not_found_404(self):
        obj = make_obj()
        err = Exception('not found')
        err.status = 404
        obj.zone_info_api.zone_info_service_get_vdc_by_id.side_effect = err

        result = obj.get_vdc_by_id('invalid-id')

        assert result is None
        obj.module.fail_json.assert_not_called()

    def test_get_vdc_by_id_server_error(self):
        obj = make_obj()
        err = Exception('internal error')
        err.status = 500
        obj.zone_info_api.zone_info_service_get_vdc_by_id.side_effect = err

        with patch(f'{UTILS}.determine_error', return_value='internal error'):
            obj.get_vdc_by_id('some-id')

        obj.module.fail_json.assert_called_once()
        assert 'some-id' in obj.module.fail_json.call_args[1]['msg']


class TestVdcInfoPerform:

    def test_perform_list_all(self):
        obj = make_obj()
        obj.list_all_vdcs = MagicMock(return_value=[VDC_DICT])

        obj.perform_module_operation()

        obj.list_all_vdcs.assert_called_once()
        obj.module.exit_json.assert_called_once_with(changed=False, vdcs=[VDC_DICT])

    def test_perform_local_vdc(self):
        obj = make_obj(params={**PARAMS, 'local_vdc': True})
        obj.get_local_vdc = MagicMock(return_value=VDC_DICT)

        obj.perform_module_operation()

        obj.get_local_vdc.assert_called_once()
        obj.module.exit_json.assert_called_once_with(changed=False, vdcs=[VDC_DICT])

    def test_perform_local_vdc_not_found(self):
        obj = make_obj(params={**PARAMS, 'local_vdc': True})
        obj.get_local_vdc = MagicMock(return_value=None)

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(changed=False, vdcs=[])

    def test_perform_get_by_name(self):
        obj = make_obj(params={**PARAMS, 'vdc_name': 'vdc-site-a'})
        obj.get_vdc_by_name = MagicMock(return_value=VDC_DICT)

        obj.perform_module_operation()

        obj.get_vdc_by_name.assert_called_once_with('vdc-site-a')
        obj.module.exit_json.assert_called_once_with(changed=False, vdcs=[VDC_DICT])

    def test_perform_get_by_name_not_found(self):
        obj = make_obj(params={**PARAMS, 'vdc_name': 'missing'})
        obj.get_vdc_by_name = MagicMock(return_value=None)

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(changed=False, vdcs=[])

    def test_perform_get_by_id(self):
        obj = make_obj(params={**PARAMS, 'vdc_id': 'urn:storageos:VirtualDataCenterData:abc123'})
        obj.get_vdc_by_id = MagicMock(return_value=VDC_DICT)

        obj.perform_module_operation()

        obj.get_vdc_by_id.assert_called_once_with('urn:storageos:VirtualDataCenterData:abc123')
        obj.module.exit_json.assert_called_once_with(changed=False, vdcs=[VDC_DICT])

    def test_perform_get_by_id_not_found(self):
        obj = make_obj(params={**PARAMS, 'vdc_id': 'invalid-id'})
        obj.get_vdc_by_id = MagicMock(return_value=None)

        obj.perform_module_operation()

        obj.module.exit_json.assert_called_once_with(changed=False, vdcs=[])


class TestVdcInfoMain:

    @patch(f'{MODULE}.VdcInfo')
    def test_main_calls_perform(self, mock_cls):
        from ansible_collections.dellemc.objectscale.plugins.modules.vdc_info import main

        mock_obj = MagicMock()
        mock_cls.return_value = mock_obj

        main()

        mock_obj.perform_module_operation.assert_called_once()
