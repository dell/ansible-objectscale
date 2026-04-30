# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""API wrapper for ObjectScale S3 Bucket operations"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from typing import Any, Dict, List, Optional

from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import (
    ApiException,
    NotFoundException,
)


class BucketApi:
    """A wrapper class for ObjectScale S3 bucket API calls."""

    def __init__(self, api_client: Any) -> None:
        """Initialize the BucketApi with an authenticated API client."""
        self.api_client = api_client

    def get_bucket(self, name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Fetches details for a given bucket.

        Returns bucket details dict if found, None if not found.
        """
        try:
            from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
            api = generated_bucket_api.BucketApi(self.api_client)
            response = api.bucket_service_get_bucket_info(
                bucket_name=name,
                namespace=namespace
            )
            if response is None:
                return None
            result = response.to_dict()
            if not result or not result.get('name'):
                return None
            return result
        except NotFoundException:
            return None
        except ApiException as e:
            if e.status == 404:
                return None
            # ObjectScale returns HTTP 400 with specific error codes for 'not found'
            # Code 1004: "Request parameter cannot be found"
            # Code 1013: "Bad request body" (entity not found)
            if e.status == 400 and e.data:
                error_code = e.data.get('code') if isinstance(e.data, dict) else None
                if error_code in (1004, 1013):
                    return None
            raise

    def list_buckets(self, namespace: str) -> List[Dict[str, Any]]:
        """Lists all buckets in a namespace.

        Returns a list of bucket detail dicts.
        """
        try:
            from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
            api = generated_bucket_api.BucketApi(self.api_client)
            response = api.bucket_service_get_buckets(
                namespace=namespace
            )
            if response is None:
                return []
            if hasattr(response, 'object_bucket') and response.object_bucket:
                # Handle both dict and object responses
                buckets = []
                for b in response.object_bucket:
                    if isinstance(b, dict):
                        buckets.append(b)
                    elif hasattr(b, 'to_dict'):
                        buckets.append(b.to_dict())
                    else:
                        buckets.append(b)
                return buckets
            return []
        except NotFoundException:
            return []
        except ApiException as e:
            if e.status == 404:
                return []
            raise

    def create_bucket(self, payload: Dict[str, Any]) -> bool:
        """Creates a new bucket.

        Uses the generated client first. If that fails with a 500 error,
        falls back to a direct REST call to ``/object/bucket.json`` for
        compatibility with older ObjectScale versions.
        """
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models import bucket_service_create_bucket_request as create_req
        api = generated_bucket_api.BucketApi(self.api_client)
        create_kwargs = {
            'name': payload['name'],
            'namespace': payload['namespace'],
        }
        if payload.get('vpool'):
            create_kwargs['vpool'] = payload['vpool']
        create_request = create_req.BucketServiceCreateBucketRequest(
            **create_kwargs
        )
        try:
            api.bucket_service_create_bucket(
                bucket_service_create_bucket_request=create_request
            )
        except ApiException as e:
            if e.status == 500:
                # Fallback: older ObjectScale may need .json suffix
                self._create_bucket_fallback(payload)
            else:
                raise
        return True

    def _create_bucket_fallback(self, payload: Dict[str, Any]) -> None:
        """Direct REST fallback for bucket creation on older ObjectScale."""
        import json as _json
        import urllib3
        urllib3.disable_warnings()

        body = {'name': payload['name'], 'namespace': payload['namespace']}
        if payload.get('vpool'):
            body['vpool'] = payload['vpool']

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        auth_token = self.api_client.configuration.api_key.get('AuthToken')
        if auth_token:
            headers['X-SDS-AUTH-TOKEN'] = auth_token

        url = self.api_client.configuration.host + '/object/bucket.json'
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        resp = http.request(
            'POST', url,
            body=_json.dumps(body).encode('utf-8'),
            headers=headers,
        )
        if resp.status >= 400:
            resp_body = resp.data.decode('utf-8') if resp.data else ''
            raise ApiException(
                status=resp.status,
                reason=resp_body or 'Fallback bucket creation failed',
            )

    def delete_bucket(self, name: str, namespace: str, force: bool = False) -> bool:
        """Deletes a bucket."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
        api = generated_bucket_api.BucketApi(self.api_client)
        empty_bucket = 'true' if force else None
        api.bucket_service_deactivate_bucket(
            bucket_name=name,
            namespace=namespace,
            empty_bucket=empty_bucket
        )
        return True

    def update_bucket_tagging(self, name: str, namespace: str, tags: Dict[str, str]) -> bool:
        """Updates the tags for a bucket."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api \
            import bucket_api as generated_bucket_api
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.bucket_service_add_bucket_tags_request \
            import BucketServiceAddBucketTagsRequest
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.bucket_service_create_bucket_request_tag_set_inner \
            import BucketServiceCreateBucketRequestTagSetInner
        api = generated_bucket_api.BucketApi(self.api_client)
        tag_list = [
            BucketServiceCreateBucketRequestTagSetInner(key=k, value=v)
            for k, v in tags.items()
        ]
        tags_request = BucketServiceAddBucketTagsRequest(
            tag_set=tag_list
        )
        api.bucket_service_add_bucket_tags(
            bucket_name=name,
            bucket_service_add_bucket_tags_request=tags_request
        )
        return True

    def update_bucket_versioning(self, name: str, namespace: str, enabled: bool) -> bool:
        """Updates the versioning status for a bucket."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api \
            import bucket_api as generated_bucket_api
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models.bucket_service_set_bucket_versioning_request \
            import BucketServiceSetBucketVersioningRequest
        api = generated_bucket_api.BucketApi(self.api_client)
        status = 'Enabled' if enabled else 'Suspended'
        versioning_request = BucketServiceSetBucketVersioningRequest(
            status=status
        )
        api.bucket_service_set_bucket_versioning(
            bucket_name=name,
            bucket_service_set_bucket_versioning_request=versioning_request,
            namespace=namespace
        )
        return True
