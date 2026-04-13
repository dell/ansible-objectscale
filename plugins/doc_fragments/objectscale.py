# -*- coding: utf-8 -*-
# Copyright (c) 2024 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class AnsibleDellObjectScaleDocFragments:
    """
    Dell ObjectScale documentation fragments
    """

    def __init__(self):
        pass

    @staticmethod
    def get_documentation():
        """
        Return documentation fragments for ObjectScale modules
        """
        return {
            'doc_fragments': [
                {
                    'name': 'dellemc.objectscale',
                    'description': 'Dell ObjectScale Ansible Collection',
                    'content': {
                        'options': {
                            'objectscale_host': {
                                'description': [
                                    'IP address or FQDN of the ObjectScale management endpoint.'
                                ],
                                'type': 'str',
                                'required': True
                            },
                            'objectscale_port': {
                                'description': [
                                    'Port number for the ObjectScale management endpoint.'
                                ],
                                'type': 'int',
                                'default': 443,
                                'required': False
                            },
                            'objectscale_username': {
                                'description': [
                                    'Username for authenticating with the ObjectScale management endpoint.'
                                ],
                                'type': 'str',
                                'required': True
                            },
                            'objectscale_password': {
                                'description': [
                                    'Password for authenticating with the ObjectScale management endpoint.'
                                ],
                                'type': 'str',
                                'required': True,
                                'no_log': True
                            },
                            'validate_certs': {
                                'description': [
                                    'Boolean value to enable or disable SSL certificate verification.',
                                    'Set to False when certificates are not trusted.'
                                ],
                                'type': 'bool',
                                'default': True,
                                'required': False
                            },
                            'timeout': {
                                'description': [
                                    'Timeout in seconds for HTTP requests to ObjectScale.'
                                ],
                                'type': 'int',
                                'default': 30,
                                'required': False
                            }
                        },
                        'notes': [
                            'This module requires the objectscale-sdk Python package.',
                            'The objectscale-sdk is an integrated OpenAPI-generated library.',
                            'All operations are performed using the ObjectScale REST API.',
                            'SSL certificate verification can be disabled for testing environments.'
                        ],
                        'requirements': [
                            'python >= 3.6',
                            'objectscale-sdk >= 1.0.0'
                        ],
                        'author': [
                            'Dell Ansible Team (@dell)'
                        ],
                        'version_added': '1.0.0'
                    }
                }
            ]
        }
