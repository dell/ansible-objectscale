.. _management_user_module:


management_user -- Manages VDC\-level Management Users on Dell ObjectScale
==========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Manages Management Users (administrators, operators, monitors, security admins) on the Dell ObjectScale storage system. This includes creating, modifying role assignments, changing password, and deleting Management Users via the :literal:`/vdc/users` REST API. These users are VDC\-scoped and are not associated with a namespace.

:literal:`Create`\ , :literal:`Update`\ , and :literal:`Delete` operations require the :emphasis:`SECURITY\_ADMIN` role.

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


  user_id (True, str, None)
    Unique identifier of the Management User. Upper case letters are not allowed.

    If user\_id does not contain :literal:`@`\ , the user is treated as a Local User.

    If user\_id contains :literal:`@`\ , the user is treated as an AD/LDAP User or AD/LDAP Group depending on :emphasis:`is\_external\_group`.


  password (optional, str, None)
    Password to set on the Management User.

    Required when creating a Local User. Must not be provided for AD/LDAP Users or AD/LDAP Groups.

    When provided during modify of a Local User, the password is (re)set; the module has no way to know the current password so providing this value always counts as a change.


  is_system_admin (optional, bool, None)
    Assign/remove the System Admin role.


  is_system_monitor (optional, bool, None)
    Assign/remove the System Monitor role.


  is_security_admin (optional, bool, None)
    Assign/remove the Security Admin role.


  is_external_group (optional, bool, None)
    Indicates the user is an external (domain) group. Only honored on create.

    Must be set to :literal:`true` when creating an AD/LDAP Group.

    Must not be set to :literal:`true` for Local Users or AD/LDAP Users.


  state (optional, str, present)
    Desired state of the Management User.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create a Local User with System Monitor role
      dellemc.objectscale.management_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_id: localuser1
        password: "{{ local_user_password }}"
        is_system_monitor: true
        state: present

    - name: Update Local User to System Admin and Security Admin roles
      dellemc.objectscale.management_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_id: localuser1
        is_system_admin: true
        is_security_admin: true
        state: present

    - name: Create an AD/LDAP User with System Monitor role
      dellemc.objectscale.management_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_id: user1@domain
        is_system_monitor: true
        state: present

    - name: Create an AD/LDAP Group with System Admin role
      dellemc.objectscale.management_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_id: group1@domain
        is_system_admin: true
        is_external_group: true
        state: present

    - name: Delete a Management User
      dellemc.objectscale.management_user:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        user_id: localuser1
        state: absent



Return Values
-------------

changed (always, bool, True)
  Whether the resource was changed.


management_user_details (when the user exists, dict, {'user_id': 'operator1', 'is_system_admin': False, 'is_system_monitor': True, 'is_security_admin': False, 'is_external_group': False, 'is_locked': False, 'last_time_password_changed': '2026-04-21T09:00:00Z'})
  Management User details after the operation.


  user_id (, str, )
    Management user identifier.


  is_system_admin (, bool, )
    True if the user holds the System Admin role.


  is_system_monitor (, bool, )
    True if the user holds the System Monitor role.


  is_security_admin (, bool, )
    True if the user holds the Security Admin role.


  is_external_group (, bool, )
    True if this is an external/domain group entry.


  is_locked (, bool, )
    True if the user is currently locked.


  last_time_password_changed (, str, )
    ISO\-8601 timestamp of last password change.



diff (when --diff is active and something changed, dict, )
  Diff between before and after state (when \-\-diff is used).





Status
------





Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

