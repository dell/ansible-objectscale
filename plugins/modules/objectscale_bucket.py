#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing ObjectScale buckets"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: objectscale_bucket

version_added: '1.0.0'

short_description: Manage ObjectScale buckets

description:
- Manages the lifecycle of ObjectScale buckets, including creation, deletion, and configuration.

author:
- Dell Ansible Team (@dell)

options:
  objectscale_host: { type: str, required: true }
  objectscale_username: { type: str, required: true }
  objectscale_password: { type: str, required: true, no_log: true }
  validate_certs: { type: bool, default: true }
  name: { type: str, required: true }
  namespace: { type: str, required: true }
  state: { type: str, required: true, choices: ['present', 'absent'] }
  versioning: { type: bool, required: false }
  force: { type: bool, default: false, description: 'Force delete a non-empty bucket.' }
'''

EXAMPLES = r'''
- name: Create a bucket
  dellemc.objectscale.objectscale_bucket:
    objectscale_host: "{{ os_host }}"
    objectscale_username: "{{ os_user }}"
    objectscale_password: "{{ os_pass }}"
    validate_certs: false
    namespace: "my-namespace"
    name: "my-new-bucket"
    state: present
    versioning: true
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api import BucketApi

def main():
    module_params = utils.get_objectscale_management_host_parameters()
    module_params.update(
        name=dict(type='str', required=True),
        namespace=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=['present', 'absent']),
        versioning=dict(type='bool', required=False),
        force=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=module_params,
        supports_check_mode=True
    )

    result = {"changed": False}
    
    name = module.params['name']
    namespace = module.params['namespace']
    state = module.params['state']
    versioning = module.params.get('versioning')
    force = module.params['force']

    # Basic name validation
    if any(c.isupper() for c in name) or len(name) > 63:
        module.fail_json(msg="'InvalidBucketName': Bucket name is invalid.")

    try:
        api_client = utils.get_objectscale_connection(module.params)
        bucket_api = BucketApi(api_client)
        
        current_bucket = bucket_api.get_bucket(name, namespace)

        if state == 'present':
            if not current_bucket:
                if not module.check_mode:
                    bucket_api.create_bucket({'name': name, 'namespace': namespace})
                result['changed'] = True
            else:
                # Check for versioning update
                if versioning is not None and current_bucket.get('versioning') != versioning:
                    if not module.check_mode:
                        bucket_api.update_bucket_versioning(name, namespace, versioning)
                    result['changed'] = True

        elif state == 'absent':
            if current_bucket:
                if not module.check_mode:
                    try:
                        bucket_api.delete_bucket(name, namespace, force=force)
                    except Exception as e:
                        if 'BucketNotEmpty' in str(e):
                            module.fail_json(msg="'BucketNotEmpty': The bucket you tried to delete is not empty.")
                        raise
                result['changed'] = True

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Module failed: {str(e)}")

if __name__ == '__main__':
    main()
