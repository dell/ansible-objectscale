# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Mock data for storage_pool and storage_pool_info unit tests."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

BASE_PARAMS = dict(
    objectscale_host='objectscale.example.test',
    objectscale_port=4443,
    objectscale_username='testuser',
    objectscale_password='***',  # noqa: test-fixture placeholder
    validate_certs=False,
    timeout=30,
    state='present',
    storage_pool_name='sp_ansible_test',
    description='Test storage pool',
    is_cold_storage_enabled=False,
    warning_alert_at=70,
    error_alert_at=85,
)

SAMPLE_POOL = {
    'id': 'urn:storageos:VirtualArray:12345678-1234-1234-1234-123456789abc',
    'name': 'sp_ansible_test',
    'description': 'Test storage pool',
    'isProtected': False,
    'isColdStorageEnabled': False,
    'warningAlertAt': 70,
    'errorAlertAt': 85,
    'isRackProtected': False,
    'inactive': False,
}

SAMPLE_POOL_UPDATED = {
    'id': 'urn:storageos:VirtualArray:12345678-1234-1234-1234-123456789abc',
    'name': 'sp_ansible_test',
    'description': 'Updated description',
    'isProtected': False,
    'isColdStorageEnabled': True,
    'warningAlertAt': 60,
    'errorAlertAt': 90,
    'isRackProtected': False,
    'inactive': False,
}

LIST_POOLS_RESPONSE = {
    'varray': [
        {
            'id': 'urn:storageos:VirtualArray:12345678-1234-1234-1234-123456789abc',
            'name': 'sp_ansible_test',
            'description': 'Test storage pool',
            'isProtected': False,
            'isColdStorageEnabled': False,
            'warningAlertAt': 70,
            'errorAlertAt': 85,
        },
        {
            'id': 'urn:storageos:VirtualArray:87654321-4321-4321-4321-cba987654321',
            'name': 'sp_other',
            'description': 'Other pool',
            'isProtected': False,
            'isColdStorageEnabled': False,
            'warningAlertAt': 75,
            'errorAlertAt': 90,
        },
    ]
}
