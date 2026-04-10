# Copyright: (c) 2025, Dell Technologies
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Hand-crafted HTTP client for the ObjectScale IAM API (AWS IAM-compatible)."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import xml.etree.ElementTree as ET
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    import urllib3
except ImportError:
    from ansible_collections.dellemc.objectscale.plugins.module_utils \
        .objectscale_client._stubs import urllib3_stub as urllib3  # type: ignore[no-redef]


# AWS IAM XML namespace used in all response documents.
IAM_XML_NS = 'https://iam.amazonaws.com/doc/2010-05-08/'
NS = {'iam': IAM_XML_NS}


def _ns(tag):
    # type: (str) -> str
    """Return a fully-qualified XML tag name within the IAM namespace."""
    return '{%s}%s' % (IAM_XML_NS, tag)


class IamApiException(Exception):
    """Exception raised when the IAM API returns an error response."""

    def __init__(self, status, body, action=None):
        # type: (int, bytes, Optional[str]) -> None
        self.status = status  # type: int
        self.body = body  # type: bytes
        self.action = action  # type: Optional[str]
        self.error_code = None  # type: Optional[str]
        self.error_message = None  # type: Optional[str]

        try:
            xml_body = body.decode('utf-8') if isinstance(body, bytes) else body
            root = ET.fromstring(xml_body)
            error_el = root.find(_ns('Error'))
            if error_el is None:
                error_el = root.find('Error')
            if error_el is not None:
                code_el = error_el.find(_ns('Code'))
                if code_el is None:
                    code_el = error_el.find('Code')
                msg_el = error_el.find(_ns('Message'))
                if msg_el is None:
                    msg_el = error_el.find('Message')
                if code_el is not None and code_el.text:
                    self.error_code = code_el.text
                if msg_el is not None and msg_el.text:
                    self.error_message = msg_el.text
        except Exception:
            pass

        if self.error_code and self.error_message:
            message = "IAM API error (HTTP %d, Action=%s): %s - %s" % (
                status, action, self.error_code, self.error_message,
            )
        else:
            message = "IAM API error (HTTP %d, Action=%s): %s" % (
                status, action, body[:500] if body else b'<empty>',
            )
        super(IamApiException, self).__init__(message)


class IamApi(object):
    """Low-level client for the ObjectScale IAM (AWS IAM-compatible) query API.

    All IAM actions are sent as ``POST /iam`` with query-string parameters.
    Responses are XML documents in the ``https://iam.amazonaws.com/doc/2010-05-08/``
    namespace.

    Parameters
    ----------
    api_client : objectscale_client.ApiClient
        An authenticated API client obtained via ``utils.get_objectscale_connection()``.
    """

    def __init__(self, api_client):
        # type: (Any) -> None
        self._token = api_client.configuration.api_key.get('AuthToken', '')  # type: str
        self._base_url = api_client.configuration.host.rstrip('/')  # type: str
        self._verify_ssl = api_client.configuration.verify_ssl  # type: bool

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if self._verify_ssl else 'CERT_NONE',
            ca_certs=None,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_request(self, action, params, namespace):
        # type: (str, Dict[str, str], str) -> Tuple[int, bytes]
        """Execute an IAM query-API request and return ``(status, body)``."""
        query_params = dict(params)
        query_params['Action'] = action

        headers = {
            'X-SDS-AUTH-TOKEN': self._token,
            'X-Emc-Namespace': namespace,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        url = self._base_url + '/iam'

        resp = self._http.request(
            'POST',
            url,
            fields=query_params,
            headers=headers,
            encode_multipart=False,
        )

        return resp.status, resp.data

    def _handle_error(self, status_code, response_body, action):
        # type: (int, bytes, str) -> None
        """Raise :class:`IamApiException` for the given error response."""
        raise IamApiException(status=status_code, body=response_body, action=action)

    @staticmethod
    def _parse_xml(xml_bytes):
        # type: (bytes) -> ET.Element
        """Parse *xml_bytes* and return the root Element."""
        return ET.fromstring(xml_bytes)

    @staticmethod
    def _extract_text(element, tag):
        # type: (ET.Element, str) -> Optional[str]
        """Return the text content of the first child matching *tag*."""
        child = element.find(_ns(tag))
        if child is None:
            child = element.find(tag)
        if child is not None and child.text is not None:
            return child.text
        return None

    @staticmethod
    def _find_descendant(element, tag):
        # type: (ET.Element, str) -> Optional[ET.Element]
        """Find a descendant element, trying IAM namespace first, then bare tag."""
        result = element.find('.//' + _ns(tag))
        if result is None:
            result = element.find('.//' + tag)
        return result

    @staticmethod
    def _findall_children(element, tag):
        # type: (ET.Element, str) -> List[ET.Element]
        """Find all child elements, trying IAM namespace first, then bare tag."""
        results = element.findall(_ns(tag))
        if not results:
            results = element.findall(tag)
        return results

    def _extract_group(self, group_element):
        # type: (ET.Element) -> Dict[str, Optional[str]]
        """Extract a group dict from a ``<Group>`` XML element."""
        return {
            'GroupName': self._extract_text(group_element, 'GroupName'),
            'GroupId': self._extract_text(group_element, 'GroupId'),
            'Arn': self._extract_text(group_element, 'Arn'),
            'Path': self._extract_text(group_element, 'Path'),
            'CreateDate': self._extract_text(group_element, 'CreateDate'),
        }

    def _extract_user(self, user_element):
        # type: (ET.Element) -> Dict[str, Optional[str]]
        """Extract a user dict from a ``<member>`` XML element."""
        return {
            'UserName': self._extract_text(user_element, 'UserName'),
            'UserId': self._extract_text(user_element, 'UserId'),
            'Arn': self._extract_text(user_element, 'Arn'),
        }

    def _extract_attached_policy(self, policy_element):
        # type: (ET.Element) -> Dict[str, Optional[str]]
        """Extract a policy dict from an ``<member>`` XML element."""
        return {
            'PolicyName': self._extract_text(policy_element, 'PolicyName'),
            'PolicyArn': self._extract_text(policy_element, 'PolicyArn'),
        }

    def _paginate(self, action, params, namespace, result_tag, extractor):
        # type: (str, Dict[str, str], str, str, Callable[[ET.Element], Any]) -> List[Any]
        """Auto-paginate an IAM list action."""
        results = []  # type: List[Any]
        page_params = dict(params)

        while True:
            status, body = self._make_request(action, page_params, namespace)

            if status < 200 or status >= 300:
                self._handle_error(status, body, action)

            root = self._parse_xml(body)

            result_el = self._find_descendant(root, result_tag)
            if result_el is not None:
                for member in self._findall_children(result_el, 'member'):
                    results.append(extractor(member))

            is_truncated_el = self._find_descendant(root, 'IsTruncated')
            is_truncated = (
                is_truncated_el is not None
                and is_truncated_el.text is not None
                and is_truncated_el.text.lower() == 'true'
            )

            if is_truncated:
                marker_el = self._find_descendant(root, 'Marker')
                if marker_el is not None and marker_el.text:
                    page_params['Marker'] = marker_el.text
                else:
                    break
            else:
                break

        return results

    # ------------------------------------------------------------------
    # Public API -- Group CRUD
    # ------------------------------------------------------------------

    def create_group(self, group_name, namespace, path='/'):
        # type: (str, str, str) -> Dict[str, Optional[str]]
        """Create an IAM group."""
        params = {'GroupName': group_name, 'Path': path}  # type: Dict[str, str]

        status, body = self._make_request('CreateGroup', params, namespace)

        if status < 200 or status >= 300:
            self._handle_error(status, body, 'CreateGroup')

        root = self._parse_xml(body)
        group_el = self._find_descendant(root, 'Group')
        if group_el is None:
            self._handle_error(status, body, 'CreateGroup')
            raise AssertionError("unreachable")

        return self._extract_group(group_el)

    def get_group(self, group_name, namespace):
        # type: (str, str) -> Optional[Dict[str, Any]]
        """Retrieve an IAM group's details and its members. Returns None on 404."""
        params = {'GroupName': group_name}  # type: Dict[str, str]

        status, body = self._make_request('GetGroup', params, namespace)

        if status == 404:
            return None

        if status >= 400:
            try:
                err = IamApiException(status=status, body=body, action='GetGroup')
                if err.error_code == 'NoSuchEntity':
                    return None
            except Exception:
                pass
            self._handle_error(status, body, 'GetGroup')

        root = self._parse_xml(body)

        group_el = self._find_descendant(root, 'Group')
        if group_el is None:
            return None

        group = self._extract_group(group_el)

        users = []  # type: List[Dict[str, Optional[str]]]
        users_el = self._find_descendant(root, 'Users')
        if users_el is not None:
            for member in self._findall_children(users_el, 'member'):
                users.append(self._extract_user(member))
        group['Users'] = users  # type: ignore[assignment]

        return group

    def delete_group(self, group_name, namespace):
        # type: (str, str) -> None
        """Delete an IAM group. Idempotent -- returns None on 404."""
        params = {'GroupName': group_name}  # type: Dict[str, str]

        status, body = self._make_request('DeleteGroup', params, namespace)

        if status == 404:
            return None

        if status >= 400:
            try:
                err = IamApiException(status=status, body=body, action='DeleteGroup')
                if err.error_code == 'NoSuchEntity':
                    return None
            except Exception:
                pass
            self._handle_error(status, body, 'DeleteGroup')

        return None

    def list_groups(self, namespace, path_prefix=None):
        # type: (str, Optional[str]) -> List[Dict[str, Optional[str]]]
        """List all IAM groups in a namespace, with automatic pagination."""
        params = {}  # type: Dict[str, str]
        if path_prefix is not None:
            params['PathPrefix'] = path_prefix

        return self._paginate(
            action='ListGroups', params=params, namespace=namespace,
            result_tag='Groups', extractor=self._extract_group,
        )

    # ------------------------------------------------------------------
    # Public API -- Group membership
    # ------------------------------------------------------------------

    def add_user_to_group(self, group_name, user_name, namespace):
        # type: (str, str, str) -> None
        """Add a user to a group."""
        params = {'GroupName': group_name, 'UserName': user_name}

        status, body = self._make_request('AddUserToGroup', params, namespace)

        if status < 200 or status >= 300:
            self._handle_error(status, body, 'AddUserToGroup')

    def remove_user_from_group(self, group_name, user_name, namespace):
        # type: (str, str, str) -> None
        """Remove a user from a group. Idempotent -- returns None on 404."""
        params = {'GroupName': group_name, 'UserName': user_name}

        status, body = self._make_request('RemoveUserFromGroup', params, namespace)

        if status == 404:
            return None

        if status >= 400:
            try:
                err = IamApiException(status=status, body=body, action='RemoveUserFromGroup')
                if err.error_code == 'NoSuchEntity':
                    return None
            except Exception:
                pass
            self._handle_error(status, body, 'RemoveUserFromGroup')

    # ------------------------------------------------------------------
    # Public API -- Managed (attached) policies
    # ------------------------------------------------------------------

    def attach_group_policy(self, group_name, policy_arn, namespace):
        # type: (str, str, str) -> None
        """Attach a managed policy to a group."""
        params = {'GroupName': group_name, 'PolicyArn': policy_arn}

        status, body = self._make_request('AttachGroupPolicy', params, namespace)

        if status < 200 or status >= 300:
            self._handle_error(status, body, 'AttachGroupPolicy')

    def detach_group_policy(self, group_name, policy_arn, namespace):
        # type: (str, str, str) -> None
        """Detach a managed policy from a group. Idempotent -- returns None on 404."""
        params = {'GroupName': group_name, 'PolicyArn': policy_arn}

        status, body = self._make_request('DetachGroupPolicy', params, namespace)

        if status == 404:
            return None

        if status >= 400:
            try:
                err = IamApiException(status=status, body=body, action='DetachGroupPolicy')
                if err.error_code == 'NoSuchEntity':
                    return None
            except Exception:
                pass
            self._handle_error(status, body, 'DetachGroupPolicy')

    def list_attached_group_policies(self, group_name, namespace):
        # type: (str, str) -> List[Dict[str, Optional[str]]]
        """List managed policies attached to a group, with automatic pagination."""
        params = {'GroupName': group_name}

        return self._paginate(
            action='ListAttachedGroupPolicies', params=params, namespace=namespace,
            result_tag='AttachedPolicies', extractor=self._extract_attached_policy,
        )

    # ------------------------------------------------------------------
    # Public API -- Inline policies
    # ------------------------------------------------------------------

    def put_group_policy(self, group_name, policy_name, policy_document, namespace):
        # type: (str, str, str, str) -> None
        """Create or update an inline policy on a group."""
        params = {
            'GroupName': group_name,
            'PolicyName': policy_name,
            'PolicyDocument': policy_document,
        }

        status, body = self._make_request('PutGroupPolicy', params, namespace)

        if status < 200 or status >= 300:
            self._handle_error(status, body, 'PutGroupPolicy')

    def get_group_policy(self, group_name, policy_name, namespace):
        # type: (str, str, str) -> Optional[Dict[str, Optional[str]]]
        """Retrieve an inline policy on a group. Returns None on 404."""
        params = {'GroupName': group_name, 'PolicyName': policy_name}

        status, body = self._make_request('GetGroupPolicy', params, namespace)

        if status == 404:
            return None

        if status >= 400:
            try:
                err = IamApiException(status=status, body=body, action='GetGroupPolicy')
                if err.error_code == 'NoSuchEntity':
                    return None
            except Exception:
                pass
            self._handle_error(status, body, 'GetGroupPolicy')

        root = self._parse_xml(body)

        result_el = self._find_descendant(root, 'GetGroupPolicyResult')
        if result_el is None:
            return None

        return {
            'GroupName': self._extract_text(result_el, 'GroupName'),
            'PolicyName': self._extract_text(result_el, 'PolicyName'),
            'PolicyDocument': self._extract_text(result_el, 'PolicyDocument'),
        }

    def delete_group_policy(self, group_name, policy_name, namespace):
        # type: (str, str, str) -> None
        """Delete an inline policy from a group. Idempotent -- returns None on 404."""
        params = {'GroupName': group_name, 'PolicyName': policy_name}

        status, body = self._make_request('DeleteGroupPolicy', params, namespace)

        if status == 404:
            return None

        if status >= 400:
            try:
                err = IamApiException(status=status, body=body, action='DeleteGroupPolicy')
                if err.error_code == 'NoSuchEntity':
                    return None
            except Exception:
                pass
            self._handle_error(status, body, 'DeleteGroupPolicy')

    def list_group_policies(self, group_name, namespace):
        # type: (str, str) -> List[str]
        """List names of inline policies on a group, with automatic pagination."""
        params = {'GroupName': group_name}

        def _extract_policy_name(member_el):
            # type: (ET.Element) -> str
            return member_el.text or ''

        return self._paginate(
            action='ListGroupPolicies', params=params, namespace=namespace,
            result_tag='PolicyNames', extractor=_extract_policy_name,
        )

    # ------------------------------------------------------------------
    # Public API -- User-group queries
    # ------------------------------------------------------------------

    def list_groups_for_user(self, user_name, namespace):
        # type: (str, str) -> List[Dict[str, Optional[str]]]
        """List groups that a user belongs to, with automatic pagination."""
        params = {'UserName': user_name}

        return self._paginate(
            action='ListGroupsForUser', params=params, namespace=namespace,
            result_tag='Groups', extractor=self._extract_group,
        )
