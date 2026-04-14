.. _dellemc.objectscale.iam_role_info_module:

*********************************************
dellemc.objectscale.iam_role_info module
*********************************************

**Version added: 1.0.0**

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather information about IAM roles on Dell ObjectScale. Can retrieve a single role by name or list all roles in a namespace. Supports optional enrichment with attached managed policies, inline policies, and role tags.

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
       <td colspan=3><b>IAM Role Info</b></td>
   </tr>

.. raw:: html

   <tr>
       <td>role_name</td>
       <td></td>
       <td>The name of the IAM role to retrieve. If not specified, all roles in the namespace are listed.</td>
   </tr>

.. raw:: html

   <tr>
       <td>namespace_name</td>
       <td></td>
       <td>The ObjectScale namespace to query IAM roles from. Required.</td>
   </tr>

.. raw:: html

   <tr>
       <td>include_attached_policies</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>Whether to include attached managed policies for each role. Default is C(false).</td>
   </tr>

.. raw:: html

   <tr>
       <td>include_inline_policies</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>Whether to include inline policy names for each role. Default is C(false).</td>
   </tr>

.. raw:: html

   <tr>
       <td>inline_policy_name</td>
       <td></td>
       <td>Name of a specific inline policy to retrieve the document for.</td>
   </tr>

.. raw:: html

   <tr>
       <td>include_tags</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>Whether to include role tags for each role. Default is C(false).</td>
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

    - name: List all IAM roles in a namespace
      dellemc.objectscale.iam_role_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "mynamespace"
      register: all_roles

    - name: Get a specific IAM role with policies and tags
      dellemc.objectscale.iam_role_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "mynamespace"
        role_name: "app-data-access-role"
        include_attached_policies: true
        include_inline_policies: true
        include_tags: true
      register: role_info

    - name: List all roles with full enrichment
      dellemc.objectscale.iam_role_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "mynamespace"
        include_attached_policies: true
        include_inline_policies: true
        include_tags: true
      register: enriched_roles


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
       <td>iam_roles</td>
       <td>always</td>
       <td>List of IAM role dictionaries. Each entry contains RoleName, RoleId, Arn, CreateDate, Path, AssumeRolePolicyDocument, Description, MaxSessionDuration, and PermissionsBoundary. Optional fields include attached_policies, inline_policies, and role_tags depending on include_* parameters.</td>
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
