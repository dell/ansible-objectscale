.. Created with antsibull-docs 2.24.0

dellemc.objectscale.namespace module -- Manages namespace configuration on Dell ObjectScale
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.

To use it in a playbook, specify: ``dellemc.objectscale.namespace``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Manages the namespace configuration on the Dell ObjectScale storage system. This includes creating, modifying and deleting a namespace.








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
      <div class="ansibleOptionAnchor" id="parameter-allowed_protocols"></div>
      <p style="display: inline;"><strong>allowed_protocols</strong></p>
      <a class="ansibleOptionLink" href="#parameter-allowed_protocols" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of protocols allowed for this namespace (e.g. <code class='docutils literal notranslate'>s3</code>, <code class='docutils literal notranslate'>atmos</code>, <code class='docutils literal notranslate'>swift</code>).</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-allowed_vpools_list"></div>
      <p style="display: inline;"><strong>allowed_vpools_list</strong></p>
      <a class="ansibleOptionLink" href="#parameter-allowed_vpools_list" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>Desired list of replication groups allowed for this namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-blocked_quota_size"></div>
      <p style="display: inline;"><strong>blocked_quota_size</strong></p>
      <a class="ansibleOptionLink" href="#parameter-blocked_quota_size" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Quota size (in bytes) at which new object creation is blocked.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-current_root_user_password"></div>
      <p style="display: inline;"><strong>current_root_user_password</strong></p>
      <a class="ansibleOptionLink" href="#parameter-current_root_user_password" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Current password for namespace virtual root user.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-default_audit_delete_expiration"></div>
      <p style="display: inline;"><strong>default_audit_delete_expiration</strong></p>
      <a class="ansibleOptionLink" href="#parameter-default_audit_delete_expiration" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Default bucket audit delete expiration for the namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-default_bucket_block_size"></div>
      <p style="display: inline;"><strong>default_bucket_block_size</strong></p>
      <a class="ansibleOptionLink" href="#parameter-default_bucket_block_size" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Default bucket quota size for buckets created in this namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-default_data_services_vpool"></div>
      <p style="display: inline;"><strong>default_data_services_vpool</strong></p>
      <a class="ansibleOptionLink" href="#parameter-default_data_services_vpool" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>The default data services replication group (vpool) for the namespace.</p>
      <p>Required when creating a namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-default_object_project"></div>
      <p style="display: inline;"><strong>default_object_project</strong></p>
      <a class="ansibleOptionLink" href="#parameter-default_object_project" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Default object project identifier used when creating buckets in this namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-default_replication_factor"></div>
      <p style="display: inline;"><strong>default_replication_factor</strong></p>
      <a class="ansibleOptionLink" href="#parameter-default_replication_factor" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Deprecated and currently unsupported by ObjectScale namespace API.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-disallowed_vpools_list"></div>
      <p style="display: inline;"><strong>disallowed_vpools_list</strong></p>
      <a class="ansibleOptionLink" href="#parameter-disallowed_vpools_list" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>Desired list of replication groups disallowed for this namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-external_group_admins"></div>
      <p style="display: inline;"><strong>external_group_admins</strong></p>
      <a class="ansibleOptionLink" href="#parameter-external_group_admins" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of Active Directory groups to set as external namespace administrators.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-hard_quota_size"></div>
      <p style="display: inline;"><strong>hard_quota_size</strong></p>
      <a class="ansibleOptionLink" href="#parameter-hard_quota_size" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Hard quota size (in bytes).</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-is_compliance_enabled"></div>
      <p style="display: inline;"><strong>is_compliance_enabled</strong></p>
      <a class="ansibleOptionLink" href="#parameter-is_compliance_enabled" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether compliance (WORM) is enabled for the namespace.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-is_encryption_enabled"></div>
      <p style="display: inline;"><strong>is_encryption_enabled</strong></p>
      <a class="ansibleOptionLink" href="#parameter-is_encryption_enabled" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether server-side encryption is enabled for the namespace.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-is_object_lock_with_ado_allowed"></div>
      <p style="display: inline;"><strong>is_object_lock_with_ado_allowed</strong></p>
      <a class="ansibleOptionLink" href="#parameter-is_object_lock_with_ado_allowed" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether Object Lock with ADO is allowed by default for new buckets in this namespace.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-is_stale_allowed"></div>
      <p style="display: inline;"><strong>is_stale_allowed</strong></p>
      <a class="ansibleOptionLink" href="#parameter-is_stale_allowed" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether reading from stale/secondary zone data is allowed.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-namespace_admins"></div>
      <p style="display: inline;"><strong>namespace_admins</strong></p>
      <a class="ansibleOptionLink" href="#parameter-namespace_admins" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of user IDs to set as namespace administrators.</p>
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
      <p>The name of the namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-new_root_user_password"></div>
      <p style="display: inline;"><strong>new_root_user_password</strong></p>
      <a class="ansibleOptionLink" href="#parameter-new_root_user_password" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>New password for namespace virtual root user.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-notification_quota_size"></div>
      <p style="display: inline;"><strong>notification_quota_size</strong></p>
      <a class="ansibleOptionLink" href="#parameter-notification_quota_size" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Quota size (in bytes) at which a notification is sent.</p>
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
      <div class="ansibleOptionAnchor" id="parameter-quota_enabled"></div>
      <p style="display: inline;"><strong>quota_enabled</strong></p>
      <a class="ansibleOptionLink" href="#parameter-quota_enabled" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether namespace quota is enabled.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-retention_classes"></div>
      <p style="display: inline;"><strong>retention_classes</strong></p>
      <a class="ansibleOptionLink" href="#parameter-retention_classes" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Desired list of retention classes for the namespace.</p>
      <p>Each entry should contain <code class='docutils literal notranslate'>name</code> and <code class='docutils literal notranslate'>period</code> in seconds.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-root_user_password"></div>
      <p style="display: inline;"><strong>root_user_password</strong></p>
      <a class="ansibleOptionLink" href="#parameter-root_user_password" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Password for namespace virtual root user when creating a namespace.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-soft_quota_size"></div>
      <p style="display: inline;"><strong>soft_quota_size</strong></p>
      <a class="ansibleOptionLink" href="#parameter-soft_quota_size" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Soft quota size (in bytes).</p>
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
      <p>The state of the namespace after the task is performed.</p>
      <p><code class='docutils literal notranslate'>present</code> - indicates that the namespace should exist on the system.</p>
      <p><code class='docutils literal notranslate'>absent</code> - indicates that the namespace should not exist on the system.</p>
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
      <div class="ansibleOptionAnchor" id="parameter-user_mapping"></div>
      <p style="display: inline;"><strong>user_mapping</strong></p>
      <a class="ansibleOptionLink" href="#parameter-user_mapping" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of namespace user mapping entries.</p>
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

- The :emphasis:`check\_mode` is not supported.
- The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client` and install with :literal:`make install\_client`.
- Use :emphasis:`dellemc.objectscale.namespace\_info` for listing namespaces and getting namespace details by name.


Examples
--------

.. code-block:: yaml

    - name: Create a namespace
      dellemc.objectscale.namespace:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "testnamespace"
        default_data_services_vpool: "urn:storageos:ReplicationGroupInfo:xxxx:global"
        namespace_admins:
          - "admin@example.com"
        is_compliance_enabled: false
        is_encryption_enabled: false
        state: "present"

    - name: Enable quota on a namespace
      dellemc.objectscale.namespace:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "testnamespace"
        quota_enabled: true
        hard_quota_size: 107374182400
        notification_quota_size: 85899345920
        state: "present"

    - name: Configure namespace user mapping and retention class
      dellemc.objectscale.namespace:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "testnamespace"
        user_mapping:
          - domain: "example.com"
            groups:
              - "ops"
            attributes:
              - key: "department"
                value:
                  - "engineering"
        retention_classes:
          - name: "compliance-7d"
            period: 604800
        state: "present"

    - name: Delete a namespace
      dellemc.objectscale.namespace:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "testnamespace"
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
      <div class="ansibleOptionAnchor" id="return-namespace_details"></div>
      <p style="display: inline;"><strong>namespace_details</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Namespace details.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> When a namespace exists</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>{&#34;allowed_protocols&#34;: [&#34;s3&#34;], &#34;default_data_services_vpool&#34;: &#34;urn:storageos:ReplicationGroupInfo:xxxx:global&#34;, &#34;default_replication_factor&#34;: 1, &#34;id&#34;: &#34;testnamespace&#34;, &#34;is_compliance_enabled&#34;: false, &#34;is_encryption_enabled&#34;: false, &#34;is_stale_allowed&#34;: false, &#34;name&#34;: &#34;testnamespace&#34;, &#34;namespace_admins&#34;: [&#34;admin@example.com&#34;]}</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/allowed_protocols"></div>
      <p style="display: inline;"><strong>allowed_protocols</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/allowed_protocols" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>Protocols allowed for this namespace.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/default_data_services_vpool"></div>
      <p style="display: inline;"><strong>default_data_services_vpool</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/default_data_services_vpool" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Default replication group for the namespace.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/default_replication_factor"></div>
      <p style="display: inline;"><strong>default_replication_factor</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/default_replication_factor" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Default replication factor.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/id"></div>
      <p style="display: inline;"><strong>id</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/id" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Unique namespace identifier.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/is_compliance_enabled"></div>
      <p style="display: inline;"><strong>is_compliance_enabled</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/is_compliance_enabled" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether compliance (WORM) mode is enabled.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/is_encryption_enabled"></div>
      <p style="display: inline;"><strong>is_encryption_enabled</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/is_encryption_enabled" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether server-side encryption is enabled.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/is_stale_allowed"></div>
      <p style="display: inline;"><strong>is_stale_allowed</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/is_stale_allowed" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether stale data reads are allowed.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/name"></div>
      <p style="display: inline;"><strong>name</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/name" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Name of the namespace.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-namespace_details/namespace_admins"></div>
      <p style="display: inline;"><strong>namespace_admins</strong></p>
      <a class="ansibleOptionLink" href="#return-namespace_details/namespace_admins" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of namespace administrator user IDs.</p>
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
