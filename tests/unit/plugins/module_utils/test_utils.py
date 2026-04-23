# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import sys
import types
import pytest
from unittest.mock import MagicMock, patch

# Ensure urllib3 is importable even when not installed (CI has no urllib3).
# This lets @patch('urllib3.PoolManager') work regardless.
if 'urllib3' not in sys.modules:
    _urllib3 = types.ModuleType('urllib3')
    _urllib3.PoolManager = MagicMock
    _urllib3.disable_warnings = MagicMock()
    _urllib3_exc = types.ModuleType('urllib3.exceptions')
    _urllib3_exc.InsecureRequestWarning = type('InsecureRequestWarning', (Warning,), {})
    _urllib3.exceptions = _urllib3_exc
    sys.modules['urllib3'] = _urllib3
    sys.modules['urllib3.exceptions'] = _urllib3_exc

UTILS = 'ansible_collections.dellemc.objectscale.plugins.module_utils.utils'

MODULE_PARAMS = dict(
    objectscale_host='10.0.0.1',
    objectscale_port=4443,
    objectscale_username='admin',
    objectscale_password='secret',
    validate_certs=False,
    timeout=30,
)


class TestGetObjectscaleManagementHostParameters:

    def test_returns_all_keys(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_management_host_parameters
        )
        result = get_objectscale_management_host_parameters()
        assert set(result.keys()) == {
            'objectscale_host', 'objectscale_port', 'objectscale_username',
            'objectscale_password', 'validate_certs', 'timeout'
        }

    def test_required_fields(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_management_host_parameters
        )
        result = get_objectscale_management_host_parameters()
        assert result['objectscale_host']['required'] is True
        assert result['objectscale_username']['required'] is True
        assert result['objectscale_password']['required'] is True
        assert result['objectscale_password']['no_log'] is True

    def test_defaults(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_management_host_parameters
        )
        result = get_objectscale_management_host_parameters()
        assert result['objectscale_port']['default'] == 4443
        assert result['validate_certs']['default'] is True
        assert result['timeout']['default'] == 30


class TestGetObjectscaleConnection:

    def _make_mock_http(self, status=200, token='test-token'):
        mock_resp = MagicMock()
        mock_resp.status = status
        mock_resp.headers = {'X-SDS-AUTH-TOKEN': token}
        mock_resp.data = b'ok'
        mock_http = MagicMock()
        mock_http.request.return_value = mock_resp
        return mock_http, mock_resp

    @patch(f'{UTILS}.objectscale_client')
    @patch('urllib3.PoolManager')
    @patch('urllib3.disable_warnings')
    def test_success(self, mock_disable, mock_pool_cls, mock_client):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_connection
        )
        mock_http, mock_resp = self._make_mock_http(status=200, token='tok123')
        mock_pool_cls.return_value = mock_http

        mock_config = MagicMock()
        mock_client.Configuration.return_value = mock_config
        mock_api_client = MagicMock()
        mock_client.ApiClient.return_value = mock_api_client

        result = get_objectscale_connection(MODULE_PARAMS)

        assert result is mock_api_client
        assert mock_config.api_key == {'AuthToken': 'tok123'}
        mock_disable.assert_called_once()

    @patch('urllib3.PoolManager')
    @patch('urllib3.disable_warnings')
    def test_login_http_failure_raises(self, mock_disable, mock_pool_cls):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_connection
        )
        mock_http, mock_resp = self._make_mock_http(status=401)
        mock_resp.data = b'Unauthorized'
        mock_pool_cls.return_value = mock_http

        with pytest.raises(Exception, match="ObjectScale login failed"):
            get_objectscale_connection(MODULE_PARAMS)

    @patch('urllib3.PoolManager')
    @patch('urllib3.disable_warnings')
    def test_missing_token_raises(self, mock_disable, mock_pool_cls):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_connection
        )
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {}  # No token
        mock_http = MagicMock()
        mock_http.request.return_value = mock_resp
        mock_pool_cls.return_value = mock_http

        with pytest.raises(Exception, match="X-SDS-AUTH-TOKEN was absent"):
            get_objectscale_connection(MODULE_PARAMS)

    @patch('urllib3.PoolManager')
    @patch('urllib3.disable_warnings')
    def test_no_objectscale_client_raises(self, mock_disable, mock_pool_cls):
        from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
        mock_http, mock_resp = self._make_mock_http(status=200, token='tok')
        mock_pool_cls.return_value = mock_http

        original = utils.objectscale_client
        try:
            utils.objectscale_client = None
            with pytest.raises(RuntimeError, match="objectscale_client is not available"):
                utils.get_objectscale_connection(MODULE_PARAMS)
        finally:
            utils.objectscale_client = original

    @patch(f'{UTILS}.objectscale_client')
    @patch('urllib3.PoolManager')
    @patch('urllib3.disable_warnings')
    def test_validate_certs_true(self, mock_disable, mock_pool_cls, mock_client):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_connection
        )
        params = {**MODULE_PARAMS, 'validate_certs': True}
        mock_http, _mock_resp = self._make_mock_http(status=200, token='tok')
        mock_pool_cls.return_value = mock_http
        mock_client.Configuration.return_value = MagicMock()
        mock_client.ApiClient.return_value = MagicMock()

        get_objectscale_connection(params)

        pool_call_kwargs = mock_pool_cls.call_args[1]
        assert pool_call_kwargs['cert_reqs'] == 'CERT_REQUIRED'

    @patch(f'{UTILS}.objectscale_client')
    @patch('urllib3.PoolManager')
    @patch('urllib3.disable_warnings')
    def test_validate_certs_false(self, mock_disable, mock_pool_cls, mock_client):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            get_objectscale_connection
        )
        params = {**MODULE_PARAMS, 'validate_certs': False}
        mock_http, _mock_resp = self._make_mock_http(status=200, token='tok')
        mock_pool_cls.return_value = mock_http
        mock_client.Configuration.return_value = MagicMock()
        mock_client.ApiClient.return_value = MagicMock()

        get_objectscale_connection(params)

        pool_call_kwargs = mock_pool_cls.call_args[1]
        assert pool_call_kwargs['cert_reqs'] == 'CERT_NONE'


class TestDetermineError:

    def test_with_json_body_with_description(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            determine_error
        )
        err = Exception("something")
        err.body = json.dumps({'description': 'Quota exceeded'}).encode()

        result = determine_error(err)

        assert result == 'Quota exceeded'

    def test_with_json_body_without_description(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            determine_error
        )
        err = Exception("something")
        err.body = json.dumps({'code': 404}).encode()

        result = determine_error(err)

        # Falls back to str(body)
        assert '404' in result

    def test_with_non_json_body(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            determine_error
        )
        err = Exception("something")
        err.body = b'plain text error'

        result = determine_error(err)

        assert 'plain text error' in result

    def test_without_body(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            determine_error
        )
        err = Exception("bare exception message")

        result = determine_error(err)

        assert result == 'bare exception message'

    def test_body_is_none(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            determine_error
        )
        err = Exception("no body attr")
        err.body = None

        result = determine_error(err)

        assert result == 'no body attr'


class TestPaginateWithNextMarker:

    def _make_mock_response(self, items, next_marker=None):
        """Helper to create a mock response with items and optional NextMarker."""
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            'namespace': items,
            'NextMarker': next_marker
        }
        return mock_response

    def test_single_page(self):
        """Test pagination when all items fit on one page."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            paginate_with_next_marker
        )

        mock_api_call = MagicMock()
        mock_api_call.return_value = self._make_mock_response(
            items=[{'id': '1', 'name': 'ns1'}, {'id': '2', 'name': 'ns2'}],
            next_marker=None
        )

        result = paginate_with_next_marker(
            api_call=mock_api_call,
            base_kwargs={'namespace': 'ns1'},
            items_key='namespace'
        )

        assert len(result) == 2
        assert result[0]['name'] == 'ns1'
        assert result[1]['name'] == 'ns2'
        mock_api_call.assert_called_once_with(namespace='ns1')

    def test_multiple_pages(self):
        """Test pagination across multiple pages."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            paginate_with_next_marker
        )

        call_count = [0]

        def mock_api_call(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return self._make_mock_response(
                    items=[{'id': '1', 'name': 'ns1'}],
                    next_marker='marker1'
                )
            elif call_count[0] == 2:
                return self._make_mock_response(
                    items=[{'id': '2', 'name': 'ns2'}],
                    next_marker='marker2'
                )
            else:
                return self._make_mock_response(
                    items=[{'id': '3', 'name': 'ns3'}],
                    next_marker=None
                )

        result = paginate_with_next_marker(
            api_call=mock_api_call,
            base_kwargs={'namespace': 'ns1'},
            items_key='namespace'
        )

        assert len(result) == 3
        assert result[0]['name'] == 'ns1'
        assert result[1]['name'] == 'ns2'
        assert result[2]['name'] == 'ns3'
        assert call_count[0] == 3

    def test_marker_passed_to_subsequent_calls(self):
        """Test that marker is correctly passed to subsequent API calls."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            paginate_with_next_marker
        )

        call_kwargs = []

        def mock_api_call(**kwargs):
            call_kwargs.append(kwargs.copy())
            if len(call_kwargs) == 1:
                return self._make_mock_response(
                    items=[{'id': '1'}],
                    next_marker='marker1'
                )
            else:
                return self._make_mock_response(
                    items=[{'id': '2'}],
                    next_marker=None
                )

        paginate_with_next_marker(
            api_call=mock_api_call,
            base_kwargs={'namespace': 'ns1'},
            items_key='namespace'
        )

        assert call_kwargs[0] == {'namespace': 'ns1'}
        assert call_kwargs[1] == {'namespace': 'ns1', 'marker': 'marker1'}

    def test_empty_response(self):
        """Test pagination when API returns empty items."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            paginate_with_next_marker
        )

        mock_api_call = MagicMock()
        mock_api_call.return_value = self._make_mock_response(
            items=[],
            next_marker=None
        )

        result = paginate_with_next_marker(
            api_call=mock_api_call,
            base_kwargs={'namespace': 'ns1'},
            items_key='namespace'
        )

        assert result == []

    def test_base_kwargs_preserved(self):
        """Test that base_kwargs are preserved in all API calls."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import (
            paginate_with_next_marker
        )

        call_kwargs = []

        def mock_api_call(**kwargs):
            call_kwargs.append(kwargs.copy())
            return self._make_mock_response(
                items=[{'id': '1'}],
                next_marker=None
            )

        paginate_with_next_marker(
            api_call=mock_api_call,
            base_kwargs={'namespace': 'ns1', 'filter': 'active'},
            items_key='namespace'
        )

        assert call_kwargs[0] == {'namespace': 'ns1', 'filter': 'active'}
