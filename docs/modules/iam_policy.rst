.. _iam_policy_module:


iam_policy -- Manages IAM (S3) policies on Dell ObjectScale
===========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Manages IAM (S3) managed policies on the Dell ObjectScale storage system. This includes creating, modifying (via policy versions), deleting, and retrieving details of IAM policies. Also supports attaching and detaching policies to/from IAM users, groups, and roles.






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

    Set to :literal:`false` when certificates are not trusted.


  timeout (False, int, 30)
    Timeout in seconds for HTTP requests to the ObjectScale management endpoint.


  policy_name (optional, str, None)
    The friendly name of the IAM policy.

    Required when creating a new policy.

    Used to construct the policy ARN if :emphasis:`policy\_arn` is not provided.


  policy_arn (optional, str, None)
    The Amazon Resource Name (ARN) of the IAM policy.

    Used to identify an existing policy for get, update, delete, attach, and detach operations.

    Takes precedence over :emphasis:`policy\_name` for identifying existing policies.


  policy_document (optional, json, None)
    The JSON policy document that defines the permissions for the policy.

    Must be a valid JSON string.

    Required when creating a new policy (\ :literal:`state=present` and policy does not exist).

    When provided for an existing policy, a new policy version is created with the updated document and set as the default version.


  description (optional, str, None)
    A friendly description for the policy.

    Only used during policy creation.


  path (optional, str, /)
    The path for the policy.

    Defaults to "/" and only "/" is supported.


  namespace_name (optional, str, None)
    The ObjectScale namespace (ECS namespace) that the IAM entity belongs to.

    Required when the request is performed by a management user.


  attach_entities (optional, list, None)
    List of entities to attach the policy to.

    Each entity must have :emphasis:`entity\_type` and :emphasis:`entity\_name`.


    entity_type (True, str, None)
      Type of the IAM entity.


    entity_name (True, str, None)
      Name of the IAM entity.



  detach_entities (optional, list, None)
    List of entities to detach the policy from.

    Each entity must have :emphasis:`entity\_type` and :emphasis:`entity\_name`.


    entity_type (True, str, None)
      Type of the IAM entity.


    entity_name (True, str, None)
      Name of the IAM entity.



  state (True, str, None)
    The desired state of the IAM policy.

    :literal:`present` ensures the policy exists.

    :literal:`absent` ensures the policy is deleted.





Notes
-----

.. note::
   - The :emphasis:`check\_mode` is supported.
   - The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client` and install with :literal:`make install\_client`.




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create an IAM policy with S3 read-only access
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_name: "S3ReadOnlyPolicy"
        policy_document: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": "*"
              }
            ]
          }
        description: "Grants read-only access to S3 buckets"
        state: present

    - name: Attach a policy to a user, group, and role
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
        attach_entities:
          - entity_type: user
            entity_name: alice
          - entity_type: group
            entity_name: developers
          - entity_type: role
            entity_name: s3-readonly-role
        state: present

    - name: Update the policy document (creates a new version)
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
        policy_document: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket", "s3:GetBucketLocation"],
                "Resource": "*"
              }
            ]
          }
        state: present

    - name: Detach a policy from a user, group, and role
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
        detach_entities:
          - entity_type: user
            entity_name: alice
          - entity_type: group
            entity_name: developers
          - entity_type: role
            entity_name: s3-readonly-role
        state: present

    - name: Delete an IAM policy
      dellemc.objectscale.iam_policy:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "{{ namespace_name }}"
        policy_arn: "urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy"
        state: absent



Return Values
-------------

changed (always, bool, False)
  Whether or not the resource has changed.


policy_details (When a policy exists, dict, {'Arn': 'urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy', 'PolicyId': 'ANPA1234567890', 'PolicyName': 'S3ReadOnlyPolicy', 'Description': 'Grants read-only access to S3 buckets', 'Path': '/', 'DefaultVersionId': 'v1', 'AttachmentCount': 2, 'IsAttachable': True, 'CreateDate': '2025-01-15T10:30:00Z', 'UpdateDate': '2025-01-15T10:30:00Z'})
  IAM policy details.


  Arn (, str, )
    The Amazon Resource Name (ARN) of the policy.


  PolicyId (, str, )
    Unique stable identifier of the policy.


  PolicyName (, str, )
    Friendly name of the policy.


  Description (, str, )
    Friendly description of the policy.


  Path (, str, )
    Path of the policy.


  DefaultVersionId (, str, )
    Identifier of the default policy version.


  AttachmentCount (, int, )
    Number of entities the policy is attached to.


  IsAttachable (, bool, )
    Whether the policy can be attached to entities.


  CreateDate (, str, )
    ISO 8601 creation timestamp.


  UpdateDate (, str, )
    ISO 8601 last update timestamp.






Status
------





Authors
~~~~~~~

- Dell Ansible Team (@dell) <ansible.team@dell.com>

