""" import objectscale client (OpenAPI generated, vendored in module_utils) """
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ansible_collections.dellemc.objectscale.plugins.module_utils \
        import objectscale_client

try:
    from ansible_collections.dellemc.objectscale.plugins.module_utils \
        import objectscale_client
    HAS_OBJECTSCALE_CLIENT = True
except ImportError:
    objectscale_client = None  # type: ignore[assignment]
    HAS_OBJECTSCALE_CLIENT = False


def get_objectscale_management_host_parameters() -> Dict[str, Dict[str, Any]]:
    """
    Returns a dict of standard ObjectScale connection parameters for use as module argument_spec.
    """
    return dict(
        objectscale_host=dict(type='str', required=True),
        objectscale_port=dict(type='int', default=4443, required=False),
        objectscale_username=dict(type='str', required=True, no_log=False),
        objectscale_password=dict(type='str', required=True, no_log=True),
        validate_certs=dict(type='bool', default=True, required=False),
        timeout=dict(type='int', default=30, required=False),
    )


def get_objectscale_connection(module_params: Dict[str, Any]) -> Any:
    """
    Creates and returns an authenticated objectscale_client.ApiClient.
    The /login endpoint requires HTTP Basic Auth — bypasses the generated client
    for that single call, extracts X-SDS-AUTH-TOKEN, then configures the ApiClient
    to include it as an api_key on all subsequent requests.
    """

    try:
        import urllib3
    except ImportError:
        from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import urllib3_stub as urllib3
    import base64

    host = module_params['objectscale_host']
    port = module_params['objectscale_port']
    username = module_params['objectscale_username']
    password = module_params['objectscale_password']
    validate_certs = module_params.get('validate_certs', True)

    # Login via urllib3 Basic Auth — the generated client always injects AuthToken
    # for the /login path, but the first call needs HTTP Basic credentials instead.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED' if validate_certs else 'CERT_NONE',
        ca_certs=None,
    )
    credentials = base64.b64encode(
        f"{username}:{password}".encode('utf-8')
    ).decode('utf-8')
    login_resp = http.request(
        'GET',
        f"https://{host}:{port}/login",
        headers={'Authorization': f'Basic {credentials}'}
    )
    if login_resp.status not in (200, 201):
        raise Exception(
            f"ObjectScale login failed (HTTP {login_resp.status}): {login_resp.data[:200]}"
        )
    token = login_resp.headers.get('X-SDS-AUTH-TOKEN')
    if not token:
        raise Exception(
            "ObjectScale login succeeded but X-SDS-AUTH-TOKEN was absent from response headers"
        )

    # Build the ApiClient with the obtained token
    if objectscale_client is None:
        raise RuntimeError("objectscale_client is not available")
    config = objectscale_client.Configuration(host=f"https://{host}:{port}")
    config.verify_ssl = validate_certs
    config.api_key = {'AuthToken': token}

    client = objectscale_client.ApiClient(config)

    def cleanup_token() -> None:
        try:
            from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client.api.authentication_api import AuthenticationApi
            auth_api = AuthenticationApi(client)
            auth_api.authentication_resource_logout()
        except Exception:
            pass  # Best effort cleanup

    import atexit
    atexit.register(cleanup_token)

    return client


def determine_error(error_obj: Exception) -> str:
    """
    Determine and return a readable error message from an exception.
    """
    body = getattr(error_obj, 'body', None)
    if body:
        try:
            import json
            parsed = json.loads(body)
            return parsed.get('description', str(body))
        except Exception:
            return str(body)
    return str(error_obj)


def paginate_with_next_marker(api_call, base_kwargs, items_key):
    """
    Auto-paginate an API call that uses NextMarker-based pagination.

    This function handles the following pagination pattern:
    1. The list API accepts `marker` as a query parameter.
    2. The list API returns a response with following structure:
       {
           "items": [...],
           "NextMarker": "..."
       }

    Args:
        api_call: The API method to call (e.g., self.bucket_api.bucket_service_get_buckets)
        base_kwargs: Base kwargs to pass to each API call (e.g., {'namespace': 'ns1'})
        items_key: Key in response.to_dict() containing the items list
                   (e.g., 'object_bucket', 'namespace', 'blobuser')

    Returns:
        List of all items across all pages

    Example:
        def list_all_buckets(self):
            return paginate_with_next_marker(
                api_call=self.bucket_api.bucket_service_get_buckets,
                base_kwargs=dict(namespace=self.namespace),
                items_key='object_bucket'
            )
    """
    all_items = []
    marker = None

    while True:
        kwargs = dict(base_kwargs)
        if marker:
            kwargs['marker'] = marker

        response = api_call(**kwargs)
        result = response.to_dict()
        items = result.get(items_key) or []
        all_items.extend(items)

        # Check if there are more results using NextMarker
        next_marker = result.get('NextMarker')
        if next_marker:
            marker = next_marker
        else:
            break

    return all_items
