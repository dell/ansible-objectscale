.. _dellemc.objectscale.vdc_certificate_info:

**********************************************
dellemc.objectscale.vdc_certificate_info
**********************************************

**Retrieve VDC keystore certificate chain details from Dell ObjectScale**

.. contents::
   :local:
   :depth: 2

Synopsis
========

- Queries the current VDC-level TLS certificate chain via the ``GET /vdc/keystore`` API.
- Parses and returns certificate metadata including fingerprint, chain length, and per-certificate details.
- Always returns ``changed: false`` (read-only operation).
- Supports Ansible check mode.

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

   - name: Retrieve current VDC certificate details
     dellemc.objectscale.vdc_certificate_info:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
     register: cert_info

   - name: Display certificate fingerprint
     ansible.builtin.debug:
       var: cert_info.vdc_certificate_details.fingerprint

Return Values
=============

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Key
     - Description
   * - ``changed``
     - Always ``false``. (bool)
   * - ``vdc_certificate_details``
     - Dictionary with certificate metadata. (dict)
   * - ``vdc_certificate_details.fingerprint``
     - SHA-256 fingerprint of the normalised certificate chain. (str)
   * - ``vdc_certificate_details.chain``
     - List of per-certificate metadata objects. With the ``cryptography`` package, each entry contains ``subject``, ``issuer``, ``serial_number``, ``not_before``, and ``not_after``. (list)
   * - ``vdc_certificate_details.chain_length``
     - Count of certificates in the chain. (int)

Notes
=====

- Requires the ``objectscale_client`` Python package.
- The ``cryptography`` Python package is optional but enables richer certificate metadata (subject, issuer, serial, expiry).
