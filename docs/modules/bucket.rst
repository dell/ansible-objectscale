.. _dellemc.objectscale.bucket:

********************************
dellemc.objectscale.bucket
********************************

**Manage ObjectScale buckets**

.. contents::
   :local:
   :depth: 2

Synopsis
========

- Manages the lifecycle of ObjectScale buckets, including creation, deletion, and configuration.

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
   * - ``name``
     - The name of the bucket. (Required)
   * - ``namespace``
     - The ObjectScale namespace where the bucket resides. (Required)
   * - ``state``
     - The desired state of the bucket. (Required, choices: [present, absent])
   * - ``versioning``
     - Enable or disable object versioning on the bucket. (bool)
   * - ``force``
     - Force delete a non-empty bucket. (bool, default: false)

Examples
========

.. code-block:: yaml

   - name: Create a bucket
     dellemc.objectscale.bucket:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
       namespace: "my-namespace"
       name: "my-new-bucket"
       state: present
       versioning: true

   - name: Delete a bucket
     dellemc.objectscale.bucket:
       objectscale_host: "{{ os_host }}"
       objectscale_username: "{{ os_user }}"
       objectscale_password: "{{ os_pass }}"
       validate_certs: false
       namespace: "my-namespace"
       name: "my-new-bucket"
       state: absent

Return Values
=============

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Key
     - Description
   * - ``changed``
     - Whether or not the resource has changed. (bool)
