# -*- coding: utf-8 -*-
# Copyright (c) 2024 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment:
    """Dell ObjectScale documentation fragments."""

    DOCUMENTATION = r'''
options:
  objectscale_host:
    description:
      - IP address or FQDN of the ObjectScale management endpoint.
    type: str
    required: true
  objectscale_port:
    description:
      - Port number for the ObjectScale management endpoint.
    type: int
    default: 4443
    required: false
  objectscale_username:
    description:
      - Username for authenticating with the ObjectScale management endpoint.
    type: str
    required: true
  objectscale_password:
    description:
      - Password for authenticating with the ObjectScale management endpoint.
    type: str
    required: true
  validate_certs:
    description:
      - Boolean value to enable or disable SSL certificate verification.
      - Set to C(false) when certificates are not trusted.
    type: bool
    default: true
    required: false
  timeout:
    description:
      - Timeout in seconds for HTTP requests to ObjectScale.
    type: int
    default: 30
    required: false
notes:
  - This module requires the ObjectScale Python client library.
  - The client library is included as part of the collection.
  - All operations are performed using the ObjectScale REST API.
  - SSL certificate verification can be disabled for testing environments.
requirements:
  - python >= 3.9
author:
  - Dell Ansible Team (@dell)
'''
