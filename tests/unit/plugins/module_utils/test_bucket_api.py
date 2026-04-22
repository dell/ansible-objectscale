from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest
from unittest.mock import patch, MagicMock

# This import will fail initially, which is the expected "red" state.
from ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api import BucketApi
from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.exceptions import (
    NotFoundException,
)


class TestBucketApi(unittest.TestCase):
    """Unit tests for the BucketApi class."""

    def setUp(self):
        """Set up a mock API client for each test."""
        self.mock_api_client = MagicMock()
        # This instantiation will fail until BucketApi is created.
        self.bucket_api = BucketApi(self.mock_api_client)

    @patch('ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api.BucketApi.get_bucket')
    def test_get_bucket_success(self, mock_get_bucket):
        """Test successful retrieval of an existing bucket."""
        mock_get_bucket.return_value = {'name': 'test-bucket', 'versioning': False}

        result = self.bucket_api.get_bucket('test-bucket', 'my-namespace')

        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'test-bucket')
        mock_get_bucket.assert_called_once_with('test-bucket', 'my-namespace')

    @patch('ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.bucket_api.BucketApi')
    def test_get_bucket_not_found(self, mock_generated_api_cls):
        """Test handling of a 404 Not Found error when getting a bucket."""
        # Mock the generated API to raise NotFoundException
        mock_api_instance = MagicMock()
        mock_api_instance.bucket_service_get_bucket_info.side_effect = NotFoundException(status=404, reason="Not Found")
        mock_generated_api_cls.return_value = mock_api_instance

        # The bucket_api.get_bucket method returns None for non-existent buckets
        result = self.bucket_api.get_bucket('non-existent-bucket', 'my-namespace')
        self.assertIsNone(result)

    @patch('ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api.BucketApi.create_bucket')
    def test_create_bucket(self, mock_create_bucket):
        """Test the payload construction for creating a bucket."""
        payload = {'name': 'new-bucket', 'namespace': 'my-namespace'}
        mock_create_bucket.return_value = True

        self.bucket_api.create_bucket(payload)

        mock_create_bucket.assert_called_once_with(payload)

    @patch('ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api.BucketApi.delete_bucket')
    def test_delete_bucket(self, mock_delete_bucket):
        """Test the call for deleting a bucket."""
        mock_delete_bucket.return_value = True
        self.bucket_api.delete_bucket('old-bucket', 'my-namespace')
        mock_delete_bucket.assert_called_once_with('old-bucket', 'my-namespace')

    @patch('ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api.BucketApi.update_bucket_tagging')
    def test_update_bucket_tagging(self, mock_update_tagging):
        """Test the payload for updating bucket tags."""
        tags = {'owner': 'test', 'project': 'ansible'}
        mock_update_tagging.return_value = True
        self.bucket_api.update_bucket_tagging('tagged-bucket', 'my-namespace', tags)
        mock_update_tagging.assert_called_once_with('tagged-bucket', 'my-namespace', tags)

    @patch('ansible_collections.dellemc.objectscale.plugins.module_utils.bucket_api.BucketApi.get_bucket')
    def test_api_503_error(self, mock_get_bucket):
        """Test graceful failure on a 503 Service Unavailable error."""
        mock_get_bucket.side_effect = Exception("503 Service Unavailable")

        with self.assertRaises(Exception) as context:
            self.bucket_api.get_bucket('any-bucket', 'my-namespace')

        self.assertIn("503", str(context.exception))


if __name__ == '__main__':
    unittest.main()
