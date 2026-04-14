.. Created with antsibull-docs 2.24.0

dellemc.objectscale.iam_group module -- Manage IAM groups on Dell ObjectScale
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.

To use it in a playbook, specify: ``dellemc.objectscale.iam_group``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Manages IAM groups on the Dell ObjectScale storage system. This includes creating, modifying, deleting and retrieving details of an IAM group.
- Supports managing group membership (users), attached managed policies, and inline policies.
- All operations are scoped to a specific ObjectScale namespace.








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
      <div class="ansibleOptionAnchor" id="parameter-group_name"></div>
      <p style="display: inline;"><strong>group_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-group_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The name of the IAM group.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-inline_policies"></div>
      <p style="display: inline;"><strong>inline_policies</strong></p>
      <a class="ansibleOptionLink" href="#parameter-inline_policies" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of inline policies to manage on the group.</p>
      <p>Each item is a dictionary with <code class='docutils literal notranslate'>name</code> and <code class='docutils literal notranslate'>document</code> keys.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-inline_policy_state"></div>
      <p style="display: inline;"><strong>inline_policy_state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-inline_policy_state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Determines how the <em>inline_policies</em> list is applied.</p>
      <p><code class='docutils literal notranslate'>present-in-group</code> ensures the specified inline policies exist on the group.</p>
      <p><code class='docutils literal notranslate'>absent-in-group</code> ensures the specified inline policies are removed from the group.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code style="color: blue;"><b>&#34;present-in-group&#34;</b></code> <span style="color: blue;">← (default)</span></p></li>
        <li><p><code>&#34;absent-in-group&#34;</code></p></li>
      </ul>

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
      <p>The ObjectScale namespace in which the group resides.</p>
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
      <div class="ansibleOptionAnchor" id="parameter-path"></div>
      <p style="display: inline;"><strong>path</strong></p>
      <a class="ansibleOptionLink" href="#parameter-path" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The IAM path prefix for the group.</p>
      <p>Only used during group creation.</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">&#34;/&#34;</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-policies"></div>
      <p style="display: inline;"><strong>policies</strong></p>
      <a class="ansibleOptionLink" href="#parameter-policies" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of managed policy ARNs to manage on the group.</p>
      <p>Behavior is controlled by <em>policy_state</em>.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-policy_state"></div>
      <p style="display: inline;"><strong>policy_state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-policy_state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Determines how the <em>policies</em> list is applied.</p>
      <p><code class='docutils literal notranslate'>present-in-group</code> ensures the specified policies are attached to the group.</p>
      <p><code class='docutils literal notranslate'>absent-in-group</code> ensures the specified policies are detached from the group.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code style="color: blue;"><b>&#34;present-in-group&#34;</b></code> <span style="color: blue;">← (default)</span></p></li>
        <li><p><code>&#34;absent-in-group&#34;</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-state"></div>
      <p style="display: inline;"><strong>state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The desired state of the IAM group.</p>
      <p><code class='docutils literal notranslate'>present</code> ensures the group exists with the specified configuration.</p>
      <p><code class='docutils literal notranslate'>absent</code> ensures the group does not exist. All users, managed policies, and inline policies are removed before the group is deleted.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;present&#34;</code></p></li>
        <li><p><code>&#34;absent&#34;</code></p></li>
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
      <p>Timeout in seconds for HTTP requests to the ObjectScale management endpoint.</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">30</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-user_state"></div>
      <p style="display: inline;"><strong>user_state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-user_state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Determines how the <em>users</em> list is applied.</p>
      <p><code class='docutils literal notranslate'>present-in-group</code> ensures the specified users are members of the group.</p>
      <p><code class='docutils literal notranslate'>absent-in-group</code> ensures the specified users are removed from the group.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code style="color: blue;"><b>&#34;present-in-group&#34;</b></code> <span style="color: blue;">← (default)</span></p></li>
        <li><p><code>&#34;absent-in-group&#34;</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-users"></div>
      <p style="display: inline;"><strong>users</strong></p>
      <a class="ansibleOptionLink" href="#parameter-users" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of IAM user names to manage in the group.</p>
      <p>Behavior is controlled by <em>user_state</em>.</p>
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




Attributes
----------

.. list-table::
  :widths: auto
  :header-rows: 1

  * - Attribute
    - Support
    - Description

  * - .. _ansible_collections.dellemc.objectscale.iam_group_module__attribute-check_mode:

      **check_mode**

    - Support: full



    -
      Supports check mode. No changes will be made when check mode is enabled.



  * - .. _ansible_collections.dellemc.objectscale.iam_group_module__attribute-diff_mode:

      **diff_mode**

    - Support: full



    -
      Supports diff mode. Shows before and after state of the IAM group.




Notes
-----

- The :emphasis:`check\_mode` is supported.
- The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client` and install with :literal:`make install\_client`.


Examples
--------

.. code-block:: yaml

    - name: Create an IAM group
      dellemc.objectscale.iam_group:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        group_name: "developers"
        namespace: "my-namespace"
        state: "present"

    - name: Add users to an IAM group
      dellemc.objectscale.iam_group:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        group_name: "developers"
        namespace: "my-namespace"
        users:
          - "alice"
          - "bob"
        user_state: "present-in-group"
        state: "present"

    - name: Attach managed policies to an IAM group
      dellemc.objectscale.iam_group:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        group_name: "developers"
        namespace: "my-namespace"
        policies:
          - "urn:ecs:iam:::policy/ReadOnlyAccess"
        policy_state: "present-in-group"
        state: "present"

    - name: Add an inline policy to an IAM group
      dellemc.objectscale.iam_group:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        group_name: "developers"
        namespace: "my-namespace"
        inline_policies:
          - name: "AllowS3List"
            document: '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:ListBucket","Resource":"*"}]}'
        inline_policy_state: "present-in-group"
        state: "present"

    - name: Remove users from an IAM group
      dellemc.objectscale.iam_group:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        group_name: "developers"
        namespace: "my-namespace"
        users:
          - "bob"
        user_state: "absent-in-group"
        state: "present"

    - name: Check mode - preview group creation
      dellemc.objectscale.iam_group:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        group_name: "preview-group"
        namespace: "my-namespace"
        state: "present"
      check_mode: true

    - name: Delete an IAM group
      dellemc.objectscale.iam_group:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        group_name: "developers"
        namespace: "my-namespace"
        state: "absent"




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
      <div class="ansibleOptionAnchor" id="return-changed"></div>
      <p style="display: inline;"><strong>changed</strong></p>
      <a class="ansibleOptionLink" href="#return-changed" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether or not the resource has changed.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>false</code></p>
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
      <p>Diff of the IAM group before and after changes.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> When diff mode is enabled</p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details"></div>
      <p style="display: inline;"><strong>iam_group_details</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>IAM group details.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> When state is <code class='docutils literal notranslate'>present</code> and the group exists</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>{&#34;arn&#34;: &#34;urn:ecs:iam::my-namespace:group/developers&#34;, &#34;attached_policies&#34;: [{&#34;policy_arn&#34;: &#34;urn:ecs:iam:::policy/ReadOnlyAccess&#34;, &#34;policy_name&#34;: &#34;ReadOnlyAccess&#34;}], &#34;create_date&#34;: &#34;2025-01-15T12:00:00Z&#34;, &#34;group_id&#34;: &#34;AGPA1234567890EXAMPLE&#34;, &#34;group_name&#34;: &#34;developers&#34;, &#34;inline_policies&#34;: [&#34;AllowS3List&#34;], &#34;path&#34;: &#34;/&#34;, &#34;users&#34;: [&#34;alice&#34;, &#34;bob&#34;]}</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/arn"></div>
      <p style="display: inline;"><strong>arn</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/arn" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The Amazon Resource Name (ARN) of the group.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/attached_policies"></div>
      <p style="display: inline;"><strong>attached_policies</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/attached_policies" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of managed policies attached to the group.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/create_date"></div>
      <p style="display: inline;"><strong>create_date</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/create_date" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The date and time when the group was created.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/group_id"></div>
      <p style="display: inline;"><strong>group_id</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/group_id" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The unique identifier for the IAM group.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/group_name"></div>
      <p style="display: inline;"><strong>group_name</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/group_name" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The name of the IAM group.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/inline_policies"></div>
      <p style="display: inline;"><strong>inline_policies</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/inline_policies" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of inline policy names on the group.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/path"></div>
      <p style="display: inline;"><strong>path</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/path" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The IAM path prefix for the group.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-iam_group_details/users"></div>
      <p style="display: inline;"><strong>users</strong></p>
      <a class="ansibleOptionLink" href="#return-iam_group_details/users" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of user names that are members of the group.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>

  </tbody>
  </table>




Authors
~~~~~~~

- Dell Ansible Team (@dell)


Collection links
~~~~~~~~~~~~~~~~

* `Issue Tracker <https://www.dell.com/community/Automation/bd\-p/Automation>`__
* `Repository (Sources) <https://github.com/dell/ansible\-objectscale/tree/main>`__
