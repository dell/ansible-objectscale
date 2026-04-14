.. _dellemc.objectscale.iam_user_module:

***********************************************
dellemc.objectscale.iam_user module
***********************************************

**Version added: 1.0.0**

.. contents::
   :local:
   :depth: 1


Synopsis
--------

This module manages IAM users on the Dell ObjectScale storage system. This includes creating, modifying, deleting and retrieving details of IAM users, managing their tags, policies, groups, permissions boundaries, and access keys.

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
       <td colspan=3><b>IAM User Configuration</b></td>
   </tr>

.. raw:: html

   <tr>
       <td>user_name</td>
       <td></td>
       <td>The name of the IAM user. Required.</td>
   </tr>

.. raw:: html

   <tr>
       <td>namespace_name</td>
       <td></td>
       <td>The namespace for the IAM user. Required.</td>
   </tr>

.. raw:: html

   <tr>
       <td>state</td>
       <td><ul><li>present</li><li>absent</li></ul></td>
       <td>Desired state of the IAM user. C(present) to create/update, C(absent) to delete. Default is C(present).</td>
   </tr>

.. raw:: html

   <tr>
       <td>path</td>
       <td>/</td>
       <td>The path for the IAM user</td>
   </tr>

.. raw:: html

   <tr>
       <td>permissions_boundary</td>
       <td></td>
       <td>The ARN of the managed policy to set as the permissions boundary. Set to empty string to remove the boundary.</td>
   </tr>

.. raw:: html

   <tr>
       <td>tags</td>
       <td></td>
       <td>Dictionary of tags to apply to the user</td>
   </tr>

.. raw:: html

   <tr>
       <td>purge_tags</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>If true, remove tags not in the desired set. Default is C(true).</td>
   </tr>

.. raw:: html

   <tr>
       <td>managed_policies</td>
       <td></td>
       <td>List of managed policy ARNs to attach to the user</td>
   </tr>

.. raw:: html

   <tr>
       <td>purge_managed_policies</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>If true, detach policies not in the desired list. Default is C(true).</td>
   </tr>

.. raw:: html

   <tr>
       <td>inline_policies</td>
       <td></td>
       <td>Dictionary of inline policy names to policy documents</td>
   </tr>

.. raw:: html

   <tr>
       <td>purge_inline_policies</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>If true, delete inline policies not in the desired set. Default is C(true).</td>
   </tr>

.. raw:: html

   <tr>
       <td>groups</td>
       <td></td>
       <td>List of group names the user should belong to</td>
   </tr>

.. raw:: html

   <tr>
       <td>purge_groups</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>If true, remove user from groups not in the desired list. Default is C(true).</td>
   </tr>

.. raw:: html

   <tr>
       <td>access_key_state</td>
       <td><ul><li>present</li><li>absent</li></ul></td>
       <td>State for access key operations. C(present) creates a new access key. C(absent) deletes an existing access key.</td>
   </tr>

.. raw:: html

   <tr>
       <td>access_key_id</td>
       <td></td>
       <td>The access key ID for delete or status update operations</td>
   </tr>

.. raw:: html

   <tr>
       <td>access_key_status</td>
       <td><ul><li>Active</li><li>Inactive</li></ul></td>
       <td>Desired status for an access key</td>
   </tr>

.. raw:: html

   <tr>
       <td>force_delete</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>If true, remove all dependencies before deleting the user. Default is C(false).</td>
   </tr>

.. raw:: html

   </table>


Notes
-----

* This module requires administrative credentials to manage IAM users.
* The I(check_mode) is supported.
* The objectscale_client Python package must be installed. Generate it with C(make build_client) and install with C(make install_client).
* When deleting a user with dependencies, set I(force_delete) to C(true) to remove all access keys, policies, group memberships, and permissions boundaries before deletion.


Examples
--------

.. code-block:: yaml

    - name: Create an IAM user
      dellemc.objectscale.iam_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: "testuser"
        namespace_name: "testns"
        state: present

    - name: Create IAM user with tags and policies
      dellemc.objectscale.iam_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: "testuser"
        namespace_name: "testns"
        tags:
          Env: prod
          Team: ops
        managed_policies:
          - "urn:ecs:iam::testns:policy/ReadOnly"
        groups:
          - admins
        state: present

    - name: Delete an IAM user with force cleanup
      dellemc.objectscale.iam_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_name: "testuser"
        namespace_name: "testns"
        state: absent
        force_delete: true


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
       <td>Whether or not the resource has changed</td>
   </tr>

.. raw:: html

   <tr>
       <td>user</td>
       <td>When user exists and state is present</td>
       <td>Dictionary containing IAM user details including UserName, Arn, UserId, CreateDate, and Path</td>
   </tr>

.. raw:: html

   <tr>
       <td>access_key</td>
       <td>When access_key_state is present</td>
       <td>Dictionary containing created access key details including AccessKeyId, SecretAccessKey, and Status</td>
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
