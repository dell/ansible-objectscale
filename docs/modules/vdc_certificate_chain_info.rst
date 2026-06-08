.. _dellemc.objectscale.vdc_certificate_chain_info:

**********************************************
dellemc.objectscale.vdc_certificate_chain_info
**********************************************

**Retrieve Object-cert keystore certificate chain details from Dell ObjectScale**

.. contents::
   :local:
   :depth: 2

Synopsis
========

- Queries the current Object-cert (S3/object) keystore certificate chain via ``GET /object-cert/keystore``.
- Parses and returns certificate metadata including fingerprint, chain length, and per-certificate details.
- Always returns ``changed: false`` (read-only operation).
- Supports Ansible check mode.
- This module queries the Object-cert keystore, which is distinct from the VDC management keystore queried by ``dellemc.objectscale.vdc_certificate_info``.

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

Examples
========

.. code-block:: yaml

   - name: Retrieve current Object-cert certificate details
     dellemc.objectscale.vdc_certificate_chain_info:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
     register: chain_info

   - name: Display certificate fingerprint
     ansible.builtin.debug:
       var: chain_info.vdc_certificate_chain_details.fingerprint

Return Values
=============

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Key
     - Description
   * - ``changed``
     - Always ``false``. (bool)
   * - ``vdc_certificate_chain_details``
     - Dictionary with certificate metadata. (dict)
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

Notes
=====

- Requires the ``objectscale_client`` Python package.
- The ``cryptography`` Python package is optional but enables richer certificate metadata (subject, issuer, serial, expiry).
