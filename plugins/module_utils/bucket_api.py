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
        Raises Exception for server/connection errors.
        """
        try:
            response = self.api_client.get(
                f'/object/bucket/{name}',
                params={'namespace': namespace}
            )
            if response is None:
                return None
            return response
        except Exception as e:
            if '404' in str(e) or 'Not Found' in str(e):
                return None
            raise

    def list_buckets(self, namespace: str) -> list:
        """Lists all buckets in a namespace.

        Returns a list of bucket detail dicts.
        """
        try:
            response = self.api_client.get(
                '/object/bucket',
                params={'namespace': namespace}
            )
            if response is None:
                return []
            if isinstance(response, list):
                return response
            return response.get('buckets', [])
        except Exception as e:
            if '404' in str(e) or 'Not Found' in str(e):
                return []
            raise

    def create_bucket(self, payload: Dict[str, Any]) -> bool:
        """Creates a new bucket."""
        self.api_client.post(
            '/object/bucket',
            json=payload
        )
        return True

    def delete_bucket(self, name: str, namespace: str, force: bool = False) -> bool:
        """Deletes a bucket."""
        params = {'namespace': namespace}
        if force:
            params['force'] = 'true'
        self.api_client.delete(
            f'/object/bucket/{name}',
            params=params
        )
        return True

    def update_bucket_tagging(self, name: str, namespace: str, tags: Dict[str, str]) -> bool:
        """Updates the tags for a bucket."""
        self.api_client.put(
            f'/object/bucket/{name}/tagging',
            params={'namespace': namespace},
            json={'tags': tags}
        )
        return True

    def update_bucket_versioning(self, name: str, namespace: str, enabled: bool) -> bool:
        """Updates the versioning status for a bucket."""
        self.api_client.put(
            f'/object/bucket/{name}/versioning',
            params={'namespace': namespace},
            json={'versioning_enabled': enabled}
        )
        return True
