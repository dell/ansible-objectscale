.. vim: set fileencoding=utf-8 :

.. _dellemc.objectscale.iam_policy_attachment_info_module:

===========================================
dellemc.objectscale.iam_policy_attachment_info module
===========================================

**Gather IAM policy attachment information from Dell ObjectScale**

.. contents::
   :local:
   :depth: 2

Version added: 1.0.0

.. contents::
   :local:
   :depth: 2

Description
-----------

- Gather information about managed IAM policies attached to a user, group, or role
  on Dell ObjectScale.
- Returns the list of attached policy ARNs and names for the specified entity.

Parameters
----------

.. rst-class:: ansible-table

.. list-table::
   :width: 100%
   :widths: 2 8
   :header-rows: 1

   * - Parameter
     - Type
   * - **namespace**
     - **string** / **required**
     
       The ObjectScale namespace in which the IAM entity resides.
   * - **user_name**
     - **string**
     
       The IAM user name whose attached policies to list.
       Exactly one of user_name, group_name, or role_name must be specified.
   * - **group_name**
     - **string**
     
       The IAM group name whose attached policies to list.
       Exactly one of user_name, group_name, or role_name must be specified.
   * - **role_name**
     - **string**
     
       The IAM role name whose attached policies to list.
       Exactly one of user_name, group_name, or role_name must be specified.

.. note::
   - The check_mode is supported. This is a read-only info module.
   - The objectscale_client Python package must be installed.
     Generate it with make build_client and install with make install_client.

Examples
--------

.. code-block:: yaml+jinja

    - name: List attached policies for an IAM user
      dellemc.objectscale.iam_policy_attachment_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "testuser"
      register: user_policies

    - name: List attached policies for an IAM group
      dellemc.objectscale.iam_policy_attachment_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        group_name: "developers"
      register: group_policies

    - name: List attached policies for an IAM role
      dellemc.objectscale.iam_policy_attachment_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        role_name: "admin-role"
      register: role_policies

Return Values
--------------

.. rst-class:: ansible-table

.. list-table::
   :width: 100%
   :widths: 2 8
   :header-rows: 1

   * - Key
     - Description
   * - **changed**
     - **returned, bool, sample**
     
       Whether or not the resource has changed. Always false for info modules.
   * - **iam_attached_policies**
     - **returned, list, elements=dict, sample**
     
       List of attached policy dictionaries for the specified entity.
     
       contains:
       
       - **PolicyName** (returned, str, sample)
         The friendly name of the attached policy.
       
       - **PolicyArn** (returned, str, sample)
         The Amazon Resource Name (ARN) of the attached policy.
   * - **entity_type**
     - **returned, str, sample**
     
       The type of IAM entity queried (user, group, or role).
   * - **entity_name**
     - **returned, str, sample**
     
       The name of the IAM entity queried.

Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

.. seealso::
   :ref:`dellemc.objectscale.iam_policy_attachment_module`
   :ref:`dellemc.objectscale.iam_policy_module`
   :ref:`dellemc.objectscale.iam_user_module`
   :ref:`dellemc.objectscale.iam_group_module`
