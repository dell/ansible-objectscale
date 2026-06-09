.. _dellemc.objectscale.vdc_certificate:

*****************************************
dellemc.objectscale.vdc_certificate
*****************************************

**Manage the VDC keystore private key and certificate chain on Dell ObjectScale**

.. contents::
   :local:
   :depth: 2

Synopsis
========

- Sets or replaces the VDC-level TLS private key and certificate chain via the ``PUT /vdc/keystore`` API.
- Supports idempotency — compares SHA-256 fingerprints of the desired vs. current certificate chain and skips the update when they match.
- Supports Ansible check mode and diff mode.
- Private key material is never logged or included in diff output (``no_log: true``).

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
   * - ``private_key_content``
     - PEM-encoded private key as an inline string. Mutually exclusive with ``private_key_path``. (no_log)
   * - ``private_key_path``
     - Filesystem path to a PEM-encoded private key file. Mutually exclusive with ``private_key_content``.
   * - ``certificate_chain_content``
     - PEM-encoded certificate chain as an inline string. Mutually exclusive with ``certificate_chain_path``.
   * - ``certificate_chain_path``
     - Filesystem path to a PEM-encoded certificate chain file. Mutually exclusive with ``certificate_chain_content``.
   * - ``timeout``
     - HTTP request timeout in seconds. (int, default: 30)

Examples
========

.. code-block:: yaml

   - name: Set VDC certificate from inline PEM content
     dellemc.objectscale.vdc_certificate:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
       private_key_content: "{{ lookup('file', 'server.key') }}"
       certificate_chain_content: "{{ lookup('file', 'server-chain.pem') }}"

   - name: Set VDC certificate from file paths
     dellemc.objectscale.vdc_certificate:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
       private_key_path: /etc/ssl/private/server.key
       certificate_chain_path: /etc/ssl/certs/server-chain.pem

   - name: Dry-run (check mode) VDC certificate update
     dellemc.objectscale.vdc_certificate:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
       private_key_content: "{{ lookup('file', 'server.key') }}"
       certificate_chain_content: "{{ lookup('file', 'server-chain.pem') }}"
     check_mode: true
     diff: true

Return Values
=============

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Key
     - Description
   * - ``changed``
     - Whether the certificate chain was updated. (bool)
   * - ``vdc_certificate_details``
     - Dictionary with certificate metadata including ``fingerprint``, ``chain_length``, and ``chain`` (array of per-cert metadata). (dict)
   * - ``diff``
     - Before/after fingerprint metadata. Returned only when diff mode is enabled and ``changed`` is true. Private key material is never included. (dict)

Notes
=====

- The ``cryptography`` Python package is optional but enables richer certificate metadata (subject, issuer, serial, expiry).
- Error codes follow the FC-220 through FC-239 range.
