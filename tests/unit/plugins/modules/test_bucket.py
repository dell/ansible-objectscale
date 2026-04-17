# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the bucket module."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.bucket'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    name='test-bucket',
    namespace='test-ns',
    state='present',
    versioning=None,
    force=False,
)

MOCK_BUCKET = {'name': 'test-bucket', 'namespace': 'test-ns', 'versioning': False, 'tags': {}}


class TestBucketCreate:

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_create_bucket_when_not_exists(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_module.check_mode = False
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = None
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.create_bucket.assert_called_once_with({'name': 'test-bucket', 'namespace': 'test-ns'})
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_create_bucket_check_mode(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_module.check_mode = True
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = None
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.create_bucket.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_create_bucket_idempotent(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'versioning': None}
        mock_module.check_mode = False
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.create_bucket.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)


class TestBucketVersioning:

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_update_versioning(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'versioning': True}
        mock_module.check_mode = False
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.update_bucket_versioning.assert_called_once_with('test-bucket', 'test-ns', True)
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_update_versioning_check_mode(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'versioning': True}
        mock_module.check_mode = True
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.update_bucket_versioning.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_versioning_no_change(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'versioning': False}
        mock_module.check_mode = False
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.update_bucket_versioning.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)


class TestBucketDelete:

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_delete_bucket(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'state': 'absent'}
        mock_module.check_mode = False
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.delete_bucket.assert_called_once_with('test-bucket', 'test-ns', force=False)
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_delete_bucket_check_mode(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'state': 'absent'}
        mock_module.check_mode = True
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.delete_bucket.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_delete_bucket_not_exists(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'state': 'absent'}
        mock_module.check_mode = False
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = None
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_api_instance.delete_bucket.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_delete_bucket_not_empty(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'state': 'absent'}
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_instance.delete_bucket.side_effect = Exception("BucketNotEmpty")
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'BucketNotEmpty' in call_kwargs['msg']

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_delete_raises_other_exception(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'state': 'absent'}
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_instance.delete_bucket.side_effect = Exception("ServerError: internal error")
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'Module failed' in call_kwargs['msg']


class TestBucketValidation:

    @patch(f'{MODULE}.AnsibleModule')
    def test_invalid_name_uppercase(self, mock_am):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'name': 'TestBucket'}
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_am.return_value = mock_module

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'InvalidBucketName' in call_kwargs['msg']

    @patch(f'{MODULE}.AnsibleModule')
    def test_invalid_name_too_long(self, mock_am):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'name': 'a' * 64}
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_am.return_value = mock_module

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'InvalidBucketName' in call_kwargs['msg']


class TestBucketApiError:

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_api_connection_error(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_am.return_value = mock_module
        mock_conn.side_effect = Exception("Connection refused")

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'Module failed' in call_kwargs['msg']
        assert 'Connection refused' in call_kwargs['msg']


class TestBucketMain:

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_main_callable(self, mock_am, mock_conn, mock_api_cls):
        """Test that main() can be called directly (covers __main__ block)."""
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_module.check_mode = False
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket import main
        main()

        mock_module.exit_json.assert_called_once()
