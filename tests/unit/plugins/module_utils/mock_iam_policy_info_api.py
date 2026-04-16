# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Mock data and helpers for IAM Policy Info module unit tests."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

SAMPLE_POLICY_DOCUMENT = json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": "*"
        }
    ]
})

BASE_PARAMS = dict(
    objectscale_host='objectscale.example.test',
    objectscale_port=4443,
    objectscale_username='testuser',
    objectscale_password='***',
    validate_certs=False,
    timeout=30,
    policy_name=None,
    policy_arn=None,
    namespace_name='testns',
    include_policy_document=False,
    include_versions=False,
    policy_scope=None,
    only_attached=False,
)

MOCK_POLICY_1 = {
    'Arn': 'urn:ecs:iam::testns:policy/TestPolicy1',
    'PolicyId': 'ANPA1111111111',
    'PolicyName': 'TestPolicy1',
    'Description': 'First test policy',
    'Path': '/',
    'DefaultVersionId': 'v1',
    'AttachmentCount': 0,
    'IsAttachable': True,
    'CreateDate': '2025-01-15T10:30:00Z',
    'UpdateDate': '2025-01-15T10:30:00Z',
}

MOCK_POLICY_2 = {
    'Arn': 'urn:ecs:iam::testns:policy/TestPolicy2',
    'PolicyId': 'ANPA2222222222',
    'PolicyName': 'TestPolicy2',
    'Description': 'Second test policy',
    'Path': '/',
    'DefaultVersionId': 'v2',
    'AttachmentCount': 3,
    'IsAttachable': True,
    'CreateDate': '2025-02-10T08:00:00Z',
    'UpdateDate': '2025-03-01T12:00:00Z',
}

MOCK_GET_POLICY_RESPONSE = {
    'GetPolicyResult': {
        'Policy': MOCK_POLICY_1,
    }
}

MOCK_LIST_POLICIES_RESPONSE = {
    'ListPoliciesResult': {
        'Policies': [MOCK_POLICY_1, MOCK_POLICY_2],
        'IsTruncated': False,
        'Marker': None,
    }
}

MOCK_LIST_POLICIES_PAGE1 = {
    'ListPoliciesResult': {
        'Policies': [MOCK_POLICY_1],
        'IsTruncated': True,
        'Marker': 'page2marker',
    }
}

MOCK_LIST_POLICIES_PAGE2 = {
    'ListPoliciesResult': {
        'Policies': [MOCK_POLICY_2],
        'IsTruncated': False,
        'Marker': None,
    }
}

MOCK_POLICY_VERSION_V1 = {
    'GetPolicyVersionResult': {
        'PolicyVersion': {
            'Document': SAMPLE_POLICY_DOCUMENT,
            'VersionId': 'v1',
            'IsDefaultVersion': True,
            'CreateDate': '2025-01-15T10:30:00Z',
        }
    }
}

MOCK_LIST_VERSIONS_RESPONSE = {
    'ListPolicyVersionsResult': {
        'Versions': [
            {
                'VersionId': 'v1',
                'IsDefaultVersion': False,
                'CreateDate': '2025-01-15T10:30:00Z',
            },
            {
                'VersionId': 'v2',
                'IsDefaultVersion': True,
                'CreateDate': '2025-03-01T12:00:00Z',
            },
        ],
        'IsTruncated': False,
        'Marker': None,
    }
}
