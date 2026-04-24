.. vim: set fileencoding=utf-8 :

.. _dellemc.objectscale.iam_inline_policy_module:

==============================================
dellemc.objectscale.iam_inline_policy module
==============================================

**Manage IAM inline policies on Dell ObjectScale**

.. contents::
   :local:
   :depth: 2

Version added: 1.0.0

.. contents::
   :local:
   :depth: 2

Description
-----------

- Manages IAM inline policies for Dell ObjectScale entities (user, group, or role).
- Supports creating, updating, and deleting multiple inline policies on a single entity.
- Uses diff-based idempotency — only changed policies are applied.
- When state=absent, all existing inline policies on the entity are deleted.

.. note::
   - The check_mode is supported.
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
     
       Name of the IAM user. Exactly one of user_name, group_name, or role_name must be specified.
   * - **group_name**
     - **string**
     
       Name of the IAM group. Exactly one of user_name, group_name, or role_name must be specified.
   * - **role_name**
     - **string**
     
       Name of the IAM role. Exactly one of user_name, group_name, or role_name must be specified.
   * - **policies**
     - **list** / **elements=dict**
     
       List of inline policies to associate with the entity.
       Each item must be a dict with name (str) and document (JSON str) keys.
       Required when state=present.
   * - **state**
     - **string**
     
       Desired state of the inline policies.
       present ensures the specified policies are applied (diff-based).
       absent deletes all inline policies from the entity.
     
       **Choices:** `['present', 'absent']`
       **Default:** `present`

Examples
--------

.. code-block:: yaml+jinja

    - name: Set inline policies on IAM user
      dellemc.objectscale.iam_inline_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "userTest1"
        policies:
          - name: "readOnlyPolicy"
            document: |
              {
                "Version": "2012-10-17",
                "Statement": [
                  {
                    "Effect": "Allow",
                    "Action": ["iam:Get*", "iam:List*"],
                    "Resource": "*"
                  }
                ]
              }
        state: present

    - name: Set inline policies on IAM group
      dellemc.objectscale.iam_inline_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        group_name: "developers"
        policies:
          - name: "s3Access"
            document: |
              {
                "Version": "2012-10-17",
                "Statement": [
                  {
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": "*"
                  }
                ]
              }
        state: present

    - name: Set inline policies on IAM role
      dellemc.objectscale.iam_inline_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        role_name: "admin-role"
        policies:
          - name: "fullAccess"
            document: |
              {
                "Version": "2012-10-17",
                "Statement": [
                  {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                  }
                ]
              }
        state: present

    - name: Remove all inline policies from user
      dellemc.objectscale.iam_inline_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "userTest1"
        state: absent

    - name: Check mode - preview inline policy changes
      dellemc.objectscale.iam_inline_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "userTest1"
        policies:
          - name: "readOnlyPolicy"
            document: '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["iam:Get*"],"Resource":"*"}]}'
        state: present
        check_mode: true

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
     
       Whether or not the resource has changed.
   * - **inline_policy_details**
     - **returned, dict, sample**
     
       Details of the inline policy state after the operation.
     
       contains:
       
       - **namespace** (returned, str, sample)
         The ObjectScale namespace.
       
       - **entity_type** (returned, str, sample)
         The type of IAM entity (user, group, or role).
       
       - **entity_name** (returned, str, sample)
         The name of the IAM entity.
       
       - **policies** (returned, list, elements=dict, sample)
         List of inline policies on the entity.
   * - **id**
     - **returned, str, sample**
     
       Resource identifier in format namespace:entity_type:entity_name.
   * - **diff**
     - **returned, dict, sample**
     
       Diff of the inline policies before and after changes.

Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

.. seealso::
   :ref:`dellemc.objectscale.iam_user_module`
   :ref:`dellemc.objectscale.iam_group_module`
   :ref:`dellemc.objectscale.iam_role_module`
   :ref:`dellemc.objectscale.iam_policy_module`
