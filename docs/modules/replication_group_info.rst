.. _dellemc.objectscale.replication_group_info_module:

*********************************************
dellemc.objectscale.replication_group_info module
*********************************************

**Version added: 1.0.0**

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather information about ObjectScale replication groups. Can retrieve a single replication group by id, by name, or list all replication groups. Supports optional fetching of full details for each matched replication group.

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
       <td colspan=3><b>Replication Group Info</b></td>
   </tr>

.. raw:: html

   <tr>
       <td>id</td>
       <td></td>
       <td>Replication group identifier (URN). Mutually exclusive with I(name).</td>
   </tr>

.. raw:: html

   <tr>
       <td>name</td>
       <td></td>
       <td>Replication group name. Mutually exclusive with I(id).</td>
   </tr>

.. raw:: html

   <tr>
       <td>fetch_full_details</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>Fetch full details for each matched replication group. Default is C(true).</td>
   </tr>

.. raw:: html

   </table>


Notes
-----

* This module does not modify the ObjectScale system configuration.
* The I(check_mode) is supported. This is a read-only info module.
* The objectscale_client Python package must be installed. Generate it with C(make build_client) and install with C(make install_client).


Examples
--------

.. code-block:: yaml

    - name: List all replication groups
      dellemc.objectscale.replication_group_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
      register: all_replication_groups

    - name: Get replication group by id
      dellemc.objectscale.replication_group_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        id: urn:storageos:ReplicationGroupInfo:111:global
      register: replication_group_details

    - name: Get replication group by name
      dellemc.objectscale.replication_group_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        name: rg-ansible-01
      register: replication_group_details

    - name: List all replication groups without full details
      dellemc.objectscale.replication_group_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        fetch_full_details: false
      register: replication_groups_summary


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
       <td>always</td>
       <td>Whether or not the resource has changed. Always false for info modules.</td>
   </tr>

.. raw:: html

   <tr>
       <td>replication_groups</td>
       <td>always</td>
       <td>List of replication group dictionaries. Each entry contains id, name, description, mappings, and other replication group details.</td>
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
