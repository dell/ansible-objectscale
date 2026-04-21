# Copyright: (c) 2026, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""API wrapper for ObjectScale S3 Bucket operations"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from typing import Any, Dict, Optional

# In a real implementation, this would import the actual API client
# from the objectscale_client package.
# For this simulation, we'll use a mock object.


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
            return response.to_dict()
        except Exception as e:
            if '404' in str(e) or 'Not Found' in str(e):
                return None
            raise

    def list_buckets(self, namespace: str) -> list:
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
            if hasattr(response, 'buckets') and response.buckets:
                return [b.to_dict() for b in response.buckets]
            return []
        except Exception as e:
            if '404' in str(e) or 'Not Found' in str(e):
                return []
            raise

    def create_bucket(self, payload: Dict[str, Any]) -> bool:
        """Creates a new bucket."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models import bucket_service_create_bucket_request as create_req
        api = generated_bucket_api.BucketApi(self.api_client)
        create_request = create_req.BucketServiceCreateBucketRequest(
            name=payload['name'],
            namespace=payload['namespace']
        )
        api.bucket_service_create_bucket(
            bucket_service_create_bucket_request=create_request
        )
        return True

    def delete_bucket(self, name: str, namespace: str, force: bool = False) -> bool:
        """Deletes a bucket."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
        api = generated_bucket_api.BucketApi(self.api_client)
        api.bucket_service_deactivate_bucket(
            bucket_name=name,
            namespace=namespace,
            force=force
        )
        return True

    def update_bucket_tagging(self, name: str, namespace: str, tags: Dict[str, str]) -> bool:
        """Updates the tags for a bucket."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.models import bucket_service_add_bucket_tags_request as tags_req
        api = generated_bucket_api.BucketApi(self.api_client)
        tag_list = [{'key': k, 'value': v} for k, v in tags.items()]
        tags_request = tags_req.BucketServiceAddBucketTagsRequest(
            tags=tag_list
        )
        api.bucket_service_add_bucket_tags(
            bucket_name=name,
            namespace=namespace,
            bucket_service_add_bucket_tags_request=tags_request
        )
        return True

    def update_bucket_versioning(self, name: str, namespace: str, enabled: bool) -> bool:
        """Updates the versioning status for a bucket."""
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api import bucket_api as generated_bucket_api
        api = generated_bucket_api.BucketApi(self.api_client)
        api.bucket_service_set_bucket_versioning(
            bucket_name=name,
            namespace=namespace,
            versioning_enabled=enabled
        )
        return True
