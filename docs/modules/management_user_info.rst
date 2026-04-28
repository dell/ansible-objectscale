.. _management_user_info_module:


management_user_info -- Gathers information about Management Users on Dell ObjectScale
======================================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Retrieves details for a single Management User or lists all Management Users on Dell ObjectScale via the :literal:`/vdc/users` REST API.

:literal:`Read` operations require any one of :emphasis:`SECURITY\_ADMIN`\ , :emphasis:`SYSTEM\_ADMIN`\ , or :emphasis:`SYSTEM\_MONITOR` roles.






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


  user_id (optional, str, None)
    User identifier. When provided, returns details of the single user.

    When omitted, returns a list of all Management Users.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: List all Management Users
      dellemc.objectscale.management_user_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
      register: all_mgmt_users

    - name: Get a single Management User
      dellemc.objectscale.management_user_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_id: operator1
      register: mgmt_user



Return Values
-------------

changed (always, bool, False)
  Always false for info modules.


management_user (when I(user_id) is provided, dict, )
  Details of a single Management User.


management_users (when I(user_id) is omitted, list, )
  List of Management User dicts.





Status
------





Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

