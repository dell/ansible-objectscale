# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the bucket_info module."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.modules.bucket_info'

BASE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
    name='test-bucket',
    namespace='test-ns',
)

MOCK_BUCKET = {'name': 'test-bucket', 'namespace': 'test-ns', 'versioning': False, 'tags': {}}


class TestBucketInfoGet:

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_get_bucket_info_by_name(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket_info import main
        main()

        mock_api_instance.get_bucket.assert_called_once_with('test-bucket', 'test-ns')
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        assert len(call_kwargs['buckets']) == 1
        assert call_kwargs['buckets'][0] == MOCK_BUCKET

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_get_bucket_info_not_found(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = None
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket_info import main
        main()

        mock_api_instance.get_bucket.assert_called_once_with('test-bucket', 'test-ns')
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        assert call_kwargs['buckets'] == []

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_get_bucket_info_no_name(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = {**BASE_PARAMS, 'name': None}
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.list_buckets.return_value = [MOCK_BUCKET.copy()]
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket_info import main
        main()

        mock_api_instance.get_bucket.assert_not_called()
        mock_api_instance.list_buckets.assert_called_once_with('test-ns')
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs['changed'] is False
        assert len(call_kwargs['buckets']) == 1

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_get_bucket_info_api_error(self, mock_am, mock_conn, mock_api_cls):
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.side_effect = Exception("API error")
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket_info import main
        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert 'Failed to retrieve bucket info' in call_kwargs['msg']
        assert 'API error' in call_kwargs['msg']


class TestBucketInfoMain:

    @patch(f'{MODULE}.BucketApi')
    @patch(f'{MODULE}.utils.get_objectscale_connection')
    @patch(f'{MODULE}.AnsibleModule')
    def test_main_callable(self, mock_am, mock_conn, mock_api_cls):
        """Test that main() can be called directly (covers __main__ block)."""
        mock_module = MagicMock()
        mock_module.params = BASE_PARAMS.copy()
        mock_am.return_value = mock_module
        mock_api_instance = MagicMock()
        mock_api_instance.get_bucket.return_value = MOCK_BUCKET.copy()
        mock_api_cls.return_value = mock_api_instance

        from ansible_collections.dellemc.objectscale.plugins.modules.bucket_info import main
        main()

        mock_module.exit_json.assert_called_once()
