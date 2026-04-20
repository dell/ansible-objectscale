.. _iam_policy_attachment_module:


iam_policy_attachment -- Manage IAM policy attachments on Dell ObjectScale
==========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Attaches or detaches managed IAM policies to/from a target principal (user, group, or role) in Dell ObjectScale.

Supports diff\-based idempotency.

When :emphasis:`state=absent`\ , all currently attached policies are detached.






Parameters
----------

  objectscale_host (True, str, None)
    IP address or FQDN of the ObjectScale management endpoint.


  objectscale_port (False, int, 4443)
    Port number for the ObjectScale management endpoint.


  objectscale_username (True, str, None)
    Username for authenticating with the ObjectScale management endpoint.


  objectscale_password (True, str, None)
    Password for authenticating with the ObjectScale management endpoint.


  validate_certs (False, bool, True)
    Boolean value to enable or disable SSL certificate verification.


  timeout (False, int, 30)
    Timeout in seconds for HTTP requests to the ObjectScale management endpoint.


  namespace (True, str, None)
    The ObjectScale namespace in which the IAM entity resides.


  user_name (optional, str, None)
    Name of the IAM user. Exactly one of :emphasis:`user\_name`\ , :emphasis:`group\_name`\ , or :emphasis:`role\_name` must be specified.


  group_name (optional, str, None)
    Name of the IAM group. Exactly one of :emphasis:`user\_name`\ , :emphasis:`group\_name`\ , or :emphasis:`role\_name` must be specified.


  role_name (optional, str, None)
    Name of the IAM role. Exactly one of :emphasis:`user\_name`\ , :emphasis:`group\_name`\ , or :emphasis:`role\_name` must be specified.


  policy_arns (optional, list, None)
    List of managed policy ARNs to associate with the entity.

    Required when :emphasis:`state=present`.


  state (optional, str, present)
    Desired state of the policy attachment.

    :literal:`present` ensures the specified policies are attached (diff\-based).

    :literal:`absent` detaches all currently attached policies.





Notes
-----

.. note::
   - The :emphasis:`check\_mode` is supported.
   - The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client` and install with :literal:`make install\_client`.




Examples
--------

.. code-block:: yaml+jinja

    - name: Attach policies to an IAM user
      dellemc.objectscale.iam_policy_attachment:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "userTest1"
        policy_arns:
          - "urn:ecs:iam:::policy/ECSS3ReadOnlyAccess"
          - "urn:ecs:iam:::policy/IAMReadOnlyAccess"
        state: present

    - name: Attach policies to a group
      dellemc.objectscale.iam_policy_attachment:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        group_name: "developers"
        policy_arns:
          - "urn:ecs:iam:::policy/ECSS3FullAccess"
        state: present

    - name: Attach policy to a role
      dellemc.objectscale.iam_policy_attachment:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        role_name: "admin-role"
        policy_arns:
          - "urn:ecs:iam:::policy/IAMFullAccess"
        state: present

    - name: Detach all policies from a user
      dellemc.objectscale.iam_policy_attachment:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "userTest1"
        state: absent

    - name: Check mode - preview policy attachment
      dellemc.objectscale.iam_policy_attachment:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace: "ns1"
        user_name: "userTest1"
        policy_arns:
          - "urn:ecs:iam:::policy/ECSS3ReadOnlyAccess"
        state: present
      check_mode: true



Return Values
-------------

changed (always, bool, True)
  Whether or not the resource has changed.


policy_attachment_details (always, dict, sample)
  Details of the policy attachment state after the operation.

  contains:

    namespace (str)
      The ObjectScale namespace.

    entity_type (str)
      The type of IAM entity (user, group, or role).

    entity_name (str)
      The name of the IAM entity.

    attached_policy_arns (list)
      List of policy ARNs currently attached to the entity.

  sample: {'namespace': 'ns1', 'entity_type': 'user', 'entity_name': 'userTest1', 'attached_policy_arns': ['urn:ecs:iam:::policy/ECSS3ReadOnlyAccess', 'urn:ecs:iam:::policy/IAMReadOnlyAccess']}



id (always, str, sample)
  Resource identifier in format namespace:entity_type:entity_name.


diff (When diff mode is enabled, dict, sample)
  Diff of the attached policies before and after changes.





Status
------





Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

