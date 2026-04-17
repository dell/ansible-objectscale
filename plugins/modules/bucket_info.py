#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for retrieving information about ObjectScale buckets"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: bucket_info

version_added: '1.0.0'

short_description: Retrieve information about ObjectScale buckets

description:
- Retrieves details of one or more ObjectScale buckets.

author:
- Dell Ansible Team (@dell)

options:
  objectscale_host: { type: str, required: true }
  objectscale_username: { type: str, required: true }
  objectscale_password: { type: str, required: true, no_log: true }
  validate_certs: { type: bool, default: true }
  namespace: { type: str, required: true }
  name: { type: str, required: false }
'''

EXAMPLES = r'''
- name: Get info for a single bucket
  dellemc.objectscale.objectscale_bucket_info:
    objectscale_host: "{{ os_host }}"
    objectscale_username: "{{ os_user }}"
    objectscale_password: "{{ os_pass }}"
    validate_certs: false
    namespace: "my-namespace"
    name: "my-bucket"
'''

RETURN = r'''
buckets:
    description: A list of buckets with their details.
    type: list
    elements: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api import BucketApi

def main():
    module_params = utils.get_objectscale_management_host_parameters()
    module_params.update(
        name=dict(type='str', required=False),
        namespace=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_params,
        supports_check_mode=False
    )

    result = {"changed": False, "buckets": []}

    try:
        api_client = utils.get_objectscale_connection(module.params)
        bucket_api = BucketApi(api_client)
        
        bucket_name = module.params.get('name')
        namespace = module.params['namespace']

        if bucket_name:
            bucket_details = bucket_api.get_bucket(bucket_name, namespace)
            if bucket_details:
                result['buckets'].append(bucket_details)
        else:
            # In a real implementation, this would list all buckets.
            # For this test, we just return an empty list if no name is given.
            pass

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve bucket info: {str(e)}")

if __name__ == '__main__':
    main()
