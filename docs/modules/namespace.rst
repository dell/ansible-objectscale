.. _dellemc.objectscale.namespace_module:

***********************************************
dellemc.objectscale.namespace module
***********************************************

**Version added: 1.0.0**

.. contents::
   :local:
   :depth: 1


Synopsis
--------

This module manages namespaces in Dell ObjectScale. It can create, delete, and modify namespaces, as well as retrieve namespace information and manage quotas.

Parameters
----------

.. raw:: html

   <table  border=1 cellpadding=4>

.. raw:: html

   <tr>
       <th bgcolor="lightgrey">Parameter</th>
       <th bgcolor="lightgrey">Choices/<font color="blue">Defaults</font></th>
       <th bgcolor="lightgrey">Comments</th>
   </tr>

.. raw:: html

   <tr>
       <td colspan=3><b>Certificate</b></td>
   </tr>

.. raw:: html

   <tr>
       <td>ca_path</td>
       <td></td>
       <td>Path to the CA bundle to be used for SSL verification</td>
   </tr>

.. raw:: html

   <tr>
       <td>cert_file</td>
       <td></td>
       <td>Path to the client certificate file for SSL authentication</td>
   </tr>

.. raw:: html

   <tr>
       <td>key_file</td>
       <td></td>
       <td>Path to the client private key file for SSL authentication</td>
   </tr>

.. raw:: html

   <tr>
       <td>validate_certs</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>If C(False), SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.</td>
   </tr>

.. raw:: html

   <tr>
       <td colspan=3><b>Connection</b></td>
   </tr>

.. raw:: html

   <tr>
       <td>objectscale_host</td>
       <td></td>
       <td>ObjectScale management endpoint hostname or IP address</td>
   </tr>

.. raw:: html

   <tr>
       <td>objectscale_password</td>
       <td></td>
       <td>Password for authenticating with the ObjectScale management endpoint</td>
   </tr>

.. raw:: html

   <tr>
       <td>objectscale_port</td>
       <td>4443</td>
       <td>ObjectScale management endpoint port number</td>
   </tr>

.. raw:: html

   <tr>
       <td>objectscale_username</td>
       <td></td>
       <td>Username for authenticating with the ObjectScale management endpoint</td>
   </tr>

.. raw:: html

   <tr>
       <td>timeout</td>
       <td>30</td>
       <td>Request timeout in seconds</td>
   </tr>

.. raw:: html

   <tr>
       <td colspan=3><b>Namespace Configuration</b></td>
   </tr>

.. raw:: html

   <tr>
       <td>name</td>
       <td></td>
       <td>Name of the namespace to manage</td>
   </tr>

.. raw:: html

   <tr>
       <td>state</td>
       <td><ul><li>present</li><li>absent</li></ul></td>
       <td>Desired state of the namespace. C(present) to create/update, C(absent) to delete</td>
   </tr>

.. raw:: html

   <tr>
       <td>quota</td>
       <td></td>
       <td>Dictionary containing quota configuration for the namespace. Includes size_limit and object_limit</td>
   </tr>

.. raw:: html

   <tr>
       <td>retention_classes</td>
       <td></td>
       <td>List of retention classes to associate with the namespace</td>
   </tr>

.. raw:: html

   <tr>
       <td>compliance_enabled</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>Enable compliance mode for the namespace</td>
   </tr>

.. raw:: html

   </table>


Notes
-----

* This module requires administrative credentials to manage namespaces.
* Namespace names must be unique within the ObjectScale system.
* When deleting a namespace, all data within the namespace will be permanently deleted.


Examples
--------

.. code-block:: yaml

    - name: Create a new namespace
      dellemc.objectscale.namespace:
        name: "test_namespace"
        state: present
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        quota:
          size_limit: 100GB
          object_limit: 1000000
        retention_classes:
          - "standard"
          - "compliance"

    - name: Update namespace quota
      dellemc.objectscale.namespace:
        name: "test_namespace"
        state: present
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        quota:
          size_limit: 200GB

    - name: Delete a namespace
      dellemc.objectscale.namespace:
        name: "test_namespace"
        state: absent
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"

    - name: Get namespace information
      dellemc.objectscale.namespace:
        name: "test_namespace"
        state: present
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
      register: namespace_info


Return Values
-------------

.. raw:: html

   <table  border=1 cellpadding=4>

.. raw:: html

   <tr>
       <th bgcolor="lightgrey">Key</th>
       <th bgcolor="lightgrey">Returned</th>
       <th bgcolor="lightgrey">Description</th>
   </tr>

.. raw:: html

   <tr>
       <td>changed</td>
       <td>success</td>
       <td>Indicates if any changes were made to the namespace</td>
   </tr>

.. raw:: html

   <tr>
       <td>failed</td>
       <td>success</td>
       <td>Indicates if the module failed to execute</td>
   </tr>

.. raw:: html

   <tr>
       <td>msg</td>
       <td>success</td>
       <td>A message describing the operation result</td>
   </tr>

.. raw:: html

   <tr>
       <td>namespace</td>
       <td>success</td>
       <td>Dictionary containing namespace details including name, quota, retention classes, and configuration</td>
   </tr>

.. raw:: html

   <tr>
       <td>quota_info</td>
       <td>success</td>
       <td>Dictionary containing current quota usage and limits for the namespace</td>
   </tr>

.. raw:: html

   </table>


Status
------

This module is not guaranteed to have a backwards compatible interface. *[preview]*


Authors
~~~~~~~

* Dell Ansible Team (@dell) <ansible.team@dell.com>

.. hint::
    Configuration entries for each entry type have a low to high priority order. For example, a variable that is lower in the list will override variables that are higher up.

.. versionadded:: 1.0.0 of dellemc.objectscale
