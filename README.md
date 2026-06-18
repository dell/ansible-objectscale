# Ansible Modules for Dell Technologies ObjectScale

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](https://github.com/dell/ansible-objectscale/blob/main/docs/CODE_OF_CONDUCT.md)
[![License](https://img.shields.io/github/license/dell/ansible-objectscale)](https://github.com/dell/ansible-objectscale/blob/main/LICENSE)
[![Python version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Ansible version](https://img.shields.io/badge/ansible-2.15+-blue.svg)](https://pypi.org/project/ansible/)
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/dell/ansible-objectscale?include_prereleases&label=latest&style=flat-square)](https://github.com/dell/ansible-objectscale/releases)

The Ansible Modules for Dell Technologies (Dell) ObjectScale allow Data Center and IT administrators to use RedHat Ansible to automate and orchestrate the provisioning and management of Dell ObjectScale storage systems.

The capabilities of the Ansible modules include managing namespaces, buckets, replication groups, storage pools, IAM users, IAM groups, IAM roles, IAM policies, IAM identity providers, VDC certificates, and to gather high level facts from the storage system. The options available are list, show, create, modify and delete. These tasks can be executed by running simple playbooks written in yaml syntax. The modules are written so that all the operations are idempotent, so making multiple identical requests has the same effect as making a single request.

## Table of contents

* [Code of conduct](https://github.com/dell/ansible-objectscale/blob/main/docs/CODE_OF_CONDUCT.md)
* [Contributing guide](https://github.com/dell/ansible-objectscale/blob/main/docs/CONTRIBUTING.md)
* [Support](#support)
* [License](#license)
* [Security](https://github.com/dell/ansible-objectscale/blob/main/docs/SECURITY.md)
* [List of Ansible modules for Dell ObjectScale](#list-of-ansible-modules-for-dell-objectscale)
* [Installation and execution of Ansible modules for Dell ObjectScale](#installation-and-execution-of-ansible-modules-for-dell-objectscale)
* [Releasing, Maintenance and Deprecation](#releasing-maintenance-and-deprecation)

## Requirements

| **Ansible Modules** | **ObjectScale Version** | **Python version** | **Ansible**              |
|---------------------|-----------------------|--------------------|--------------------------|
| v1.0.0 | 4.3 | 3.13.x <br> 3.14.x | 2.19 <br> 2.20 |

* Please follow ObjectScale installation instructions on [Dell ObjectScale Documentation](https://www.dell.com/en-us/dt/objectscale/index.htm)

## Installation and execution of Ansible modules for Dell ObjectScale

The installation and execution steps of Ansible modules for Dell ObjectScale can be found [here](https://github.com/dell/ansible-objectscale/blob/main/docs/INSTALLATION.md).

## Use Cases

Refer the [example playbooks](https://github.com/dell/ansible-objectscale/tree/main/playbooks) on how the collection can be used for [modules](https://github.com/dell/ansible-objectscale/tree/main/playbooks/modules).

## Testing

The following tests are done on ansible-objectscale collection:
- Unit tests
- Integration tests

## Release Notes, Maintenance and Deprecation

Ansible Modules for Dell Technologies ObjectScale follows [Semantic Versioning](https://semver.org/).

New version will be released regularly if significant changes (bug fix or new feature) are made in the collection.

Released code versions are located on "release" branches with names of the form "release-x.y.z" where x.y.z corresponds to the version number.

Ansible Modules for Dell Technologies ObjectScale deprecation cycle is aligned with that of [Ansible](https://docs.ansible.com/projects/ansible/latest/reference_appendices/release_and_maintenance.html).

See [change logs](https://github.com/dell/ansible-objectscale/blob/main/CHANGELOG.rst) for more information on what is new in the releases.

## Related Information

### Idempotency

The modules are written in such a way that all requests are idempotent and hence fault-tolerant. It essentially means that the result of a successfully performed request is independent of the number of times it is executed.

### List of Ansible modules for Dell ObjectScale

#### Namespace Management
* [Namespace module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/namespace_module.rst)
* [Namespace Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/namespace_info_module.rst)

#### Bucket Management
* [Bucket module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/bucket.rst)
* [Bucket Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/bucket_info.rst)

#### Replication and Storage
* [Replication Group module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/replication_group_module.rst)
* [Replication Group Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/replication_group_info.rst)
* [Storage Pool Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/storage_pool_info.rst)

#### IAM User Management
* [IAM User module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user_module.rst)
* [IAM User Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user_info_module.rst)
* [IAM User Access Key module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user_access_key_module.rst)
* [IAM User Access Key Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user_access_key_info_module.rst)

#### IAM Group Management
* [IAM Group module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_group_module.rst)
* [IAM Group Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_group_info_module.rst)

#### IAM Role and Policy Management
* [IAM Role module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_role.rst)
* [IAM Role Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_role_info.rst)
* [IAM Policy module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy.rst)
* [IAM Policy Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy_info.rst)
* [IAM Policy Attachment module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy_attachment.rst)
* [IAM Policy Attachment Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy_attachment_info.rst)
* [IAM Inline Policy module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_inline_policy.rst)
* [IAM Inline Policy Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_inline_policy_info.rst)

#### IAM Identity Provider Management
* [IAM Identity Provider module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_identity_provider_module.rst)
* [IAM Identity Provider Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_identity_provider_info_module.rst)

#### Object User Management
* [Object User module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/object_user.rst)
* [Object User Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/object_user_info.rst)

#### Management User Management
* [Management User module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/management_user.rst)
* [Management User Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/management_user_info.rst)

#### VDC Certificate Management
* [VDC Certificate module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/vdc_certificate.rst)
* [VDC Certificate Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/vdc_certificate_info.rst)
* [VDC Certificate Chain module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/vdc_certificate_chain.rst)
* [VDC Certificate Chain Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/vdc_certificate_chain_info.rst)

#### VDC Information
* [VDC Info module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/vdc_info_module.rst)

## Support

The support is available through [GitHub Issues](https://github.com/dell/ansible-objectscale/issues) or at [Dell Community forum](https://www.dell.com/community/Automation/bd-p/Automation).

As Red Hat Ansible Certified Content, this collection is entitled to support through the Ansible Automation Platform (AAP) using the **Create issue** button on the top right corner. If a support case cannot be opened with Red Hat, and the collection was obtained from Ansible Galaxy or GitHub, you can seek community support through the [Ansible Forum](https://forum.ansible.com/).

## License

The Ansible collection for ObjectScale is released and licensed under the GPL-3.0-or-later license. See [LICENSE](https://github.com/dell/ansible-objectscale/blob/main/LICENSE) for the full terms.
