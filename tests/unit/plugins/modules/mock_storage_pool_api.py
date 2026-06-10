# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Mock API helpers for storage_pool and storage_pool_info unit tests."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Sample data matching ObjectVarrayService response schemas
# ---------------------------------------------------------------------------

SAMPLE_POOL_1 = {
    'id': 'urn:storageos:VirtualArray:11111111-1111-1111-1111-111111111111',
    'name': 'sp_default',
    'description': 'Default storage pool',
    'isColdStorageEnabled': False,
    'isProtected': True,
    'numberOfDataBlocks': 12,
    'numberOfCodeBlocks': 4,
    'warningAlertAt': 70,
    'errorAlertAt': 85,
    'criticalAlertAt': 95,
    'status': 0,
    'label': 'HDD',
    'driveTechnology': 'HDD',
}

SAMPLE_POOL_2 = {
    'id': 'urn:storageos:VirtualArray:22222222-2222-2222-2222-222222222222',
    'name': 'sp_cold',
    'description': 'Cold storage pool',
    'isColdStorageEnabled': True,
    'isProtected': False,
    'numberOfDataBlocks': 12,
    'numberOfCodeBlocks': 4,
    'warningAlertAt': 80,
    'errorAlertAt': 90,
    'criticalAlertAt': 98,
    'status': 0,
    'label': 'SSD',
    'driveTechnology': 'SSD',
}

SAMPLE_POOL_UPDATED = {
    'id': 'urn:storageos:VirtualArray:11111111-1111-1111-1111-111111111111',
    'name': 'sp_default',
    'description': 'Updated by Ansible',
    'isColdStorageEnabled': False,
    'isProtected': True,
    'numberOfDataBlocks': 12,
    'numberOfCodeBlocks': 4,
    'warningAlertAt': 75,
    'errorAlertAt': 90,
    'criticalAlertAt': 98,
    'status': 0,
    'label': 'HDD',
    'driveTechnology': 'HDD',
}


def make_pool_mock(data):
    """Create a MagicMock that behaves like a pydantic model response."""
    mock = MagicMock()
    mock.to_dict.return_value = dict(data)
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


def make_list_response(pools=None):
    """Create a mock response for object_varray_service_get_virtual_arrays."""
    if pools is None:
        pools = [SAMPLE_POOL_1, SAMPLE_POOL_2]
    response = MagicMock()
    response.varray = [make_pool_mock(p) for p in pools]
    return response


def make_get_response(pool_data=None):
    """Create a mock response for object_varray_service_get_virtual_array."""
    if pool_data is None:
        pool_data = SAMPLE_POOL_1
    return make_pool_mock(pool_data)


def make_update_response(pool_data=None):
    """Create a mock response for object_varray_service_update_virtual_array."""
    if pool_data is None:
        pool_data = SAMPLE_POOL_UPDATED
    return make_pool_mock(pool_data)


class MockApiError(Exception):
    """Mock API exception that mimics objectscale_client ApiException."""

    def __init__(self, status, body='{"description": "test error"}'):
        super().__init__(body)
        self.status = status
        self.body = body


def make_api_error(status, body='{"description": "test error"}'):
    """Create a mock API exception with status and body."""
    return MockApiError(status, body)
