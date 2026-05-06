# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from unittest.mock import MagicMock

IAM_API = 'ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api'

# ---------------------------------------------------------------------------
# Sample XML responses from ObjectScale
# ---------------------------------------------------------------------------

CREATE_RESPONSE_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:CreateSAMLProviderResponse xmlns:ns2="none">
  <ResponseMetadata><RequestId>abc-123</RequestId></ResponseMetadata>
  <CreateSAMLProviderResult>
    <SAMLProviderArn>urn:ecs:iam::ns1:saml-provider/test-idp</SAMLProviderArn>
  </CreateSAMLProviderResult>
</ns2:CreateSAMLProviderResponse>'''

GET_RESPONSE_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:GetSAMLProviderResponse xmlns:ns2="none">
  <ResponseMetadata><RequestId>abc-456</RequestId></ResponseMetadata>
  <GetSAMLProviderResult>
    <SAMLMetadataDocument>&lt;xml&gt;metadata&lt;/xml&gt;</SAMLMetadataDocument>
    <CreateDate>2025-01-15T12:00:00Z</CreateDate>
    <ValidUntil>2030-12-31T23:59:59Z</ValidUntil>
  </GetSAMLProviderResult>
</ns2:GetSAMLProviderResponse>'''

# ObjectScale sometimes returns lowercase variant
GET_RESPONSE_XML_LOWERCASE = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:GetSAMLProviderResponse xmlns:ns2="none">
  <ResponseMetadata><RequestId>abc-456</RequestId></ResponseMetadata>
  <getSAMLProviderResult>
    <SAMLMetadataDocument>&lt;xml&gt;metadata&lt;/xml&gt;</SAMLMetadataDocument>
    <CreateDate>2025-01-15T12:00:00Z</CreateDate>
    <ValidUntil>2030-12-31T23:59:59Z</ValidUntil>
  </getSAMLProviderResult>
</ns2:GetSAMLProviderResponse>'''

LIST_RESPONSE_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:ListSAMLProvidersResponse xmlns:ns2="none">
  <ResponseMetadata><RequestId>abc-789</RequestId></ResponseMetadata>
  <ListSAMLProvidersResult>
    <IsTruncated>false</IsTruncated>
    <SAMLProviderList>
      <member>
        <Arn>urn:ecs:iam::ns1:saml-provider/idp1</Arn>
        <CreateDate>2025-01-15T12:00:00Z</CreateDate>
        <ValidUntil>2030-12-31T23:59:59Z</ValidUntil>
      </member>
      <member>
        <Arn>urn:ecs:iam::ns1:saml-provider/idp2</Arn>
        <CreateDate>2025-02-01T08:00:00Z</CreateDate>
        <ValidUntil>2031-01-01T00:00:00Z</ValidUntil>
      </member>
    </SAMLProviderList>
  </ListSAMLProvidersResult>
</ns2:ListSAMLProvidersResponse>'''

LIST_EMPTY_RESPONSE_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:ListSAMLProvidersResponse xmlns:ns2="none">
  <ResponseMetadata><RequestId>abc-000</RequestId></ResponseMetadata>
  <ListSAMLProvidersResult>
    <IsTruncated>false</IsTruncated>
    <SAMLProviderList/>
  </ListSAMLProvidersResult>
</ns2:ListSAMLProvidersResponse>'''

UPDATE_RESPONSE_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:UpdateSAMLProviderResponse xmlns:ns2="none">
  <ResponseMetadata><RequestId>abc-upd</RequestId></ResponseMetadata>
  <UpdateSAMLProviderResult>
    <SAMLProviderArn>urn:ecs:iam::ns1:saml-provider/test-idp</SAMLProviderArn>
  </UpdateSAMLProviderResult>
</ns2:UpdateSAMLProviderResponse>'''

DELETE_RESPONSE_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:DeleteSAMLProviderResponse xmlns:ns2="none">
  <ResponseMetadata><RequestId>abc-del</RequestId></ResponseMetadata>
</ns2:DeleteSAMLProviderResponse>'''

ERROR_NO_SUCH_ENTITY_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ErrorResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <Error>
    <Type>Sender</Type>
    <Code>NoSuchEntity</Code>
    <Message>SAML provider not found</Message>
  </Error>
  <RequestId>err-404</RequestId>
</ErrorResponse>'''

ERROR_VALIDATION_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ErrorResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <Error>
    <Type>Sender</Type>
    <Code>ValidationError</Code>
    <Message>Invalid parameter</Message>
  </Error>
  <RequestId>err-400</RequestId>
</ErrorResponse>'''

# Also test bare-tag (no namespace) error XML
ERROR_NO_SUCH_ENTITY_BARE_XML = b'''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ErrorResponse>
  <Error>
    <Type>Sender</Type>
    <Code>NoSuchEntity</Code>
    <Message>Not found</Message>
  </Error>
</ErrorResponse>'''


def _make_iam_api():
    """Create an IamApi with a mocked api_client."""
    from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApi

    api_client = MagicMock()
    api_client.configuration.api_key = {'AuthToken': 'fake-token'}
    api_client.configuration.host = 'https://10.0.0.1:4443'
    api_client.configuration.verify_ssl = False

    iam = IamApi(api_client)
    return iam


# =========================================================================
# create_saml_provider
# =========================================================================

class TestCreateSamlProvider:

    def test_success(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(200, CREATE_RESPONSE_XML))
        result = iam.create_saml_provider('test-idp', '<xml>metadata</xml>', 'ns1')
        assert result['SAMLProviderArn'] == 'urn:ecs:iam::ns1:saml-provider/test-idp'
        iam._make_request.assert_called_once_with(
            'CreateSAMLProvider',
            {'Name': 'test-idp', 'SAMLMetadataDocument': '<xml>metadata</xml>'},
            'ns1',
        )

    def test_failure_400(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(400, ERROR_VALIDATION_XML))
        with pytest.raises(IamApiException) as exc_info:
            iam.create_saml_provider('test-idp', 'short', 'ns1')
        assert exc_info.value.status == 400

    def test_failure_no_result_element(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        # Response with no result element
        bad_xml = b'<?xml version="1.0"?><Response></Response>'
        iam._make_request = MagicMock(return_value=(200, bad_xml))
        with pytest.raises(IamApiException):
            iam.create_saml_provider('test-idp', 'meta', 'ns1')


# =========================================================================
# get_saml_provider
# =========================================================================

class TestGetSamlProvider:

    def test_success(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(200, GET_RESPONSE_XML))
        result = iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/test-idp', 'ns1')
        assert result is not None
        assert result['CreateDate'] == '2025-01-15T12:00:00Z'
        assert result['ValidUntil'] == '2030-12-31T23:59:59Z'
        assert '<xml>metadata</xml>' in result['SAMLMetadataDocument']

    def test_success_lowercase_result(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(200, GET_RESPONSE_XML_LOWERCASE))
        result = iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/test-idp', 'ns1')
        assert result is not None
        assert result['CreateDate'] == '2025-01-15T12:00:00Z'

    def test_not_found_404(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(404, b''))
        result = iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/gone', 'ns1')
        assert result is None

    def test_not_found_no_such_entity(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(400, ERROR_NO_SUCH_ENTITY_XML))
        result = iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/gone', 'ns1')
        assert result is None

    def test_not_found_no_such_entity_bare_xml(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(400, ERROR_NO_SUCH_ENTITY_BARE_XML))
        result = iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/gone', 'ns1')
        assert result is None

    def test_other_400_error(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(400, ERROR_VALIDATION_XML))
        with pytest.raises(IamApiException) as exc_info:
            iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/bad', 'ns1')
        assert exc_info.value.status == 400

    def test_malformed_error_xml(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(400, b'not-xml'))
        with pytest.raises(IamApiException):
            iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/bad', 'ns1')

    def test_no_result_element(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        bad_xml = b'<?xml version="1.0"?><Response></Response>'
        iam._make_request = MagicMock(return_value=(200, bad_xml))
        with pytest.raises(IamApiException):
            iam.get_saml_provider('urn:ecs:iam::ns1:saml-provider/test', 'ns1')


# =========================================================================
# list_saml_providers
# =========================================================================

class TestListSamlProviders:

    def test_success_with_providers(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(200, LIST_RESPONSE_XML))
        result = iam.list_saml_providers('ns1')
        assert len(result) == 2
        assert result[0]['Arn'] == 'urn:ecs:iam::ns1:saml-provider/idp1'
        assert result[1]['Arn'] == 'urn:ecs:iam::ns1:saml-provider/idp2'

    def test_success_empty(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(200, LIST_EMPTY_RESPONSE_XML))
        result = iam.list_saml_providers('ns1')
        assert result == []

    def test_failure(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(500, b'server error'))
        with pytest.raises(IamApiException):
            iam.list_saml_providers('ns1')

    def test_no_provider_list_element(self):
        iam = _make_iam_api()
        no_list_xml = b'<?xml version="1.0"?><Response><Result></Result></Response>'
        iam._make_request = MagicMock(return_value=(200, no_list_xml))
        result = iam.list_saml_providers('ns1')
        assert result == []


# =========================================================================
# update_saml_provider
# =========================================================================

class TestUpdateSamlProvider:

    def test_success(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(200, UPDATE_RESPONSE_XML))
        result = iam.update_saml_provider(
            'urn:ecs:iam::ns1:saml-provider/test-idp', '<new-xml/>', 'ns1'
        )
        assert result['SAMLProviderArn'] == 'urn:ecs:iam::ns1:saml-provider/test-idp'

    def test_not_found(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(404, ERROR_NO_SUCH_ENTITY_XML))
        with pytest.raises(IamApiException):
            iam.update_saml_provider('urn:ecs:iam::ns1:saml-provider/gone', '<xml/>', 'ns1')

    def test_no_result_element(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        bad_xml = b'<?xml version="1.0"?><Response></Response>'
        iam._make_request = MagicMock(return_value=(200, bad_xml))
        with pytest.raises(IamApiException):
            iam.update_saml_provider('urn:ecs:iam::ns1:saml-provider/test', '<xml/>', 'ns1')


# =========================================================================
# delete_saml_provider
# =========================================================================

class TestDeleteSamlProvider:

    def test_success(self):
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(200, DELETE_RESPONSE_XML))
        iam.delete_saml_provider('urn:ecs:iam::ns1:saml-provider/test-idp', 'ns1')
        iam._make_request.assert_called_once()

    def test_not_found(self):
        from ansible_collections.dellemc.objectscale.plugins.module_utils.iam_api import IamApiException
        iam = _make_iam_api()
        iam._make_request = MagicMock(return_value=(404, ERROR_NO_SUCH_ENTITY_XML))
        with pytest.raises(IamApiException):
            iam.delete_saml_provider('urn:ecs:iam::ns1:saml-provider/gone', 'ns1')


# =========================================================================
# _extract_saml_provider_list_entry
# =========================================================================

class TestExtractSamlProviderListEntry:

    def test_extract(self):
        import xml.etree.ElementTree as ET
        iam = _make_iam_api()
        xml_str = '<member><Arn>urn:ecs:iam::ns1:saml-provider/idp1</Arn><CreateDate>2025-01-01</CreateDate><ValidUntil>2030-01-01</ValidUntil></member>'
        el = ET.fromstring(xml_str)
        result = iam._extract_saml_provider_list_entry(el)
        assert result['Arn'] == 'urn:ecs:iam::ns1:saml-provider/idp1'
        assert result['CreateDate'] == '2025-01-01'
        assert result['ValidUntil'] == '2030-01-01'
