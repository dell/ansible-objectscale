.. _dellemc.objectscale.iam_role_module:

***********************************************
dellemc.objectscale.iam_role module
***********************************************

**Version added: 1.0.0**

.. contents::
   :local:
   :depth: 1


Synopsis
--------

This module manages IAM roles on the Dell ObjectScale storage system. This includes creating, modifying, deleting and retrieving details of IAM roles, managing their trust policies, tags, managed policies, inline policies, and permissions boundaries.

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
       <td colspan=3><b>IAM Role Configuration</b></td>
   </tr>

.. raw:: html

   <tr>
       <td>role_name</td>
       <td></td>
       <td>The name of the IAM role. Required.</td>
   </tr>

.. raw:: html

   <tr>
       <td>namespace_name</td>
       <td></td>
       <td>The namespace for the IAM role. Required.</td>
   </tr>

.. raw:: html

   <tr>
       <td>state</td>
       <td><ul><li>present</li><li>absent</li></ul></td>
       <td>Desired state of the IAM role. C(present) to create/update, C(absent) to delete. Default is C(present).</td>
   </tr>

.. raw:: html

   <tr>
       <td>assume_role_policy_document</td>
       <td></td>
       <td>The trust relationship policy document (JSON dict) that grants an entity permission to assume the role. Required when creating a new role.</td>
   </tr>

.. raw:: html

   <tr>
       <td>description</td>
       <td></td>
       <td>A description of the IAM role.</td>
   </tr>

.. raw:: html

   <tr>
       <td>max_session_duration</td>
       <td></td>
       <td>The maximum session duration (in seconds) for the role. Valid range is 3600 to 43200 (1 hour to 12 hours).</td>
   </tr>

.. raw:: html

   <tr>
       <td>path</td>
       <td>/</td>
       <td>The path for the IAM role</td>
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
       <td>Dictionary of tags to apply to the role</td>
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
       <td>List of managed policy ARNs to attach to the role</td>
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
       <td>force_delete</td>
       <td><ul><li>True</li><li>False</li></ul></td>
       <td>If true, remove all dependencies before deleting the role. Default is C(false).</td>
   </tr>

.. raw:: html

   </table>


Notes
-----

* This module requires administrative credentials to manage IAM roles.
* The I(check_mode) is supported.
* The objectscale_client Python package must be installed. Generate it with C(make build_client) and install with C(make install_client).
* When deleting a role with dependencies, set I(force_delete) to C(true) to remove all attached policies, inline policies, and permissions boundaries before deletion.


Examples
--------

.. code-block:: yaml

    - name: Create an IAM role
      dellemc.objectscale.iam_role:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        role_name: "app-data-access-role"
        namespace_name: "testns"
        assume_role_policy_document:
          Version: "2012-10-17"
          Statement:
            - Effect: Allow
              Principal:
                AWS:
                  - "urn:ecs:iam::testns:user/app-service"
              Action: "sts:AssumeRole"
        state: present

    - name: Create IAM role with tags, policies and description
      dellemc.objectscale.iam_role:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        role_name: "finance-data-role"
        namespace_name: "testns"
        assume_role_policy_document:
          Version: "2012-10-17"
          Statement:
            - Effect: Allow
              Principal:
                AWS:
                  - "urn:ecs:iam::testns:user/finance-admin"
              Action: "sts:AssumeRole"
        description: "Finance team data access role"
        max_session_duration: 7200
        tags:
          Env: prod
          Team: finance
        managed_policies:
          - "urn:ecs:iam::testns:policy/ReadOnly"
        state: present

    - name: Delete an IAM role with force cleanup
      dellemc.objectscale.iam_role:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        role_name: "app-data-access-role"
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
       <td>role</td>
       <td>When role exists and state is present</td>
       <td>Dictionary containing IAM role details including RoleName, Arn, RoleId, CreateDate, Path, AssumeRolePolicyDocument, Description, and MaxSessionDuration</td>
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
