.. _object_user_info_module:


object_user_info -- Gathers information about non\-IAM Object Users on Dell ObjectScale
=======================================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Retrieves details for a single Object User or lists Object Users for a namespace or the whole VDC via the :literal:`/object/users` REST API. Optionally enriches each user with S3 secret key metadata (ids / timestamps only, plaintext values are never returned).






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


  user (optional, str, None)
    Identifier of the Object User. When provided, returns a single user.


  namespace (optional, str, None)
    Namespace filter. When :literal:`user` is provided, this qualifies the lookup. When :literal:`user` is not provided, returns the list of users for this namespace.


  include_secret_keys (optional, bool, False)
    When :literal:`true`\ , enrich each user with S3 secret key metadata. Only key ids and timestamps are returned; plaintext secret values are never included.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Get a single Object User
      dellemc.objectscale.object_user_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user: alice
        namespace: ns1
      register: user_info

    - name: List users in a namespace with secret key metadata
      dellemc.objectscale.object_user_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: ns1
        include_secret_keys: true

    - name: List all Object Users in the VDC
      dellemc.objectscale.object_user_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false



Return Values
-------------

changed (always, bool, False)
  Always false for info modules.


object_user (when I(user) is provided, dict, )
  A single Object User dict.


object_users (when I(user) is not provided, list, )
  List of Object User dicts.





Status
------





Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

