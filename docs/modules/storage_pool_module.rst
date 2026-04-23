.. Created with antsibull-docs 2.24.0

dellemc.objectscale.storage_pool module -- Manages storage pool configuration on Dell ObjectScale
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.

To use it in a playbook, specify: ``dellemc.objectscale.storage_pool``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Manages the storage pool configuration on the Dell ObjectScale storage system. This includes creating, modifying, deleting and retrieving details of a storage pool.











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
      <div class="ansibleOptionAnchor" id="parameter-compression_enabled"></div>
      <p style="display: inline;"><strong>compression_enabled</strong></p>
      <a class="ansibleOptionLink" href="#parameter-compression_enabled" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether compression is enabled for the storage pool.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-deduplication_enabled"></div>
      <p style="display: inline;"><strong>deduplication_enabled</strong></p>
      <a class="ansibleOptionLink" href="#parameter-deduplication_enabled" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether deduplication is enabled for the storage pool.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-description"></div>
      <p style="display: inline;"><strong>description</strong></p>
      <a class="ansibleOptionLink" href="#parameter-description" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Description of the storage pool.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-encryption_enabled"></div>
      <p style="display: inline;"><strong>encryption_enabled</strong></p>
      <a class="ansibleOptionLink" href="#parameter-encryption_enabled" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether encryption is enabled for the storage pool.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-is_protected"></div>
      <p style="display: inline;"><strong>is_protected</strong></p>
      <a class="ansibleOptionLink" href="#parameter-is_protected" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether the storage pool is protected from deletion.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-max_capacity"></div>
      <p style="display: inline;"><strong>max_capacity</strong></p>
      <a class="ansibleOptionLink" href="#parameter-max_capacity" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Maximum capacity of the storage pool in bytes.</p>
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
      <div class="ansibleOptionAnchor" id="parameter-protection_level"></div>
      <p style="display: inline;"><strong>protection_level</strong></p>
      <a class="ansibleOptionLink" href="#parameter-protection_level" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Protection level for the storage pool (e.g., <code class='docutils literal notranslate'>N+1</code>, <code class='docutils literal notranslate'>N+2</code>, <code class='docutils literal notranslate'>N+3</code>).</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;N+1&#34;</code></p></li>
        <li><p><code>&#34;N+2&#34;</code></p></li>
        <li><p><code>&#34;N+3&#34;</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-protection_type"></div>
      <p style="display: inline;"><strong>protection_type</strong></p>
      <a class="ansibleOptionLink" href="#parameter-protection_type" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Type of data protection (e.g., <code class='docutils literal notranslate'>replication</code>, <code class='docutils literal notranslate'>erasure_coding</code>).</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;replication&#34;</code></p></li>
        <li><p><code>&#34;erasure_coding&#34;</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-replication_factor"></div>
      <p style="display: inline;"><strong>replication_factor</strong></p>
      <a class="ansibleOptionLink" href="#parameter-replication_factor" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Replication factor for the storage pool.</p>
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
      <p>The state of the storage pool after the task is performed.</p>
      <p><code class='docutils literal notranslate'>present</code> - indicates that the storage pool should exist on the system.</p>
      <p><code class='docutils literal notranslate'>absent</code> - indicates that the storage pool should not exist on the system.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;present&#34;</code></p></li>
        <li><p><code>&#34;absent&#34;</code></p></li>
      </ul>

    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-storage_pool_name"></div>
      <p style="display: inline;"><strong>storage_pool_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-storage_pool_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p>The name of the storage pool.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-storage_pool_type"></div>
      <p style="display: inline;"><strong>storage_pool_type</strong></p>
      <a class="ansibleOptionLink" href="#parameter-storage_pool_type" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Type of storage pool (e.g., <code class='docutils literal notranslate'>all_flash</code>, <code class='docutils literal notranslate'>hybrid</code>, <code class='docutils literal notranslate'>performance</code>).</p>
      <p>Required when creating a storage pool.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>&#34;all_flash&#34;</code></p></li>
        <li><p><code>&#34;hybrid&#34;</code></p></li>
        <li><p><code>&#34;performance&#34;</code></p></li>
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


Examples
--------

.. code-block:: yaml

    - name: Create a storage pool
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "production_pool"
        storage_pool_type: "all_flash"
        protection_type: "replication"
        replication_factor: 3
        encryption_enabled: true
        compression_enabled: true
        deduplication_enabled: false
        state: "present"

    - name: Enable compression and deduplication on a storage pool
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "production_pool"
        compression_enabled: true
        deduplication_enabled: true
        state: "present"

    - name: Get storage pool details
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "production_pool"
        state: "present"

    - name: Delete a storage pool
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "production_pool"
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
      <div class="ansibleOptionAnchor" id="return-storage_pool_details"></div>
      <p style="display: inline;"><strong>storage_pool_details</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Storage pool details.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> When a storage pool exists</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>{&#34;compression_enabled&#34;: true, &#34;deduplication_enabled&#34;: false, &#34;description&#34;: &#34;Production storage pool&#34;, &#34;encryption_enabled&#34;: true, &#34;id&#34;: &#34;urn:storageos:StoragePoolInfo:xxxx:global&#34;, &#34;is_protected&#34;: false, &#34;max_capacity&#34;: 1099511627776, &#34;name&#34;: &#34;production_pool&#34;, &#34;protection_level&#34;: &#34;N+1&#34;, &#34;protection_type&#34;: &#34;replication&#34;, &#34;replication_factor&#34;: 3, &#34;storage_pool_type&#34;: &#34;all_flash&#34;}</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/compression_enabled"></div>
      <p style="display: inline;"><strong>compression_enabled</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/compression_enabled" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether compression is enabled.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/deduplication_enabled"></div>
      <p style="display: inline;"><strong>deduplication_enabled</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/deduplication_enabled" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether deduplication is enabled.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/description"></div>
      <p style="display: inline;"><strong>description</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/description" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Description of the storage pool.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/encryption_enabled"></div>
      <p style="display: inline;"><strong>encryption_enabled</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/encryption_enabled" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether encryption is enabled.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/id"></div>
      <p style="display: inline;"><strong>id</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/id" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Unique storage pool identifier.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/is_protected"></div>
      <p style="display: inline;"><strong>is_protected</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/is_protected" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether the storage pool is protected from deletion.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/max_capacity"></div>
      <p style="display: inline;"><strong>max_capacity</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/max_capacity" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Maximum capacity in bytes.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/name"></div>
      <p style="display: inline;"><strong>name</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/name" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Name of the storage pool.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/protection_level"></div>
      <p style="display: inline;"><strong>protection_level</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/protection_level" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Protection level of the storage pool.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/protection_type"></div>
      <p style="display: inline;"><strong>protection_type</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/protection_type" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Type of data protection.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/replication_factor"></div>
      <p style="display: inline;"><strong>replication_factor</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/replication_factor" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Replication factor.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details/storage_pool_type"></div>
      <p style="display: inline;"><strong>storage_pool_type</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details/storage_pool_type" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Type of storage pool.</p>
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
