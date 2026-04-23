#!/usr/bin/python
# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing ObjectScale buckets"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: bucket

version_added: '1.0.0'

short_description: Manage ObjectScale buckets

description:
- Manages the lifecycle of ObjectScale buckets, including creation, deletion, and configuration.

author:
- Dell Ansible Team (@dell)

options:
  objectscale_host:
    description: The hostname or IP address of the ObjectScale management host.
    type: str
    required: true
  objectscale_port:
    description: The port number of the ObjectScale management host.
    type: int
    required: false
    default: 4443
  objectscale_username:
    description: The username for authenticating with the ObjectScale management host.
    type: str
    required: true
  objectscale_password:
    description: The password for authenticating with the ObjectScale management host.
    type: str
    required: true
  validate_certs:
    description: Whether to validate SSL certificates.
    type: bool
    default: true
  timeout:
    description: The timeout in seconds for API requests.
    type: int
    default: 30
  name:
    description: The name of the bucket.
    type: str
    required: true
  namespace:
    description: The namespace of the bucket.
    type: str
    required: true
  state:
    description: The desired state of the bucket.
    type: str
    required: true
    choices: ['present', 'absent']
  versioning:
    description: Whether to enable versioning on the bucket.
    type: bool
    required: false
  force:
    description: Force delete a non-empty bucket.
    type: bool
    default: false
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
    returned: success
bucket_details:
    description: Details of the bucket.
    type: dict
    returned: when state is present
'''

# noqa: E402 - module level imports after documentation is standard for Ansible modules
from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api import BucketApi  # noqa: E402
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import (  # noqa: E402
    ApiException,
)

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils \
        import objectscale_client
except ImportError:
    objectscale_client = None  # type: ignore[assignment]


def _ensure_client_stub_compatibility() -> None:
    """Patch generated stubs for runtime compatibility when pydantic is absent.

    In environments without pydantic, generated stubs may map SecretStr to str.
    In that case, ApiClient treats normal strings as SecretStr and calls
    get_secret_value() on them, which fails. This runtime guard keeps behavior
    compatible without modifying generated module_utils code.
    """
    if objectscale_client is not None:
        secret_str_cls = getattr(objectscale_client, 'SecretStr', None)
        if secret_str_cls is str:
            class _CompatSecretStr(str):
                def get_secret_value(self) -> str:
                    return str(self)
            objectscale_client.SecretStr = _CompatSecretStr


def main():
    _ensure_client_stub_compatibility()
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

    if not name:
        module.fail_json(msg="missing required arguments: name")
    if not namespace:
        module.fail_json(msg="missing required arguments: namespace")

    # Basic name validation
    if any(c.isupper() for c in name) or len(name) > 63:
        module.fail_json(msg="'InvalidBucketName': Bucket name is invalid.")

    try:
        api_client = utils.get_objectscale_connection(module.params)
        bucket_api = BucketApi(api_client)

        current_bucket = bucket_api.get_bucket(name, namespace)

        if state == 'present':
            if not current_bucket:
                result['changed'] = True
                if not module.check_mode:
                    bucket_api.create_bucket(
                        {'name': name, 'namespace': namespace}
                    )
            else:
                if versioning is not None and \
                        current_bucket.get('versioning_status', '').lower() \
                        != ('enabled' if versioning else 'suspended'):
                    result['changed'] = True
                    if not module.check_mode:
                        bucket_api.update_bucket_versioning(
                            name, namespace, versioning
                        )

            if not module.check_mode:
                bucket_details = bucket_api.get_bucket(name, namespace)
                if bucket_details:
                    result['bucket_details'] = bucket_details

        elif state == 'absent':
            if current_bucket:
                result['changed'] = True
                if not module.check_mode:
                    try:
                        bucket_api.delete_bucket(
                            name, namespace, force=force
                        )
                    except ApiException as e:
                        if 'BucketNotEmpty' in str(e):
                            module.fail_json(
                                msg="'BucketNotEmpty': The bucket"
                                " you tried to delete is not"
                                " empty."
                            )
                        raise

    except ApiException as e:
        module.fail_json(msg=f"Module failed: {str(e)}")

    module.exit_json(**result)


if __name__ == '__main__':  # pragma: no cover
    main()
