# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

MODULE = 'ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api'

# ---------------------------------------------------------------------------
# Sample XML responses
# ---------------------------------------------------------------------------

SAMPLE_CREATE_GROUP = b'''<?xml version="1.0" encoding="UTF-8"?>
<CreateGroupResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <CreateGroupResult>
    <Group>
      <GroupName>developers</GroupName>
      <GroupId>AGPA1234567890</GroupId>
      <Arn>urn:ecs:iam::ns1:group/developers</Arn>
      <Path>/</Path>
      <CreateDate>2024-01-15T10:30:00Z</CreateDate>
    </Group>
  </CreateGroupResult>
</CreateGroupResponse>'''

SAMPLE_GET_GROUP = b'''<?xml version="1.0" encoding="UTF-8"?>
<GetGroupResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <GetGroupResult>
    <Group>
      <GroupName>developers</GroupName>
      <GroupId>AGPA1234567890</GroupId>
      <Arn>urn:ecs:iam::ns1:group/developers</Arn>
      <Path>/</Path>
      <CreateDate>2024-01-15T10:30:00Z</CreateDate>
    </Group>
    <Users>
      <member>
        <UserName>alice</UserName>
        <UserId>AIDA111</UserId>
        <Arn>urn:ecs:iam::ns1:user/alice</Arn>
      </member>
    </Users>
  </GetGroupResult>
</GetGroupResponse>'''

SAMPLE_LIST_GROUPS = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListGroupsResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListGroupsResult>
    <Groups>
      <member>
        <GroupName>developers</GroupName>
        <GroupId>AGPA1234567890</GroupId>
        <Arn>urn:ecs:iam::ns1:group/developers</Arn>
        <Path>/</Path>
      </member>
    </Groups>
    <IsTruncated>false</IsTruncated>
  </ListGroupsResult>
</ListGroupsResponse>'''

SAMPLE_LIST_ATTACHED = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListAttachedGroupPoliciesResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListAttachedGroupPoliciesResult>
    <AttachedPolicies>
      <member>
        <PolicyName>ReadOnly</PolicyName>
        <PolicyArn>urn:ecs:iam:::policy/ReadOnly</PolicyArn>
      </member>
    </AttachedPolicies>
    <IsTruncated>false</IsTruncated>
  </ListAttachedGroupPoliciesResult>
</ListAttachedGroupPoliciesResponse>'''

SAMPLE_LIST_INLINE = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListGroupPoliciesResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListGroupPoliciesResult>
    <PolicyNames>
      <member>InlinePolicy1</member>
    </PolicyNames>
    <IsTruncated>false</IsTruncated>
  </ListGroupPoliciesResult>
</ListGroupPoliciesResponse>'''

SAMPLE_SUCCESS = b'''<?xml version="1.0" encoding="UTF-8"?>
<Response xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ResponseMetadata><RequestId>req-1</RequestId></ResponseMetadata>
</Response>'''

SAMPLE_ERROR_404 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ErrorResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <Error>
    <Code>NoSuchEntity</Code>
    <Message>The group cannot be found.</Message>
  </Error>
</ErrorResponse>'''

SAMPLE_ERROR_500 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ErrorResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <Error>
    <Code>ServiceFailure</Code>
    <Message>Internal error.</Message>
  </Error>
</ErrorResponse>'''

SAMPLE_ERROR_401 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ErrorResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <Error>
    <Code>InvalidClientTokenId</Code>
    <Message>The security token included in the request is invalid.</Message>
  </Error>
</ErrorResponse>'''

SAMPLE_ERROR_403 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ErrorResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <Error>
    <Code>AccessDenied</Code>
    <Message>User is not authorized to perform this operation.</Message>
  </Error>
</ErrorResponse>'''

SAMPLE_GET_GROUP_POLICY = b'''<?xml version="1.0" encoding="UTF-8"?>
<GetGroupPolicyResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <GetGroupPolicyResult>
    <GroupName>developers</GroupName>
    <PolicyName>InlinePolicy1</PolicyName>
    <PolicyDocument>{"Version":"2012-10-17","Statement":[]}</PolicyDocument>
  </GetGroupPolicyResult>
</GetGroupPolicyResponse>'''

SAMPLE_LIST_GROUPS_PAGE1 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListGroupsResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListGroupsResult>
    <Groups>
      <member>
        <GroupName>group-a</GroupName>
        <GroupId>AGPA0001</GroupId>
        <Arn>urn:ecs:iam::ns1:group/group-a</Arn>
        <Path>/</Path>
      </member>
    </Groups>
    <IsTruncated>true</IsTruncated>
    <Marker>marker-page2</Marker>
  </ListGroupsResult>
</ListGroupsResponse>'''

SAMPLE_LIST_GROUPS_PAGE2 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListGroupsResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListGroupsResult>
    <Groups>
      <member>
        <GroupName>group-b</GroupName>
        <GroupId>AGPA0002</GroupId>
        <Arn>urn:ecs:iam::ns1:group/group-b</Arn>
        <Path>/</Path>
      </member>
    </Groups>
    <IsTruncated>false</IsTruncated>
  </ListGroupsResult>
</ListGroupsResponse>'''

SAMPLE_LIST_GROUPS_FOR_USER = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListGroupsForUserResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListGroupsForUserResult>
    <Groups>
      <member>
        <GroupName>developers</GroupName>
        <GroupId>AGPA1234567890</GroupId>
        <Arn>urn:ecs:iam::ns1:group/developers</Arn>
        <Path>/</Path>
      </member>
      <member>
        <GroupName>admins</GroupName>
        <GroupId>AGPA0987654321</GroupId>
        <Arn>urn:ecs:iam::ns1:group/admins</Arn>
        <Path>/</Path>
      </member>
    </Groups>
    <IsTruncated>false</IsTruncated>
  </ListGroupsForUserResult>
</ListGroupsForUserResponse>'''

SAMPLE_LIST_ATTACHED_PAGE1 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListAttachedGroupPoliciesResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListAttachedGroupPoliciesResult>
    <AttachedPolicies>
      <member>
        <PolicyName>ReadOnly</PolicyName>
        <PolicyArn>urn:ecs:iam:::policy/ReadOnly</PolicyArn>
      </member>
    </AttachedPolicies>
    <IsTruncated>true</IsTruncated>
    <Marker>marker-pol-page2</Marker>
  </ListAttachedGroupPoliciesResult>
</ListAttachedGroupPoliciesResponse>'''

SAMPLE_LIST_ATTACHED_PAGE2 = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListAttachedGroupPoliciesResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListAttachedGroupPoliciesResult>
    <AttachedPolicies>
      <member>
        <PolicyName>WriteAccess</PolicyName>
        <PolicyArn>urn:ecs:iam:::policy/WriteAccess</PolicyArn>
      </member>
    </AttachedPolicies>
    <IsTruncated>false</IsTruncated>
  </ListAttachedGroupPoliciesResult>
</ListAttachedGroupPoliciesResponse>'''


def _make_api():
    """Create an IamApi with mocked HTTP pool and _make_request."""
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi

    api_client = MagicMock()
    api_client.configuration.api_key = {'AuthToken': 'test-token'}
    api_client.configuration.host = 'https://10.0.0.1:4443'
    api_client.configuration.verify_ssl = False

    with patch(f'{MODULE}.urllib3'):
        api = IamApi(api_client)
    # Replace the HTTP pool with a mock so we can control responses
    api._http = MagicMock()
    return api


def _set_response(api, status, data):
    """Configure the mock HTTP pool to return a specific response."""
    resp = MagicMock()
    resp.status = status
    resp.data = data
    api._http.request.return_value = resp


class TestIamApiInit:

    def test_init_success(self):
        api = _make_api()
        assert api._token == 'test-token'
        assert api._base_url == 'https://10.0.0.1:4443'

    def test_init_extracts_token(self):
        api = _make_api()
        assert api._token == 'test-token'


class TestIamApiCreateGroup:

    def test_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_CREATE_GROUP)
        result = api.create_group('developers', 'ns1')
        assert result['GroupName'] == 'developers'
        assert result['GroupId'] == 'AGPA1234567890'

    def test_with_path(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_CREATE_GROUP)
        result = api.create_group('developers', 'ns1', path='/engineering/')
        assert result is not None

    def test_api_error(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 500, SAMPLE_ERROR_500)
        with pytest.raises(IamApiException):
            api.create_group('developers', 'ns1')


class TestIamApiGetGroup:

    def test_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_GET_GROUP)
        result = api.get_group('developers', 'ns1')
        assert result is not None
        assert result['GroupName'] == 'developers'
        assert len(result['Users']) == 1
        assert result['Users'][0]['UserName'] == 'alice'

    def test_not_found_returns_none(self):
        api = _make_api()
        _set_response(api, 404, SAMPLE_ERROR_404)
        result = api.get_group('nonexistent', 'ns1')
        assert result is None

    def test_api_error(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 500, SAMPLE_ERROR_500)
        with pytest.raises(IamApiException):
            api.get_group('developers', 'ns1')


class TestIamApiDeleteGroup:

    def test_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_SUCCESS)
        api.delete_group('developers', 'ns1')
        assert api._http.request.called

    def test_not_found_idempotent(self):
        api = _make_api()
        _set_response(api, 404, SAMPLE_ERROR_404)
        api.delete_group('nonexistent', 'ns1')  # Should not raise


class TestIamApiListGroups:

    def test_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_GROUPS)
        result = api.list_groups('ns1')
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['GroupName'] == 'developers'


class TestIamApiUserMethods:

    def test_add_user_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_SUCCESS)
        api.add_user_to_group('developers', 'alice', 'ns1')
        assert api._http.request.called

    def test_remove_user_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_SUCCESS)
        api.remove_user_from_group('developers', 'alice', 'ns1')
        assert api._http.request.called

    def test_remove_user_not_found_idempotent(self):
        api = _make_api()
        _set_response(api, 404, SAMPLE_ERROR_404)
        api.remove_user_from_group('developers', 'unknown', 'ns1')  # Should not raise

    def test_add_user_error(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 500, SAMPLE_ERROR_500)
        with pytest.raises(IamApiException):
            api.add_user_to_group('developers', 'alice', 'ns1')


class TestIamApiPolicyMethods:

    def test_attach_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_SUCCESS)
        api.attach_group_policy('developers', 'urn:policy/ReadOnly', 'ns1')
        assert api._http.request.called

    def test_detach_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_SUCCESS)
        api.detach_group_policy('developers', 'urn:policy/ReadOnly', 'ns1')
        assert api._http.request.called

    def test_list_attached_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_ATTACHED)
        result = api.list_attached_group_policies('developers', 'ns1')
        assert len(result) == 1
        assert result[0]['PolicyName'] == 'ReadOnly'

    def test_detach_not_found_idempotent(self):
        api = _make_api()
        _set_response(api, 404, SAMPLE_ERROR_404)
        api.detach_group_policy('developers', 'urn:policy/Missing', 'ns1')  # Should not raise


class TestIamApiInlinePolicyMethods:

    def test_put_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_SUCCESS)
        api.put_group_policy('developers', 'InlinePolicy1', '{"Version":"2012-10-17"}', 'ns1')
        assert api._http.request.called

    def test_delete_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_SUCCESS)
        api.delete_group_policy('developers', 'InlinePolicy1', 'ns1')
        assert api._http.request.called

    def test_list_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_INLINE)
        result = api.list_group_policies('developers', 'ns1')
        assert isinstance(result, list)
        assert 'InlinePolicy1' in result


class TestIamApiXmlParsing:

    def test_parse_create_group_response(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_CREATE_GROUP)
        result = api.create_group('developers', 'ns1')
        assert result['GroupId'] == 'AGPA1234567890'
        assert result['Arn'] == 'urn:ecs:iam::ns1:group/developers'

    def test_parse_get_group_with_users(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_GET_GROUP)
        result = api.get_group('developers', 'ns1')
        assert result['Users'][0]['UserName'] == 'alice'
        assert result['Users'][0]['UserId'] == 'AIDA111'

    def test_parse_error_response(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 500, SAMPLE_ERROR_500)
        with pytest.raises(IamApiException) as exc_info:
            api.create_group('developers', 'ns1')
        assert exc_info.value.error_code == 'ServiceFailure'


class TestIamApiMakeRequest:

    def test_includes_auth_headers(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_GROUPS)
        api.list_groups('ns1')
        call_kwargs = api._http.request.call_args
        headers = call_kwargs[1].get('headers', {}) if call_kwargs[1] else {}
        assert headers.get('X-SDS-AUTH-TOKEN') == 'test-token'
        assert headers.get('X-Emc-Namespace') == 'ns1'

    def test_post_method(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_GROUPS)
        api.list_groups('ns1')
        call_args = api._http.request.call_args[0]
        assert call_args[0] == 'POST'

    def test_url_includes_iam_path(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_GROUPS)
        api.list_groups('ns1')
        call_args = api._http.request.call_args[0]
        assert '/iam' in call_args[1]


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class TestIamApiPagination:

    def test_list_groups_multi_page(self):
        api = _make_api()
        resp1 = MagicMock(status=200, data=SAMPLE_LIST_GROUPS_PAGE1)
        resp2 = MagicMock(status=200, data=SAMPLE_LIST_GROUPS_PAGE2)
        api._http.request.side_effect = [resp1, resp2]

        result = api.list_groups('ns1')

        assert len(result) == 2
        names = [g['GroupName'] for g in result]
        assert 'group-a' in names
        assert 'group-b' in names
        assert api._http.request.call_count == 2

    def test_list_groups_single_page(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_GROUPS)
        result = api.list_groups('ns1')
        assert len(result) == 1
        assert api._http.request.call_count == 1

    def test_list_groups_with_path_prefix(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_GROUPS)
        api.list_groups('ns1', path_prefix='/engineering/')
        call_kwargs = api._http.request.call_args
        fields = call_kwargs[1].get('fields', {}) if call_kwargs[1] else {}
        assert fields.get('PathPrefix') == '/engineering/'

    def test_list_groups_api_error(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 500, SAMPLE_ERROR_500)
        with pytest.raises(IamApiException):
            api.list_groups('ns1')

    def test_list_attached_policies_multi_page(self):
        api = _make_api()
        resp1 = MagicMock(status=200, data=SAMPLE_LIST_ATTACHED_PAGE1)
        resp2 = MagicMock(status=200, data=SAMPLE_LIST_ATTACHED_PAGE2)
        api._http.request.side_effect = [resp1, resp2]

        result = api.list_attached_group_policies('developers', 'ns1')

        assert len(result) == 2
        names = [p['PolicyName'] for p in result]
        assert 'ReadOnly' in names
        assert 'WriteAccess' in names

    def test_pagination_marker_passed(self):
        api = _make_api()
        resp1 = MagicMock(status=200, data=SAMPLE_LIST_GROUPS_PAGE1)
        resp2 = MagicMock(status=200, data=SAMPLE_LIST_GROUPS_PAGE2)
        api._http.request.side_effect = [resp1, resp2]

        api.list_groups('ns1')

        second_call_fields = api._http.request.call_args_list[1][1].get('fields', {})
        assert second_call_fields.get('Marker') == 'marker-page2'


# ---------------------------------------------------------------------------
# list_groups_for_user
# ---------------------------------------------------------------------------

class TestIamApiListGroupsForUser:

    def test_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_LIST_GROUPS_FOR_USER)
        result = api.list_groups_for_user('alice', 'ns1')
        assert len(result) == 2
        names = [g['GroupName'] for g in result]
        assert 'developers' in names
        assert 'admins' in names

    def test_api_error(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 500, SAMPLE_ERROR_500)
        with pytest.raises(IamApiException):
            api.list_groups_for_user('alice', 'ns1')


# ---------------------------------------------------------------------------
# get_group_policy
# ---------------------------------------------------------------------------

class TestIamApiGetGroupPolicy:

    def test_success(self):
        api = _make_api()
        _set_response(api, 200, SAMPLE_GET_GROUP_POLICY)
        result = api.get_group_policy('developers', 'InlinePolicy1', 'ns1')
        assert result is not None
        assert result['GroupName'] == 'developers'
        assert result['PolicyName'] == 'InlinePolicy1'
        assert '2012-10-17' in result['PolicyDocument']

    def test_not_found_returns_none(self):
        api = _make_api()
        _set_response(api, 404, SAMPLE_ERROR_404)
        result = api.get_group_policy('developers', 'missing', 'ns1')
        assert result is None

    def test_no_such_entity_returns_none(self):
        api = _make_api()
        _set_response(api, 400, SAMPLE_ERROR_404)
        result = api.get_group_policy('developers', 'missing', 'ns1')
        assert result is None

    def test_api_error(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 500, SAMPLE_ERROR_500)
        with pytest.raises(IamApiException):
            api.get_group_policy('developers', 'InlinePolicy1', 'ns1')


# ---------------------------------------------------------------------------
# 401/403 error handling
# ---------------------------------------------------------------------------

class TestIamApiAuthErrors:

    def test_401_on_create_group(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 401, SAMPLE_ERROR_401)
        with pytest.raises(IamApiException) as exc_info:
            api.create_group('developers', 'ns1')
        assert exc_info.value.status == 401
        assert exc_info.value.error_code == 'InvalidClientTokenId'

    def test_403_on_create_group(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 403, SAMPLE_ERROR_403)
        with pytest.raises(IamApiException) as exc_info:
            api.create_group('developers', 'ns1')
        assert exc_info.value.status == 403
        assert exc_info.value.error_code == 'AccessDenied'

    def test_401_on_get_group(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 401, SAMPLE_ERROR_401)
        with pytest.raises(IamApiException):
            api.get_group('developers', 'ns1')

    def test_403_on_delete_group(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 403, SAMPLE_ERROR_403)
        with pytest.raises(IamApiException):
            api.delete_group('developers', 'ns1')

    def test_401_on_add_user(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 401, SAMPLE_ERROR_401)
        with pytest.raises(IamApiException):
            api.add_user_to_group('developers', 'alice', 'ns1')

    def test_403_on_attach_policy(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 403, SAMPLE_ERROR_403)
        with pytest.raises(IamApiException):
            api.attach_group_policy('developers', 'urn:pol', 'ns1')

    def test_403_on_put_group_policy(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 403, SAMPLE_ERROR_403)
        with pytest.raises(IamApiException):
            api.put_group_policy('developers', 'pol', '{}', 'ns1')

    def test_401_on_list_groups(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 401, SAMPLE_ERROR_401)
        with pytest.raises(IamApiException):
            api.list_groups('ns1')


# ---------------------------------------------------------------------------
# Malformed XML and edge cases
# ---------------------------------------------------------------------------

class TestIamApiMalformedResponses:

    def test_empty_response_body(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        api = _make_api()
        _set_response(api, 200, b'')
        with pytest.raises(Exception):
            api.create_group('developers', 'ns1')

    def test_malformed_xml_response(self):
        api = _make_api()
        _set_response(api, 200, b'<not-valid-xml')
        with pytest.raises(Exception):
            api.create_group('developers', 'ns1')

    def test_valid_xml_missing_group_element(self):
        api = _make_api()
        body = b'''<?xml version="1.0" encoding="UTF-8"?>
<CreateGroupResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <CreateGroupResult></CreateGroupResult>
</CreateGroupResponse>'''
        _set_response(api, 200, body)
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        with pytest.raises(IamApiException):
            api.create_group('developers', 'ns1')

    def test_error_exception_with_malformed_body(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        exc = IamApiException(status=500, body=b'not xml at all', action='Test')
        assert exc.status == 500
        assert exc.error_code is None
        assert exc.error_message is None

    def test_error_exception_with_empty_body(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        exc = IamApiException(status=500, body=b'', action='Test')
        assert exc.status == 500

    def test_get_group_empty_users_element(self):
        api = _make_api()
        body = b'''<?xml version="1.0" encoding="UTF-8"?>
<GetGroupResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <GetGroupResult>
    <Group>
      <GroupName>empty-group</GroupName>
      <GroupId>AGPA999</GroupId>
      <Arn>urn:ecs:iam::ns1:group/empty-group</Arn>
      <Path>/</Path>
      <CreateDate>2024-01-15T10:30:00Z</CreateDate>
    </Group>
    <Users></Users>
  </GetGroupResult>
</GetGroupResponse>'''
        _set_response(api, 200, body)
        result = api.get_group('empty-group', 'ns1')
        assert result is not None
        assert result['Users'] == []

    def test_delete_group_policy_not_found_idempotent(self):
        api = _make_api()
        _set_response(api, 404, SAMPLE_ERROR_404)
        api.delete_group_policy('developers', 'missing', 'ns1')  # Should not raise

    def test_list_group_policies_empty(self):
        api = _make_api()
        body = b'''<?xml version="1.0" encoding="UTF-8"?>
<ListGroupPoliciesResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <ListGroupPoliciesResult>
    <PolicyNames></PolicyNames>
    <IsTruncated>false</IsTruncated>
  </ListGroupPoliciesResult>
</ListGroupPoliciesResponse>'''
        _set_response(api, 200, body)
        result = api.list_group_policies('developers', 'ns1')
        assert result == []
