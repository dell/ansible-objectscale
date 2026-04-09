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
