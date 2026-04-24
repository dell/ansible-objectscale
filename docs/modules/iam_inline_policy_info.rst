.. vim: set fileencoding=utf-8 :

.. _dellemc.objectscale.iam_inline_policy_info_module:

=================================================
dellemc.objectscale.iam_inline_policy_info module
=================================================

**Gather IAM inline policy information from Dell ObjectScale**

.. contents::
   :local:
   :depth: 2

Version added: 1.0.0

Description
-----------

- Gather information about inline IAM policies on a user, group, or role
  in Dell ObjectScale.
- Returns the list of inline policy names and their documents for the specified entity.

.. note::
   - The check_mode is supported. This is a read-only info module.
   - The objectscale_client Python package must be installed.
     Generate it with make build_client and install with make install_client.

Parameters
----------

.. rst-class:: ansible-table

.. list-table::
   :width: 100%
   :widths: 2 8
   :header-rows: 1

   * - Parameter
     - Type
   * - **objectscale_host**
     - **string** / **required**

       IP address or FQDN of the ObjectScale management endpoint.
   * - **objectscale_port**
     - **integer**

       Port number for the ObjectScale management endpoint.

       **Default:** `4443`
   * - **objectscale_username**
     - **string** / **required**

       Username for authenticating with the ObjectScale management endpoint.
   * - **objectscale_password**
     - **string** / **required**

       Password for authenticating with the ObjectScale management endpoint.
   * - **validate_certs**
     - **boolean**

       Boolean value to enable or disable SSL certificate verification.

       **Default:** `true`
   * - **timeout**
     - **integer**

       Timeout in seconds for HTTP requests to the ObjectScale management endpoint.

       **Default:** `30`
   * - **namespace**
     - **string** / **required**

       The ObjectScale namespace in which the IAM entity resides.
   * - **user_name**
     - **string**

       The IAM user name whose inline policies to list.
       Exactly one of user_name, group_name, or role_name must be specified.
   * - **group_name**
     - **string**

       The IAM group name whose inline policies to list.
       Exactly one of user_name, group_name, or role_name must be specified.
   * - **role_name**
     - **string**

       The IAM role name whose inline policies to list.
       Exactly one of user_name, group_name, or role_name must be specified.

Examples
--------

.. code-block:: yaml+jinja

    - name: Get inline policies for an IAM user
      dellemc.objectscale.iam_inline_policy_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "userTest1"
      register: user_inline_policies

    - name: Get inline policies for an IAM group
      dellemc.objectscale.iam_inline_policy_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        group_name: "developers"
      register: group_inline_policies

    - name: Get inline policies for an IAM role
      dellemc.objectscale.iam_inline_policy_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        role_name: "admin-role"
      register: role_inline_policies

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
   * - **inline_policies**
     - **returned, list, elements=dict, sample**

       List of inline policies for the specified entity.

       contains:

       - **name** (returned, str, sample)
         The name of the inline policy.

       - **document** (returned, str, sample)
         The JSON policy document.
   * - **entity_type**
     - **returned, str, sample**

       The type of IAM entity queried (user, group, or role).
   * - **entity_name**
     - **returned, str, sample**

       The name of the IAM entity queried.
   * - **namespace**
     - **returned, str, sample**

       The ObjectScale namespace queried.

Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

.. seealso::
   :ref:`dellemc.objectscale.iam_inline_policy_module`
   :ref:`dellemc.objectscale.iam_user_module`
   :ref:`dellemc.objectscale.iam_group_module`
   :ref:`dellemc.objectscale.iam_role_module`
