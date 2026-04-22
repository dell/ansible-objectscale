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
    description: Username for authenticating with ObjectScale host.
    type: str
    required: true
  objectscale_password:
    description: Password for authenticating with ObjectScale host.
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
  namespace:
    description: The namespace of the bucket.
    type: str
    required: true
  name:
    description: Name of bucket to retrieve. If not provided,
                 all buckets in namespace are returned.
    type: str
    required: false
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
    returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils import (
    bucket_api
)
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import (
    ApiException,
)

BucketApi = bucket_api.BucketApi

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
        name=dict(type='str', required=False),
        namespace=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_params,
        supports_check_mode=True
    )

    result = {"changed": False, "buckets": []}

    namespace = module.params['namespace']
    bucket_name = module.params.get('name')

    if not namespace:
        module.exit_json(failed=True, msg="missing required arguments: namespace")

    try:
        api_client = utils.get_objectscale_connection(module.params)
        bucket_api = BucketApi(api_client)

        if bucket_name:
            bucket_details = bucket_api.get_bucket(
                bucket_name, namespace
            )
            if bucket_details:
                result['buckets'].append(bucket_details)
        else:
            result['buckets'] = bucket_api.list_buckets(
                namespace
            )

    except ApiException as e:
        module.exit_json(failed=True, msg=f"Failed to retrieve bucket info: {str(e)}")

    module.exit_json(**result)


if __name__ == '__main__':  # pragma: no cover
    main()
