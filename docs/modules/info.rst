.. _dellemc.objectscale.info_module:

************************************
dellemc.objectscale.info module
************************************

**Version added: 1.0.0**

.. contents::
   :local:
   :depth: 1


Synopsis
--------

This module gathers information about ObjectScale entities.
Currently, it supports namespace discovery:

* List all namespaces
* Get a namespace by name
* Filter namespace list by name prefix/wildcard

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

.. raw:: HTML

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
       <td>gather_subset</td>
       <td><ul><li>namespace</li></ul></td>
       <td>List of entities to gather. Use C(namespace) to gather namespace information.</td>
   </tr>

.. raw:: html

   <tr>
       <td>query_parameters</td>
       <td></td>
       <td>Optional query parameters for namespace lookup. Supports C(namespace.name), C(namespace.match), C(namespace.limit), and C(namespace.marker).</td>
   </tr>

.. raw:: html

   </table>


Notes
-----

* This module does not modify the ObjectScale system configuration.
* Requires administrative credentials to retrieve information.
* Namespace list/get operations are supported through C(gather_subset: [namespace]).


Examples
--------

.. code-block:: yaml

    - name: Gather all namespaces
      dellemc.objectscale.info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        gather_subset:
          - namespace
      register: objectscale_info

    - name: Display namespaces
      debug:
        var: objectscale_info.Namespaces

    - name: Get a namespace by name
      dellemc.objectscale.info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        gather_subset:
          - namespace
        query_parameters:
          namespace:
            name: "finance-namespace"
      register: namespace_info

    - name: List namespaces by prefix
      dellemc.objectscale.info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        gather_subset:
          - namespace
        query_parameters:
          namespace:
            match: "team-*"


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
       <td>Indicates if any changes were made to the system</td>
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
       <td>Namespaces</td>
       <td>success</td>
       <td>List of namespace dictionaries with namespace properties returned from ObjectScale.</td>
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
