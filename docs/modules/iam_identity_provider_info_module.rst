.. Created with antsibull-docs 2.24.0

dellemc.objectscale.iam_identity_provider_info module -- Get IAM SAML Identity Provider information from Dell ObjectScale
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.

To use it in a playbook, specify: ``dellemc.objectscale.iam_identity_provider_info``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Retrieves information about IAM SAML identity providers on the Dell ObjectScale storage system.
- Can retrieve details of a specific provider or list all providers in a namespace.
- This is a read-only module that does not make any changes.


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
      <div class="ansibleOptionAnchor" id="parameter-namespace"></div>
      <p style="display: inline;"><strong>namespace</strong></p>
      <a class="ansibleOptionLink" href="#parameter-namespace" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The ObjectScale namespace to query for identity providers.</p>
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
      <div class="ansibleOptionAnchor" id="parameter-provider_name"></div>
      <p style="display: inline;"><strong>provider_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-provider_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The name of a specific SAML identity provider to retrieve.</p>
      <p>When omitted, all providers in the namespace are listed.</p>
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


Notes
-----

- This is a read-only module; it never makes changes to the system.
- Provider ARN format is ``urn:ecs:iam::<namespace>:saml-provider/<provider_name>``.


Examples
--------

.. code-block:: yaml

    - name: List all SAML identity providers in a namespace
      dellemc.objectscale.iam_identity_provider_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "my-namespace"
      register: all_providers

    - name: Get details of a specific provider
      dellemc.objectscale.iam_identity_provider_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        provider_name: "my-saml-idp"
        namespace: "my-namespace"
      register: provider_info


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
      <p>Always false for info modules.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Sample:</b> <code style="color: blue;">false</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-identity_providers"></div>
      <p style="display: inline;"><strong>identity_providers</strong></p>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span> / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of identity provider details.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Sample:</b></p>
      <div style="margin-top: 8px;"><div class="highlight"><pre>
[
    {
        "provider_name": "my-saml-idp",
        "arn": "urn:ecs:iam::my-namespace:saml-provider/my-saml-idp",
        "create_date": "2025-01-15T12:00:00Z",
        "valid_until": "2030-12-31T23:59:59Z"
    }
]
</pre></div></div>
    </td>
  </tr>
  </tbody>
  </table>


Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>
