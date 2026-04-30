.. Created with antsibull-docs 2.24.0

dellemc.objectscale.iam_identity_provider module -- Manage IAM SAML Identity Providers on Dell ObjectScale
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.

To use it in a playbook, specify: ``dellemc.objectscale.iam_identity_provider``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Manages IAM SAML identity providers on the Dell ObjectScale storage system. This includes creating, updating, and deleting SAML identity providers.
- All operations are scoped to a specific ObjectScale namespace.
- Supports check mode and diff mode.


Parameters
----------

.. raw:: html

  <table style="width: 100%;">
  <thead>
    <tr>
    <th><p>Parameter</p></th>
    <th><p>Comments</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-provider_name"></div>
      <p style="display: inline;"><strong>provider_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-provider_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The name of the SAML identity provider.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-namespace"></div>
      <p style="display: inline;"><strong>namespace</strong></p>
      <a class="ansibleOptionLink" href="#parameter-namespace" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The ObjectScale namespace in which the identity provider resides.</p>
      <p>Maps to the <code class='docutils literal notranslate'>X-Emc-Namespace</code> header in IAM API requests.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-objectscale_host"></div>
      <p style="display: inline;"><strong>objectscale_host</strong></p>
      <a class="ansibleOptionLink" href="#parameter-objectscale_host" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>IP address or FQDN of the ObjectScale management endpoint.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-objectscale_password"></div>
      <p style="display: inline;"><strong>objectscale_password</strong></p>
      <a class="ansibleOptionLink" href="#parameter-objectscale_password" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>Password for authenticating with the ObjectScale management endpoint.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-objectscale_port"></div>
      <p style="display: inline;"><strong>objectscale_port</strong></p>
      <a class="ansibleOptionLink" href="#parameter-objectscale_port" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Port number for the ObjectScale management endpoint.</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">4443</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-objectscale_username"></div>
      <p style="display: inline;"><strong>objectscale_username</strong></p>
      <a class="ansibleOptionLink" href="#parameter-objectscale_username" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>Username for authenticating with the ObjectScale management endpoint.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-saml_metadata_document"></div>
      <p style="display: inline;"><strong>saml_metadata_document</strong></p>
      <a class="ansibleOptionLink" href="#parameter-saml_metadata_document" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The SAML metadata XML document from the identity provider.</p>
      <p>Required when creating a new identity provider (<code class='docutils literal notranslate'>state=present</code> and provider does not exist).</p>
      <p>When provided for an existing provider, the metadata will be compared and updated if different.</p>
      <p>Must be between 1000 and 10000000 characters in length.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-state"></div>
      <p style="display: inline;"><strong>state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The desired state of the identity provider.</p>
      <p><code class='docutils literal notranslate'>present</code> ensures the provider exists; <code class='docutils literal notranslate'>absent</code> ensures it does not.</p>
      <p style="margin-top: 8px;"><b>Choices:</b></p>
      <ul>
        <li><p><code style="color: blue;"><b>&#34;present&#34;</b></code> <span style="color: blue;">← (default)</span></p></li>
        <li><p><code>&#34;absent&#34;</code></p></li>
      </ul>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-validate_certs"></div>
      <p style="display: inline;"><strong>validate_certs</strong></p>
      <a class="ansibleOptionLink" href="#parameter-validate_certs" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Boolean value to enable or disable SSL certificate verification.</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">true</code></p>
    </td>
  </tr>
  </tbody>
  </table>


Attributes
----------

.. raw:: html

  <table style="width: 100%;">
  <thead>
    <tr>
    <th><p>Attribute</p></th>
    <th><p>Support</p></th>
    <th><p>Description</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td valign="top">
      <p><strong>check_mode</strong></p>
    </td>
    <td valign="top">
      <p><span style="color: green;">full</span></p>
    </td>
    <td valign="top">
      <p>Supports check mode. No changes will be made when check mode is enabled.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <p><strong>diff_mode</strong></p>
    </td>
    <td valign="top">
      <p><span style="color: green;">full</span></p>
    </td>
    <td valign="top">
      <p>Supports diff mode. Shows before and after state of the identity provider.</p>
    </td>
  </tr>
  </tbody>
  </table>


Notes
-----

- The SAML metadata document must contain a valid X.509 certificate.
- Provider ARN format is ``urn:ecs:iam::<namespace>:saml-provider/<provider_name>``.
- This module interacts with the ObjectScale IAM API (AWS IAM-compatible).


Examples
--------

.. code-block:: yaml

    - name: Create a SAML identity provider
      dellemc.objectscale.iam_identity_provider:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        provider_name: "my-saml-idp"
        namespace: "my-namespace"
        saml_metadata_document: "{{ lookup('file', 'saml-metadata.xml') }}"
        state: "present"

    - name: Update a SAML identity provider metadata
      dellemc.objectscale.iam_identity_provider:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        provider_name: "my-saml-idp"
        namespace: "my-namespace"
        saml_metadata_document: "{{ lookup('file', 'updated-saml-metadata.xml') }}"
        state: "present"

    - name: Delete a SAML identity provider
      dellemc.objectscale.iam_identity_provider:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        provider_name: "my-saml-idp"
        namespace: "my-namespace"
        state: "absent"


Return Values
-------------

.. raw:: html

  <table style="width: 100%;">
  <thead>
    <tr>
    <th><p>Key</p></th>
    <th><p>Description</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-changed"></div>
      <p style="display: inline;"><strong>changed</strong></p>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether or not the resource has changed.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Sample:</b> <code style="color: blue;">false</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_identity_provider_details"></div>
      <p style="display: inline;"><strong>iam_identity_provider_details</strong></p>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Identity provider details.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> When state is <code class='docutils literal notranslate'>present</code> and the provider exists</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Sample:</b></p>
      <div style="margin-top: 8px;"><div class="highlight"><pre>
{
    "provider_name": "my-saml-idp",
    "arn": "urn:ecs:iam::my-namespace:saml-provider/my-saml-idp",
    "create_date": "2025-01-15T12:00:00Z",
    "valid_until": "2030-12-31T23:59:59Z"
}
</pre></div></div>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-diff"></div>
      <p style="display: inline;"><strong>diff</strong></p>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Diff of the identity provider before and after changes.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> When diff mode is enabled</p>
    </td>
  </tr>
  </tbody>
  </table>


Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>
