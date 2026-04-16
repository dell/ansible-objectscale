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

    NOTE: objectscale_password is explicitly marked with no_log=True to prevent
    credential leakage in logs, diffs, or error messages (Ansible security best practice).
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

    return objectscale_client.ApiClient(config)


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
