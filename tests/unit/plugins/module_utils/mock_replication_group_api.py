# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Mock data for replication_group and replication_group_info unit tests."""

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
    id=None,
    name='rg-test-1',
    new_name=None,
    description='replication-group-created-by-tests',
    replication_type='active',
    mappings=[
        {
            'vdc_id': 'urn:storageos:VirtualDataCenterData:111',
            'storage_pool_id': 'urn:storageos:VirtualArray:111',
            'is_replication_target': False,
        }
    ],
    replicate_to_all_sites=False,
    enable_rebalancing=None,
    skip_bootstrap_check=False,
    force_pso_zones=False,
)

SAMPLE_RG = {
    'id': 'urn:storageos:ReplicationGroupInfo:111:global',
    'name': 'rg-test-1',
    'description': 'replication-group-created-by-tests',
    'enable_rebalancing': False,
    'isAllowAllNamespaces': False,
    'isFullRep': True,
    'use_replication_target': False,
    'varrayMappings': [
        {
            'name': 'urn:storageos:VirtualDataCenterData:111',
            'value': 'urn:storageos:VirtualArray:111',
            'is_replication_target': False,
        }
    ],
}

SAMPLE_RG_UPDATED = {
    'id': 'urn:storageos:ReplicationGroupInfo:111:global',
    'name': 'rg-test-1-renamed',
    'description': 'updated-description',
    'enable_rebalancing': True,
    'isAllowAllNamespaces': True,
    'isFullRep': False,
    'use_replication_target': True,
    'varrayMappings': [
        {
            'name': 'urn:storageos:VirtualDataCenterData:111',
            'value': 'urn:storageos:VirtualArray:111',
            'is_replication_target': True,
        }
    ],
}

LIST_RG_RESPONSE = {
    'data_service_vpool': [
        {
            'id': 'urn:storageos:ReplicationGroupInfo:111:global',
            'name': 'rg-test-1',
            'description': 'replication-group-created-by-tests',
        },
        {
            'id': 'urn:storageos:ReplicationGroupInfo:222:global',
            'name': 'rg-test-2',
            'description': 'second-rg',
        },
    ]
}
