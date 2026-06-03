.. Created with antsibull-docs 2.24.0

dellemc.objectscale.vdc_info module -- Gather VDC (Virtual Data Center) information from Dell ObjectScale
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `dellemc.objectscale collection <https://galaxy.ansible.com/ui/repo/published/dellemc/objectscale/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible\-galaxy collection install dellemc.objectscale`.
You need further requirements to be able to use this module,
see `Requirements <ansible_collections.dellemc.objectscale.vdc_info_module_requirements_>`_ for details.

To use it in a playbook, specify: ``dellemc.objectscale.vdc_info``.

New in dellemc.objectscale 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------

- Gather information about ObjectScale Virtual Data Centers (VDCs).
- Supports listing all VDCs in a single site or across a multi-site federation.
- Supports fetching a specific VDC by name or by ID.
- Supports fetching the local VDC details.
- All operations are non-disruptive read-only queries.
- The ``secretKeys`` field is always omitted from output to prevent credential exposure.



.. _ansible_collections.dellemc.objectscale.vdc_info_module_requirements:

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
      <div class="ansibleOptionAnchor" id="parameter-local_vdc"></div>
      <p style="display: inline;"><strong>local_vdc</strong></p>
      <a class="ansibleOptionLink" href="#parameter-local_vdc" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>When <code class='docutils literal notranslate'>true</code>, retrieves only the local VDC details.</p>
      <p>Mutually exclusive with <em>vdc_name</em> and <em>vdc_id</em>.</p>
      <p style="margin-top: 8px;"><b">Choices:</b></p>
      <ul>
        <li><p><code>false</code></p></li>
        <li><p><code>true</code></p></li>
      </ul>
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
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-vdc_id"></div>
      <p style="display: inline;"><strong>vdc_id</strong></p>
      <a class="ansibleOptionLink" href="#parameter-vdc_id" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Unique identifier of the VDC to retrieve.</p>
      <p>If specified, returns details of a single VDC matching that ID.</p>
      <p>Mutually exclusive with <em>vdc_name</em> and <em>local_vdc</em>.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-vdc_name"></div>
      <p style="display: inline;"><strong>vdc_name</strong></p>
      <a class="ansibleOptionLink" href="#parameter-vdc_name" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Name of the VDC to retrieve.</p>
      <p>If specified, returns details of a single VDC matching that name.</p>
      <p>Mutually exclusive with <em>vdc_id</em> and <em>local_vdc</em>.</p>
    </td>
  </tr>
  </tbody>
  </table>




Notes
-----

- The :emphasis:`check\_mode` is supported. This is a read\-only info module.
- The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client` and install with :literal:`make install\_client`.
- The ``secretKeys`` field is omitted from all returned VDC records to prevent credential exposure in logs or playbook output.
- When none of :emphasis:`vdc\_name`, :emphasis:`vdc\_id`, or :emphasis:`local\_vdc` is specified, all VDCs in the federation are returned.
- For a single\-site deployment, the list will contain one VDC (the local VDC).
- Parameters :emphasis:`vdc\_name`, :emphasis:`vdc\_id`, and :emphasis:`local\_vdc` are mutually exclusive.


Examples
--------

.. code-block:: yaml

    - name: List all VDCs in the federation
      dellemc.objectscale.vdc_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
      register: result

    - name: Get local VDC details
      dellemc.objectscale.vdc_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        local_vdc: true
      register: result

    - name: Get VDC details by name
      dellemc.objectscale.vdc_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        vdc_name: "vdc-site-a"
      register: result

    - name: Get VDC details by ID
      dellemc.objectscale.vdc_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        vdc_id: "urn:storageos:VirtualDataCenterData:abc123"
      register: result




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
      <p>Whether the resource changed. Always <code>false</code> for info modules.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>false</code></p>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs"></div>
      <p style="display: inline;"><strong>vdcs</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">list</span>
        / <span style="color: purple;">elements=dictionary</span>
      </p>
    </td>
    <td valign="top">
      <p>List of VDC records from the ObjectScale system.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/creation_time"></div>
      <p style="display: inline;"><strong>creation_time</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/creation_time" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">integer</span>
      </p>
    </td>
    <td valign="top">
      <p>Unix timestamp (ms) when this VDC was created in ECS.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/global"></div>
      <p style="display: inline;"><strong>global</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/global" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether this is a global VDC resource.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/hosted"></div>
      <p style="display: inline;"><strong>hosted</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/hosted" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether this VDC is hosted.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/id"></div>
      <p style="display: inline;"><strong>id</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/id" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Unique immutable identifier generated by ECS for this VDC.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>&#34;urn:storageos:VirtualDataCenterData:27154c1a-876e-4480-bcc1-1e047a2dc057&#34;</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/inactive"></div>
      <p style="display: inline;"><strong>inactive</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/inactive" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether the VDC is inactive (pending removal).</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/interVdcCmdEndPoints"></div>
      <p style="display: inline;"><strong>interVdcCmdEndPoints</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/interVdcCmdEndPoints" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Comma-separated list of inter-VDC command endpoints.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/interVdcEndPoints"></div>
      <p style="display: inline;"><strong>interVdcEndPoints</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/interVdcEndPoints" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Comma-separated list of inter-VDC communication endpoints.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/internal"></div>
      <p style="display: inline;"><strong>internal</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/internal" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether this is an internal VDC resource.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/is_encryption_enabled"></div>
      <p style="display: inline;"><strong>is_encryption_enabled</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/is_encryption_enabled" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether encryption is enabled for this VDC.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/local"></div>
      <p style="display: inline;"><strong>local</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/local" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether this VDC is the local (current site) VDC.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/managementEndPoints"></div>
      <p style="display: inline;"><strong>managementEndPoints</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/managementEndPoints" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Management endpoints for this VDC.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/name"></div>
      <p style="display: inline;"><strong>name</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/name" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>User-assigned name for this VDC resource.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>&#34;vdc1&#34;</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/permanentlyFailed"></div>
      <p style="display: inline;"><strong>permanentlyFailed</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/permanentlyFailed" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether this VDC is in a permanently failed state.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/remote"></div>
      <p style="display: inline;"><strong>remote</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/remote" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">boolean</span>
      </p>
    </td>
    <td valign="top">
      <p>Whether this is a remote (federated) VDC.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/vdcId"></div>
      <p style="display: inline;"><strong>vdcId</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/vdcId" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>VDC identifier string used in federation operations.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>&#34;urn:storageos:VirtualDataCenterData:27154c1a-876e-4480-bcc1-1e047a2dc057&#34;</code></p>
    </td>
  </tr>
  <tr>
    <td></td>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-vdcs/vdcName"></div>
      <p style="display: inline;"><strong>vdcName</strong></p>
      <a class="ansibleOptionLink" href="#return-vdcs/vdcName" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>VDC name string used in federation operations.</p>
      <p style="margin-top: 8px;"><b>Returned:</b> success</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>&#34;vdc1&#34;</code></p>
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
