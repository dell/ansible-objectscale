.. _object_user_module:


object_user -- Manages non\-IAM Object Users on Dell ObjectScale
================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Manages namespace\-scoped (non\-IAM) Object Users on the Dell ObjectScale storage system using the :literal:`/object/users` and :literal:`/object/user\-secret\-keys` REST APIs.

Supports create, delete, tag reconciliation, lock state management, and S3 secret key lifecycle (create/delete) for the user.

For IAM\-based user management, use the :ref:`dellemc.objectscale.iam\_user <ansible_collections.dellemc.objectscale.iam_user_module>` module instead.






Parameters
----------

  objectscale_host (True, str, None)
    IP address or FQDN of the ObjectScale management endpoint.


  objectscale_port (optional, int, 4443)
    Port number for the ObjectScale management endpoint.


  objectscale_username (True, str, None)
    Username for authenticating with ObjectScale.


  objectscale_password (True, str, None)
    Password for authenticating with ObjectScale.


  validate_certs (optional, bool, True)
    Whether to verify SSL certificates.


  timeout (optional, int, 30)
    HTTP request timeout in seconds.


  user (True, str, None)
    Identifier of the Object User.


  namespace (True, str, None)
    Namespace the Object User belongs to.


  tags (optional, list, None)
    Desired list of tags. Each entry must contain :literal:`name` and :literal:`value`.


  purge_tags (optional, bool, True)
    When :literal:`true`\ , tags not in the desired set are removed.


  locked (optional, bool, None)
    Desired lock state. When set, the module ensures the user is locked (\ :literal:`true`\ ) or unlocked (\ :literal:`false`\ ).


  secret_keys (optional, list, None)
    Desired S3 secret key declarations. Each entry is a dict with :literal:`state` (\ :literal:`present` or :literal:`absent`\ ) and optional :literal:`secret\_key\_id`\ , :literal:`secret\_key`\ , and :literal:`existing\_key\_expiry\_time\_mins`.

    For :literal:`state=present` with no existing keys matching, a new key is generated and its plaintext returned once under :literal:`created\_secret\_keys`.

    For :literal:`state=absent`\ , BOTH :literal:`secret\_key\_id` AND :literal:`secret\_key` must be provided to delete a specific key. The API requires the actual secret key value for security verification. Since secret keys are only returned once at creation, you must save the key value if you plan to delete it later. Note that even deleting all keys requires the actual key values for namespace\-scoped users.


  state (optional, str, present)
    Desired state of the Object User.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create an Object User in a namespace
      dellemc.objectscale.object_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user: alice
        namespace: ns1
        tags:
          - { name: env, value: prod }
        state: present

    - name: Create an S3 secret key for the user
      dellemc.objectscale.object_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user: alice
        namespace: ns1
        secret_keys:
          - state: present
        state: present
      register: s3_keys
      no_log: true

    - name: Lock the Object User
      dellemc.objectscale.object_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user: alice
        namespace: ns1
        locked: true

    - name: Delete a specific secret key (requires both ID and the actual key value)
      dellemc.objectscale.object_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user: alice
        namespace: ns1
        secret_keys:
          - secret_key_id: "{{ saved_key_id }}"
            secret_key: "{{ saved_key_value }}"
            state: absent
        state: present
      no_log: true

    - name: Delete the Object User
      dellemc.objectscale.object_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user: alice
        namespace: ns1
        state: absent



Return Values
-------------

changed (always, bool, )
  Whether the resource was changed.


object_user_details (when the user exists, dict, )
  Details of the Object User after the operation.


created_secret_keys (when a secret key was created, list, )
  S3 secret keys newly created during this run. Plaintext is returned once at creation time and should be captured securely (e.g., via Ansible Vault).





Status
------





Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

