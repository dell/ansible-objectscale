.. Created with antsibull-docs 2.24.0

dellemc.objectscale.iam_user_access_key module -- Manages IAM user access keys on Dell ObjectScale
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.
You need further requirements to be able to use this module,
see `Requirements <ansible_collections.dellemc.objectscale.iam_user_access_key_module_requirements_>`_ for details.

To use it in a playbook, specify: ``dellemc.objectscale.iam_user_access_key``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Manages IAM user S3\-compatible access keys on the Dell ObjectScale storage system.
- Supports creating a new access key, updating the status of an existing key (Active/Inactive), and deleting an access key.
- Creating a key returns a :literal:`secret\_access\_key` that is only available at creation time. Subsequent operations on the same key will never return the secret value.
- Supports :literal:`check\_mode` and :literal:`diff` mode.



.. _ansible_collections.dellemc.objectscale.iam_user_access_key_module_requirements:

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
      <p>Identifier of an existing access key to update or delete.</p>
      <p>Required when <em>state=absent</em> and when updating <em>status</em> of an existing key with <em>state=present</em>.</p>
      <p>When omitted with <em>state=present</em>, a new access key is created.</p>
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
      <div class="ansibleOptionAnchor" id="parameter-state"></div>
      <p style="display: inline;"><strong>state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The desired state of the access key.</p>
      <p><code class='docutils literal notranslate'>present</code> - the access key should exist. Creates a new key when <em>access_key_id</em> is not supplied, or updates the status of an existing key when <em>access_key_id</em> is supplied.</p>
      <p><code class='docutils literal notranslate'>absent</code> - the access key identified by <em>access_key_id</em> should not exist. The operation is idempotent.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code style="color: blue;"><b>&#34;present&#34;</b></code> <span style="color: blue;">← (default)</span></p></li>
        <li><p><code>&#34;absent&#34;</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-status"></div>
      <p style="display: inline;"><strong>status</strong></p>
      <a class="ansibleOptionLink" href="#parameter-status" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Desired status of the access key.</p>
      <p>Only applicable for updates of existing keys. New keys are always created in <code class='docutils literal notranslate'>Active</code> state by the server.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;Active&#34;</code></p></li>
        <li><p><code>&#34;Inactive&#34;</code></p></li>
      </ul>

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
      <p>Name of the IAM user to which the access key belongs.</p>
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

- Creation is not idempotent by itself; each run with :emphasis:`state=present` and no :emphasis:`access\_key\_id` creates a new access key. To manage an existing key idempotently, always supply :emphasis:`access\_key\_id`.
- The :literal:`secret\_access\_key` value is returned only on creation and is marked :literal:`no\_log`. It is never logged, surfaced in diff output, or returned on update/delete operations.
- The :emphasis:`check\_mode` and :emphasis:`diff` modes are supported.
- The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client`.
- This module requires the ObjectScale Python client library.
- The client library is included as part of the collection.
- All operations are performed using the ObjectScale REST API.
- SSL certificate verification can be disabled for testing environments.


Examples
--------

.. code-block:: yaml

    - name: Create a new access key for an IAM user
      dellemc.objectscale.iam_user_access_key:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: sample_user_1
        namespace_name: ns1
        state: present
      register: access_key_result
      no_log: true

    - name: Update access key status to Inactive
      dellemc.objectscale.iam_user_access_key:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: sample_user_1
        namespace_name: ns1
        access_key_id: "{{ access_key_result.access_key.AccessKeyId }}"
        status: Inactive
        state: present

    - name: Delete an access key
      dellemc.objectscale.iam_user_access_key:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: sample_user_1
        namespace_name: ns1
        access_key_id: AKIA80817B9F1F4C72CB
        state: absent




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
      <div class="ansibleOptionAnchor" id="return-access_key"></div>
      <p style="display: inline;"><strong>access_key</strong></p>
      <a class="ansibleOptionLink" href="#return-access_key" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>The access key metadata.</p>
      <p>On creation, contains <code class='docutils literal notranslate'>SecretAccessKey</code>; on update and on subsequent operations the secret is never returned.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> when state=present and the key exists or was created</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-access_key/AccessKeyId"></div>
      <p style="display: inline;"><strong>AccessKeyId</strong></p>
      <a class="ansibleOptionLink" href="#return-access_key/AccessKeyId" title="Permalink to this return value"></a>
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
      <div class="ansibleOptionAnchor" id="return-access_key/CreateDate"></div>
      <p style="display: inline;"><strong>CreateDate</strong></p>
      <a class="ansibleOptionLink" href="#return-access_key/CreateDate" title="Permalink to this return value"></a>
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
      <div class="ansibleOptionAnchor" id="return-access_key/SecretAccessKey"></div>
      <p style="display: inline;"><strong>SecretAccessKey</strong></p>
      <a class="ansibleOptionLink" href="#return-access_key/SecretAccessKey" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The secret access key. Returned ONLY at creation time and marked <code class='docutils literal notranslate'>no_log</code>. Never populated on updates.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> only when a new access key is created</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-access_key/Status"></div>
      <p style="display: inline;"><strong>Status</strong></p>
      <a class="ansibleOptionLink" href="#return-access_key/Status" title="Permalink to this return value"></a>
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
      <div class="ansibleOptionAnchor" id="return-access_key/UserName"></div>
      <p style="display: inline;"><strong>UserName</strong></p>
      <a class="ansibleOptionLink" href="#return-access_key/UserName" title="Permalink to this return value"></a>
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
      <p>Whether any change was made.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>true</code></p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="return-diff"></div>
      <p style="display: inline;"><strong>diff</strong></p>
      <a class="ansibleOptionLink" href="#return-diff" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Standard Ansible diff dictionary returned in diff mode.</p>
      <p>Secret access key values are never included in the diff. New keys show the placeholder <code class='docutils literal notranslate'>&lt;NEW_SECRET_KEY_GENERATED&gt;</code>; existing keys show <code class='docutils literal notranslate'>&lt;REDACTED&gt;</code>.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> when run with --diff</p>
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
