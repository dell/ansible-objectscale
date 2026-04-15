.. _iam_policy_info_module:


iam_policy_info -- Gather IAM policy information from Dell ObjectScale
======================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather information about IAM managed policies on Dell ObjectScale.

Can retrieve a single policy by ARN or name, or list all policies in a namespace.

Supports optional enrichment with policy versions and the default policy document.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python \>= 3.9



Parameters
----------

  policy_name (False, str, None)
    The friendly name of the IAM policy to retrieve.

    Used to construct the policy ARN if :emphasis:`policy\_arn` is not provided.


  policy_arn (False, str, None)
    The Amazon Resource Name (ARN) of the IAM policy to retrieve.

    Takes precedence over :emphasis:`policy\_name` for identifying a specific policy.


  namespace_name (True, str, None)
    The ObjectScale namespace to query IAM policies from.


  include_policy_document (False, bool, False)
    Whether to include the default version policy document for each policy.


  include_versions (False, bool, False)
    Whether to include the list of policy versions for each policy.


  policy_scope (False, str, None)
    The scope to use for filtering the results when listing all policies.

    One of :literal:`All`\ , :literal:`ECS`\ , :literal:`AWS`\ , :literal:`Local`.


  only_attached (False, bool, False)
    A flag to filter the results to only the attached policies.


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
    Timeout in seconds for HTTP requests to ObjectScale.





Notes
-----

.. note::
   - The :emphasis:`check\_mode` is supported. This is a read\-only info module.
   - The objectscale\_client Python package must be installed. Generate it with :literal:`make build\_client` and install with :literal:`make install\_client`.
   - This module requires the ObjectScale Python client library.
   - The client library is included as part of the collection.
   - All operations are performed using the ObjectScale REST API.
   - SSL certificate verification can be disabled for testing environments.




Examples
--------

.. code-block:: yaml+jinja

    
    - name: List all IAM policies in a namespace
      dellemc.objectscale.iam_policy_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "mynamespace"
      register: all_policies

    - name: Get a specific IAM policy by ARN
      dellemc.objectscale.iam_policy_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "mynamespace"
        policy_arn: "urn:ecs:iam::mynamespace:policy/S3ReadOnlyPolicy"
      register: policy_info

    - name: Get a specific IAM policy by name with document and versions
      dellemc.objectscale.iam_policy_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "mynamespace"
        policy_name: "S3ReadOnlyPolicy"
        include_policy_document: true
        include_versions: true
      register: enriched_policy

    - name: List only attached policies in a namespace
      dellemc.objectscale.iam_policy_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        namespace_name: "mynamespace"
        only_attached: true
      register: attached_policies



Return Values
-------------

changed (always, bool, False)
  Whether or not the resource has changed. Always false for info modules.


iam_policies (always, list, [{'Arn': 'urn:ecs:iam::ns1:policy/S3ReadOnlyPolicy', 'PolicyId': 'ANPA1234567890', 'PolicyName': 'S3ReadOnlyPolicy', 'Description': 'Grants read-only access to S3 buckets', 'Path': '/', 'DefaultVersionId': 'v1', 'AttachmentCount': 2, 'IsAttachable': True, 'CreateDate': '2025-01-15T10:30:00Z', 'UpdateDate': '2025-01-15T10:30:00Z'}])
  List of IAM policy dictionaries.


  Arn (, str, )
    The Amazon Resource Name (ARN) of the policy.


  PolicyId (, str, )
    The unique identifier for the policy.


  PolicyName (, str, )
    The friendly name of the policy.


  Description (, str, )
    The description of the policy.


  Path (, str, )
    The path to the policy.


  DefaultVersionId (, str, )
    The identifier for the default version of the policy.


  AttachmentCount (, int, )
    The number of entities the policy is attached to.


  IsAttachable (, bool, )
    Whether the policy can be attached to entities.


  CreateDate (, str, )
    The date and time the policy was created.


  UpdateDate (, str, )
    The date and time the policy was last updated.


  policy_document (when include_policy_document is true, dict, )
    The default version policy document (when include\_policy\_document is true).


  versions (when include_versions is true, list, )
    List of policy version dicts (when include\_versions is true).






Status
------





Authors
~~~~~~~

- Dell Ansible Team (@dell)
- Dell Ansible Team (@dell) <ansible.team@dell.com>

