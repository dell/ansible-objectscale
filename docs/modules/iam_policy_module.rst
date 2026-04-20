.. Created with antsibull-docs 2.24.0

dellemc.objectscale.iam_policy module -- Manages IAM (S3) policies on Dell ObjectScale
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.

To use it in a playbook, specify: ``dellemc.objectscale.iam_policy``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Manages IAM (S3) managed policies on the Dell ObjectScale storage system. This includes creating, modifying (via policy versions), deleting, and retrieving details of IAM policies. Also supports attaching and detaching policies to/from IAM users, groups, and roles.








Parameters
----------

.. raw:: html

  <table style="width: 100%;">
  <thead>
    <tr>
    <th colspan="2"><p>Parameter</p></th>
    <th><p>Comments</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-attach_entities"></div>
      <p style="display: inline;"><strong>attach_entities</strong></p>
      <a class="ansibleOptionLink" href="#parameter-attach_entities" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of entities to attach the policy to.</p>
      <p>Each entity must have <em>entity_type</em> and <em>entity_name</em>.</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-attach_entities/entity_name"></div>
      <p style="display: inline;"><strong>entity_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-attach_entities/entity_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>Name of the IAM entity.</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-attach_entities/entity_type"></div>
      <p style="display: inline;"><strong>entity_type</strong></p>
      <a class="ansibleOptionLink" href="#parameter-attach_entities/entity_type" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>Type of the IAM entity.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;user&#34;</code></p></li>
        <li><p><code>&#34;group&#34;</code></p></li>
        <li><p><code>&#34;role&#34;</code></p></li>
      </ul>

    </td>
  </tr>

  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-description"></div>
      <p style="display: inline;"><strong>description</strong></p>
      <a class="ansibleOptionLink" href="#parameter-description" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>A friendly description for the policy.</p>
      <p>Only used during policy creation.</p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-detach_entities"></div>
      <p style="display: inline;"><strong>detach_entities</strong></p>
      <a class="ansibleOptionLink" href="#parameter-detach_entities" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of entities to detach the policy from.</p>
      <p>Each entity must have <em>entity_type</em> and <em>entity_name</em>.</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-detach_entities/entity_name"></div>
      <p style="display: inline;"><strong>entity_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-detach_entities/entity_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>Name of the IAM entity.</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-detach_entities/entity_type"></div>
      <p style="display: inline;"><strong>entity_type</strong></p>
      <a class="ansibleOptionLink" href="#parameter-detach_entities/entity_type" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>Type of the IAM entity.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;user&#34;</code></p></li>
        <li><p><code>&#34;group&#34;</code></p></li>
        <li><p><code>&#34;role&#34;</code></p></li>
      </ul>

    </td>
  </tr>

  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-namespace_name"></div>
      <p style="display: inline;"><strong>namespace_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-namespace_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The ObjectScale namespace (ECS namespace) that the IAM entity belongs to.</p>
      <p>Required when the request is performed by a management user.</p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
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
    <td colspan="2" valign="top">
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
    <td colspan="2" valign="top">
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
    <td colspan="2" valign="top">
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
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-path"></div>
      <p style="display: inline;"><strong>path</strong></p>
      <a class="ansibleOptionLink" href="#parameter-path" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The path for the policy.</p>
      <p>Defaults to "/" and only "/" is supported.</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">&#34;/&#34;</code></p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-policy_arn"></div>
      <p style="display: inline;"><strong>policy_arn</strong></p>
      <a class="ansibleOptionLink" href="#parameter-policy_arn" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The Amazon Resource Name (ARN) of the IAM policy.</p>
      <p>Used to identify an existing policy for get, update, delete, attach, and detach operations.</p>
      <p>Takes precedence over <em>policy_name</em> for identifying existing policies.</p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-policy_document"></div>
      <p style="display: inline;"><strong>policy_document</strong></p>
      <a class="ansibleOptionLink" href="#parameter-policy_document" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">json</span>
      </p>
    </td>
    <td valign="top">
      <p>The JSON policy document that defines the permissions for the policy.</p>
      <p>Must be a valid JSON string.</p>
      <p>Required when creating a new policy (<code class='docutils literal notranslate'>state=present</code> and policy does not exist).</p>
      <p>When provided for an existing policy, a new policy version is created with the updated document and set as the default version.</p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-policy_name"></div>
      <p style="display: inline;"><strong>policy_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-policy_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The friendly name of the IAM policy.</p>
      <p>Required when creating a new policy.</p>
      <p>Used to construct the policy ARN if <em>policy_arn</em> is not provided.</p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="parameter-state"></div>
      <p style="display: inline;"><strong>state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The desired state of the IAM policy.</p>
      <p><code class='docutils literal notranslate'>present</code> ensures the policy exists.</p>
      <p><code class='docutils literal notranslate'>absent</code> ensures the policy is deleted.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;present&#34;</code></p></li>
        <li><p><code>&#34;absent&#34;</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
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
    <td colspan="2" valign="top">
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

- The :emphasis:`check\_mode` is supported.
- The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client` and install with :literal:`make install\_client`.


Examples
--------

.. code-block:: yaml

    - name: Create an IAM policy with S3 read-only access
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_name: "S3ReadOnlyPolicy"
        policy_document: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": "*"
              }
            ]
          }
        description: "Grants read-only access to S3 buckets"
        state: present

    - name: Attach a policy to a user, group, and role
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
        attach_entities:
          - entity_type: user
            entity_name: alice
          - entity_type: group
            entity_name: developers
          - entity_type: role
            entity_name: s3-readonly-role
        state: present

    - name: Update the policy document (creates a new version)
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
        policy_document: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket", "s3:GetBucketLocation"],
                "Resource": "*"
              }
            ]
          }
        state: present

    - name: Detach a policy from a user, group, and role
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
        detach_entities:
          - entity_type: user
            entity_name: alice
          - entity_type: group
            entity_name: developers
          - entity_type: role
            entity_name: s3-readonly-role
        state: present

    - name: Delete an IAM policy
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
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
      <div class="ansibleOptionAnchor" id="return-policy_details"></div>
      <p style="display: inline;"><strong>policy_details</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>IAM policy details.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> When a policy exists</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>{&#34;Arn&#34;: &#34;urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy&#34;, &#34;AttachmentCount&#34;: 2, &#34;CreateDate&#34;: &#34;2025-01-15T10:30:00Z&#34;, &#34;DefaultVersionId&#34;: &#34;v1&#34;, &#34;Description&#34;: &#34;Grants read-only access to S3 buckets&#34;, &#34;IsAttachable&#34;: true, &#34;Path&#34;: &#34;/&#34;, &#34;PolicyId&#34;: &#34;ANPA1234567890&#34;, &#34;PolicyName&#34;: &#34;S3ReadOnlyPolicy&#34;, &#34;UpdateDate&#34;: &#34;2025-01-15T10:30:00Z&#34;}</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/Arn"></div>
      <p style="display: inline;"><strong>Arn</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/Arn" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The Amazon Resource Name (ARN) of the policy.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/AttachmentCount"></div>
      <p style="display: inline;"><strong>AttachmentCount</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/AttachmentCount" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Number of entities the policy is attached to.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/CreateDate"></div>
      <p style="display: inline;"><strong>CreateDate</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/CreateDate" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>ISO 8601 creation timestamp.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/DefaultVersionId"></div>
      <p style="display: inline;"><strong>DefaultVersionId</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/DefaultVersionId" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Identifier of the default policy version.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/Description"></div>
      <p style="display: inline;"><strong>Description</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/Description" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Friendly description of the policy.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/IsAttachable"></div>
      <p style="display: inline;"><strong>IsAttachable</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/IsAttachable" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether the policy can be attached to entities.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/Path"></div>
      <p style="display: inline;"><strong>Path</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/Path" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Path of the policy.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/PolicyId"></div>
      <p style="display: inline;"><strong>PolicyId</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/PolicyId" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Unique stable identifier of the policy.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/PolicyName"></div>
      <p style="display: inline;"><strong>PolicyName</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/PolicyName" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Friendly name of the policy.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-policy_details/UpdateDate"></div>
      <p style="display: inline;"><strong>UpdateDate</strong></p>
      <a class="ansibleOptionLink" href="#return-policy_details/UpdateDate" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>ISO 8601 last update timestamp.</p>
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
