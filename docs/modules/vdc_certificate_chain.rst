.. _dellemc.objectscale.vdc_certificate_chain:

**********************************************
dellemc.objectscale.vdc_certificate_chain
**********************************************

**Manage the Object-cert keystore certificate chain on Dell ObjectScale**

.. contents::
   :local:
   :depth: 2

Synopsis
========

- Uploads a private key and certificate chain to the Object-cert (S3/object) keystore via ``PUT /object-cert/keystore``.
- Supports idempotent operation by comparing SHA-256 fingerprints of the normalised PEM chain.
- When the desired chain is already installed, no change is made.
- Supports Ansible check mode and diff mode.
- This module manages the Object-cert keystore, which is distinct from the VDC management keystore managed by ``dellemc.objectscale.vdc_certificate``.

Parameters
==========

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Parameter
     - Comments
   * - ``objectscale_host``
     - FQDN or IP address of the ObjectScale management endpoint. (Required)
   * - ``objectscale_username``
     - Username for authentication. (Required)
   * - ``objectscale_password``
     - Password for authentication. (Required, no_log)
   * - ``validate_certs``
     - Whether to validate SSL certificates. (bool, default: true)
   * - ``timeout``
     - HTTP request timeout in seconds. (int, default: 30)
   * - ``state``
     - Desired state. Only ``present`` is supported. (str, default: present)
   * - ``private_key_path``
     - Path to a PEM-encoded private key file. Mutually exclusive with ``private_key_content``.
   * - ``private_key_content``
     - PEM-encoded private key as inline string. Mutually exclusive with ``private_key_path``. (no_log)
   * - ``certificate_chain_path``
     - Path to a PEM-encoded certificate chain file. Mutually exclusive with ``certificate_chain_content``.
   * - ``certificate_chain_content``
     - PEM-encoded certificate chain as inline string. Mutually exclusive with ``certificate_chain_path``.

Examples
========

.. code-block:: yaml

   - name: Upload Object-cert certificate chain from files
     dellemc.objectscale.vdc_certificate_chain:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
       private_key_path: /etc/ssl/private/objectscale.key
       certificate_chain_path: /etc/ssl/certs/objectscale-chain.pem
       state: present
     register: result

   - name: Upload Object-cert certificate chain inline
     dellemc.objectscale.vdc_certificate_chain:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
       private_key_content: "{{ vault_private_key }}"
       certificate_chain_content: "{{ vault_certificate_chain }}"
       state: present

Return Values
=============

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Key
     - Description
   * - ``changed``
     - Whether the certificate chain was updated. (bool)
   * - ``vdc_certificate_chain_details``
     - Dictionary with certificate metadata after the operation. (dict)
   * - ``vdc_certificate_chain_details.fingerprint``
     - SHA-256 fingerprint of the normalised certificate chain. (str)
   * - ``vdc_certificate_chain_details.chain``
     - PEM-encoded certificate chain. (str)
   * - ``vdc_certificate_chain_details.chain_length``
     - Count of certificates in the chain. (int)
   * - ``vdc_certificate_chain_details.leaf_subject``
     - X.509 subject of the leaf certificate (requires ``cryptography``). (str)
   * - ``vdc_certificate_chain_details.not_after``
     - ISO-8601 expiry of the leaf certificate (requires ``cryptography``). (str)
   * - ``diff``
     - Before/after fingerprint comparison (only in diff mode). (dict)

Notes
=====

- Requires the ``objectscale_client`` Python package.
- The ``cryptography`` Python package is optional but enables richer certificate metadata.
- Private key content is never logged or included in diff output.
- Uses failure codes FC-220 through FC-239 for specific error conditions.
