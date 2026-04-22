# -*- coding: utf-8 -*-
# Copyright (c) 2026 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: replication_group_info
short_description: Gather ObjectScale replication group information
description:
  - Retrieve ObjectScale replication group details by id, by name, or list all.
version_added: "1.0.0"
author:
- Dell Ansible Team (@dell) <ansible.team@dell.com>

attributes:
  check_mode:
    support: full
    description: Supports check mode. This is a read-only info module.

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
  timeout:
    description:
    - Timeout in seconds for HTTP requests to the ObjectScale management endpoint.
    type: int
    default: 30
  id:
    description:
    - Replication group identifier (URN).
    type: str
  name:
    description:
    - Replication group name.
    type: str
  fetch_full_details:
    description:
    - Fetch full details for each matched replication group.
    type: bool
    default: true
'''

EXAMPLES = r'''
- name: List all replication groups
  dellemc.objectscale.replication_group_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false

- name: Get replication group by id
  dellemc.objectscale.replication_group_info:
    objectscale_host: "{{ objectscale_host }}"
    objectscale_username: "{{ objectscale_username }}"
    objectscale_password: "{{ objectscale_password }}"
    validate_certs: false
    id: urn:storageos:ReplicationGroupInfo:111:global
'''

RETURN = r'''
changed:
  description: Always false for info module.
  type: bool
  returned: always
replication_groups:
  description: List of replication groups.
  type: list
  elements: dict
  returned: always
'''

from typing import Any, Dict, List, Optional

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.objectscale.plugins.module_utils import utils
from ansible_collections.dellemc.objectscale.plugins.module_utils.utils import HAS_OBJECTSCALE_CLIENT

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.data_vpool_api import (
        DataVpoolApi,
    )
except (ImportError, Exception):
    DataVpoolApi = None  # type: ignore[assignment,misc]


class ReplicationGroupInfo(object):
    """Class for gathering replication group info from ObjectScale."""

    def __init__(self) -> None:
        self.module_params = utils.get_objectscale_management_host_parameters()
        self.module_params.update(self.get_replication_group_info_parameters())

        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=True,
        )

        if not HAS_OBJECTSCALE_CLIENT:
            self.module.exit_json(
                failed=True,
                msg="The objectscale_client Python package is required. "
                    "Install it with: pip install pydantic urllib3 python-dateutil"
            )
            return

        if DataVpoolApi is None:
            self.module.exit_json(
                failed=True,
                msg="ObjectScale DataVpool API client is unavailable. Rebuild/install objectscale_client."
            )
            return

        try:
            self.api_client = utils.get_objectscale_connection(self.module.params)
            self.data_vpool_api = DataVpoolApi(self.api_client)
        except Exception as e:
            self.module.exit_json(failed=True, msg="Failed to connect to ObjectScale: %s" % str(e))
            return

    @staticmethod
    def _to_dict(response: Any) -> Dict[str, Any]:
        if response is None:
            return {}
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        if isinstance(response, dict):
            return response
        return {}

    def get_by_id(self, rg_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.data_vpool_api.data_service_vpool_service_get_data_service_store(id=rg_id)
            data = self._to_dict(response)
            # Some ObjectScale builds return an empty object (200) for unknown ids.
            if not data:
                return None
            if not data.get('id') and not data.get('name') and not data.get('description'):
                return None
            return data
        except Exception as e:
            status = getattr(e, 'status', None)
            if str(status) in ('404', '400'):
                return None
            error_msg = utils.determine_error(e)
            self.module.exit_json(failed=True, msg="Getting replication group %s failed with error: %s" % (rg_id, error_msg))
            return None

    def list_all(self) -> List[Dict[str, Any]]:
        try:
            response = self.data_vpool_api.data_service_vpool_service_get_data_service_vpools()
            data = self._to_dict(response)
            return data.get('data_service_vpool', []) or []
        except Exception as e:
            error_msg = utils.determine_error(e)
            self.module.exit_json(failed=True, msg="Listing replication groups failed with error: %s" % error_msg)
            return []

    def perform_module_operation(self) -> None:
        rg_id = self.module.params.get('id')
        rg_name = self.module.params.get('name')
        fetch_full = self.module.params.get('fetch_full_details')

        if rg_id and rg_name:
            self.module.exit_json(failed=True, msg="Parameters 'id' and 'name' are mutually exclusive")
            return

        result_items: List[Dict[str, Any]] = []

        if rg_id:
            details = self.get_by_id(rg_id)
            if details:
                result_items = [details]
        else:
            listed = self.list_all()
            if rg_name:
                listed = [item for item in listed if item.get('name') == rg_name]
                if len(listed) > 1:
                    self.module.exit_json(failed=True, msg="Multiple replication groups found for name '%s'. Use id." % rg_name)
                    return

            if fetch_full:
                for item in listed:
                    item_id = item.get('id')
                    if item_id:
                        detailed = self.get_by_id(item_id)
                        if detailed:
                            result_items.append(detailed)
                    else:
                        result_items.append(item)
            else:
                result_items = listed

        self.module.exit_json(changed=False, replication_groups=result_items)

    @staticmethod
    def get_replication_group_info_parameters() -> Dict[str, Dict[str, Any]]:
        return dict(
            id=dict(type='str'),
            name=dict(type='str'),
            fetch_full_details=dict(type='bool', default=True),
        )


def main() -> None:
    obj = ReplicationGroupInfo()
    obj.perform_module_operation()


if __name__ == '__main__':
    main()
