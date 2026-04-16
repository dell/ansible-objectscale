# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Mock data and helpers for IAM Policy module unit tests."""

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

SAMPLE_POLICY_DOCUMENT_V2 = json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket", "s3:GetBucketLocation"],
            "Resource": "*"
        }
    ]
})

BASE_PARAMS = dict(
    objectscale_host='objectscale.example.test',
    objectscale_port=4443,
    objectscale_username='testuser',
    objectscale_password='***',  # noqa: test-fixture placeholder
    validate_certs=False,
    timeout=30,
    policy_name='TestPolicy',
    policy_arn=None,
    policy_document=SAMPLE_POLICY_DOCUMENT,
    description='Test IAM policy',
    path='/',
    namespace_name='testns',
    attach_entities=None,
    detach_entities=None,
    state='present',
)

MOCK_POLICY_DETAILS = {
    'GetPolicyResult': {
        'Policy': {
            'Arn': 'urn:ecs:iam::testns:policy/TestPolicy',
            'PolicyId': 'ANPA1234567890',
            'PolicyName': 'TestPolicy',
            'Description': 'Test IAM policy',
            'Path': '/',
            'DefaultVersionId': 'v1',
            'AttachmentCount': 0,
            'IsAttachable': True,
            'CreateDate': '2025-01-15T10:30:00Z',
            'UpdateDate': '2025-01-15T10:30:00Z',
        }
    }
}

MOCK_CREATE_POLICY_RESPONSE = {
    'CreatePolicyResult': {
        'Policy': {
            'Arn': 'urn:ecs:iam::testns:policy/TestPolicy',
            'PolicyId': 'ANPA1234567890',
            'PolicyName': 'TestPolicy',
            'Description': 'Test IAM policy',
            'Path': '/',
            'DefaultVersionId': 'v1',
            'AttachmentCount': 0,
            'IsAttachable': True,
            'CreateDate': '2025-01-15T10:30:00Z',
            'UpdateDate': '2025-01-15T10:30:00Z',
        }
    }
}

MOCK_POLICY_VERSION_RESPONSE = {
    'GetPolicyVersionResult': {
        'PolicyVersion': {
            'Document': SAMPLE_POLICY_DOCUMENT,
            'VersionId': 'v1',
            'IsDefaultVersion': True,
            'CreateDate': '2025-01-15T10:30:00Z',
        }
    }
}

MOCK_CREATE_VERSION_RESPONSE = {
    'CreatePolicyVersionResult': {
        'PolicyVersion': {
            'Document': SAMPLE_POLICY_DOCUMENT_V2,
            'VersionId': 'v2',
            'IsDefaultVersion': True,
            'CreateDate': '2025-01-16T10:30:00Z',
        }
    }
}
