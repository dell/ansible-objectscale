.. Created with antsibull-docs 2.24.0

dellemc.objectscale.iam_user_access_key_info module -- Gather IAM user access key information from Dell ObjectScale
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.
You need further requirements to be able to use this module,
see `Requirements <ansible_collections.dellemc.objectscale.iam_user_access_key_info_module_requirements_>`_ for details.

To use it in a playbook, specify: ``dellemc.objectscale.iam_user_access_key_info``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Gather information about IAM user S3\-compatible access keys on Dell ObjectScale.
- Supports both a read operation (when :emphasis:`access\_key\_id` is supplied) and a list operation (when only :emphasis:`user\_name` and :emphasis:`namespace\_name` are supplied).
- This is a read\-only module and does not make any modifications to the target system.
- The :literal:`secret\_access\_key` is NEVER returned by this module. Only access key metadata (id, status, create date, user name) is returned.



.. _ansible_collections.dellemc.objectscale.iam_user_access_key_info_module_requirements:

Requirements
------------
The below requirements are needed on the host that executes this module.

- python \>= 3.9






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
      <div class="ansibleOptionAnchor" id="parameter-access_key_id"></div>
      <p style="display: inline;"><strong>access_key_id</strong></p>
      <a class="ansibleOptionLink" href="#parameter-access_key_id" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Identifier of a specific access key to read.</p>
      <p>When supplied, the module returns only that key&#x27;s metadata (or an empty list if it does not exist).</p>
      <p>When omitted, all access keys for the user are returned.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-namespace_name"></div>
      <p style="display: inline;"><strong>namespace_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-namespace_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The ObjectScale namespace that owns the IAM user.</p>
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
      <div class="ansibleOptionAnchor" id="parameter-timeout"></div>
      <p style="display: inline;"><strong>timeout</strong></p>
      <a class="ansibleOptionLink" href="#parameter-timeout" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Timeout in seconds for HTTP requests to ObjectScale.</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">30</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-user_name"></div>
      <p style="display: inline;"><strong>user_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-user_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>Name of the IAM user whose access keys should be queried.</p>
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
      <p>Set to <code class='docutils literal notranslate'>false</code> when certificates are not trusted.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code style="color: blue;"><b>true</b></code> <span style="color: blue;">← (default)</span></p></li>
      </ul>

    </td>
  </tr>
  </tbody>
  </table>




Notes
-----

- The :emphasis:`check\_mode` is supported. This is a read\-only info module.
- The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client`.
- This module requires the ObjectScale Python client library.
- The client library is included as part of the collection.
- All operations are performed using the ObjectScale REST API.
- SSL certificate verification can be disabled for testing environments.


Examples
--------

.. code-block:: yaml

    - name: List all access keys for an IAM user
      dellemc.objectscale.iam_user_access_key_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: sample_user_1
        namespace_name: ns1
      register: all_keys

    - name: Get details of a specific access key
      dellemc.objectscale.iam_user_access_key_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: sample_user_1
        namespace_name: ns1
        access_key_id: AKIA80817B9F1F4C72CB
      register: specific_key




Return Values
-------------
The following are the fields unique to this module:

.. raw:: html

  <table style="width: 100%;">
  <thead>
    <tr>
    <th colspan="2"><p>Key</p></th>
    <th><p>Description</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="return-access_keys"></div>
      <p style="display: inline;"><strong>access_keys</strong></p>
      <a class="ansibleOptionLink" href="#return-access_keys" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of access key metadata dicts.</p>
      <p>When <em>access_key_id</em> is supplied, contains 0 or 1 entries.</p>
      <p>The <code class='docutils literal notranslate'>SecretAccessKey</code> is never included.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>[{&#34;AccessKeyId&#34;: &#34;AKIA80817B9F1F4C72CB&#34;, &#34;CreateDate&#34;: &#34;2025-01-15T10:30:00Z&#34;, &#34;Status&#34;: &#34;Active&#34;, &#34;UserName&#34;: &#34;sample_user_1&#34;}]</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-access_keys/AccessKeyId"></div>
      <p style="display: inline;"><strong>AccessKeyId</strong></p>
      <a class="ansibleOptionLink" href="#return-access_keys/AccessKeyId" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The access key identifier.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-access_keys/CreateDate"></div>
      <p style="display: inline;"><strong>CreateDate</strong></p>
      <a class="ansibleOptionLink" href="#return-access_keys/CreateDate" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The date and time the access key was created.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-access_keys/Status"></div>
      <p style="display: inline;"><strong>Status</strong></p>
      <a class="ansibleOptionLink" href="#return-access_keys/Status" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The status of the access key (Active or Inactive).</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-access_keys/UserName"></div>
      <p style="display: inline;"><strong>UserName</strong></p>
      <a class="ansibleOptionLink" href="#return-access_keys/UserName" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The IAM user the access key belongs to.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>

  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="return-changed"></div>
      <p style="display: inline;"><strong>changed</strong></p>
      <a class="ansibleOptionLink" href="#return-changed" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Always false for info modules.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>false</code></p>
    </td>
  </tr>
  </tbody>
  </table>




Authors
~~~~~~~

- Dell Ansible Team (@dell)
- Dell Ansible Team (@dell)


Collection links
~~~~~~~~~~~~~~~~

* `Issue Tracker <https://www.dell.com/community/Automation/bd\-p/Automation>`__
* `Repository (Sources) <https://github.com/dell/ansible\-objectscale/tree/main>`__
