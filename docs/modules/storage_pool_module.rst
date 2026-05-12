.. Created with antsibull-docs 2.24.0

dellemc.objectscale.storage_pool module -- Manage storage pools on Dell ObjectScale
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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

- Creates, modifies, and deletes storage pools on Dell ObjectScale.
- Supports idempotent operations — reruns without changes are safe.
- Supports check mode (dry-run) and diff mode (before/after comparison).


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
      <div class="ansibleOptionAnchor" id="parameter-error_alert_at"></div>
      <p style="display: inline;"><strong>error_alert_at</strong></p>
      <a class="ansibleOptionLink" href="#parameter-error_alert_at" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Percentage of used capacity at which an error alert is triggered.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-is_cold_storage_enabled"></div>
      <p style="display: inline;"><strong>is_cold_storage_enabled</strong></p>
      <a class="ansibleOptionLink" href="#parameter-is_cold_storage_enabled" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Enable or disable cold storage for this storage pool.</p>
      <p style="margin-top: 8px;"><b>Default:</b> <code style="color: blue;">false</code></p>
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
      <p style="margin-top: 8px;"><b>Default:</b> <code style="color: blue;">4443</code></p>
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
        / <span style="color: red;">required</span>
      </p>
    </td>
    <td valign="top">
      <p><code class="ansible-value literal notranslate">present</code> ensures the storage pool exists with specified configuration.</p>
      <p><code class="ansible-value literal notranslate">absent</code> ensures the storage pool does not exist.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code style="color: blue;"><b>&#34;present&#34;</b></code></p></li>
        <li><p><code style="color: blue;"><b>&#34;absent&#34;</b></code></p></li>
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
      <p>Name of the storage pool. Used as the primary identifier for idempotency checks.</p>
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
      <p style="margin-top: 8px;"><b>Default:</b> <code style="color: blue;">30</code></p>
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
      <p>Set to <code class="ansible-value literal notranslate">false</code> when certificates are not trusted.</p>
      <p style="margin-top: 8px;"><b>Default:</b> <code style="color: blue;">true</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-warning_alert_at"></div>
      <p style="display: inline;"><strong>warning_alert_at</strong></p>
      <a class="ansibleOptionLink" href="#parameter-warning_alert_at" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Percentage of used capacity at which a warning alert is triggered.</p>
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
      <p><span style="color: green"><strong>full</strong></span></p>
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
      <p><span style="color: green"><strong>full</strong></span></p>
    </td>
    <td valign="top">
      <p>Supports diff mode. Shows before and after state of the storage pool.</p>
    </td>
  </tr>
  </tbody>
  </table>


Notes
-----

- Storage pools are identified by name for idempotency.
- Supports check mode — use :code:`ansible\-playbook \-\-check` to preview changes.
- Supports diff mode — use :code:`ansible\-playbook \-\-diff` to show before/after.
- :code:`isProtected` is always set to false; protected varrays are not supported by ObjectScale.


Examples
--------

.. code-block:: yaml

    - name: Create a storage pool
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "sp_production"
        description: "Production storage pool"
        is_cold_storage_enabled: false
        warning_alert_at: 70
        error_alert_at: 85
        state: present

    - name: Modify a storage pool description
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "sp_production"
        description: "Updated production pool"
        state: present

    - name: Delete a storage pool
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "sp_staging"
        state: absent

    - name: Create pool (check mode — preview only)
      dellemc.objectscale.storage_pool:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        storage_pool_name: "sp_new"
        description: "New pool"
        state: present
      check_mode: true


Return Values
-------------

The following are the fields unique to this module:

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
      <a class="ansibleOptionLink" href="#return-changed" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether the storage pool was created, modified, or deleted.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px;"><b>Sample:</b> <code style="color: blue;">true</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-diff"></div>
      <p style="display: inline;"><strong>diff</strong></p>
      <a class="ansibleOptionLink" href="#return-diff" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Before/after comparison when diff mode is enabled.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> when diff mode enabled and changes made</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-storage_pool_details"></div>
      <p style="display: inline;"><strong>storage_pool_details</strong></p>
      <a class="ansibleOptionLink" href="#return-storage_pool_details" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>Details of the storage pool after the operation. Empty dict if deleted.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> when state=present and not check_mode</p>
    </td>
  </tr>
  </tbody>
  </table>
