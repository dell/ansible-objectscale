# Ansible Modules for Dell Technologies ObjectScale

The Ansible Modules for Dell Technologies ObjectScale allow Data Center and IT administrators to use RedHat Ansible to automate and orchestrate the configuration and management of Dell ObjectScale storage arrays.

The capabilities of the Ansible modules are managing buckets, IAM users, IAM groups, IAM policies, IAM roles, IAM user access keys, namespaces, and replication groups. It also allows gathering high-level info from the array. The options available for each are list, show, create, modify and delete. These tasks can be executed by running simple playbooks written in yaml syntax. The modules are written so that all the operations are idempotent, so making multiple identical requests has the same effect as making a single request.

## License
Ansible collection for ObjectScale is released and licensed under the GPL-3.0 license. See [LICENSE](https://github.com/dell/ansible-objectscale/blob/main/LICENSE) for the full terms.

## Support

The support is available through [GitHub Issues](https://github.com/dell/ansible-objectscale/issues) or at [Dell Community forum](https://www.dell.com/community/Automation/bd-p/Automation).

As Red Hat Ansible Certified Content, this collection is entitled to support through the Ansible Automation Platform (AAP) using the **Create issue** button on the top right corner. If a support case cannot be opened with Red Hat, and the collection was obtained from Ansible Galaxy or GitHub, you can seek community support through the [Ansible Forum](https://forum.ansible.com/).

## Prerequisites
This table provides information about the software prerequisites for the Ansible Modules for Dell ObjectScale.

|| **Ansible Modules** | **ObjectScale Version** | **Python version** | **Python SDK version** | **Ansible**              |
||---------------------|-----------------------|--------------------|----------------------------|--------------------------|
|| v1.0.0 | 1.0.x | 3.11.x <br> 3.12.x <br> 3.13 | 1.0.0 | 2.17 <br> 2.18 <br> 2.19 |

  * Please follow objectscale-sdk installation instructions on [ObjectScale Documentation](https://github.com/dell/python-objectscale)

## Idempotency
The modules are written in such a way that all requests are idempotent and hence fault-tolerant. It essentially means that the result of a successfully performed request is independent of the number of times it is executed.

## List of Ansible Modules for Dell ObjectScale

### Bucket Management
* [Bucket Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/bucket.rst)
* [Bucket Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/bucket_info.rst)

### Identity & Access Management
* [IAM User Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user.rst)
* [IAM User Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user_info.rst)
* [IAM User Access Key Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user_access_key.rst)
* [IAM User Access Key Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_user_access_key_info.rst)
* [IAM Group Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_group.rst)
* [IAM Group Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_group_info.rst)
* [IAM Role Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_role.rst)
* [IAM Role Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_role_info.rst)
* [IAM Policy Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy.rst)
* [IAM Policy Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy_info.rst)
* [IAM Policy Attachment Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy_attachment.rst)
* [IAM Policy Attachment Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/iam_policy_attachment_info.rst)

### Namespace Management
* [Namespace Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/namespace.rst)
* [Namespace Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/namespace_info.rst)

### Replication
* [Replication Group Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/replication_group.rst)
* [Replication Group Info Module](https://github.com/dell/ansible-objectscale/blob/main/docs/modules/replication_group_info.rst)

## Installation of SDK
Install python sdk named 'objectscale-sdk'. It can be installed using pip, based on appropriate python version.

    pip install objectscale-sdk

## Installing Collections

#### Online Installation of Collections
  * Use the following command to install the latest collection hosted in [galaxy portal](https://galaxy.ansible.com/dellemc/objectscale):

        ansible-galaxy collection install dellemc.objectscale -p <install_path>

#### Offline Installation of Collections

  * Download the latest tar build from any of the available distribution channel [Ansible Galaxy](https://galaxy.ansible.com/dellemc/objectscale) /[Automation Hub](https://console.redhat.com/ansible/automation-hub/repo/published/dellemc/objectscale) and use the following command to install the collection anywhere in your system:

        ansible-galaxy collection install dellemc-objectscale-1.0.0.tar.gz -p <install_path>

  * Set the environment variable:

        export ANSIBLE_COLLECTIONS_PATHS=$ANSIBLE_COLLECTIONS_PATHS:<install_path>

## Using Collections

  * In order to use any Ansible module, ensure that the importing of proper FQCN(Fully Qualified Collection Name) must be embedded in the playbook.
   Below example can be referred

        collections:
        - dellemc.objectscale

  * In order to use installed collection in a specific task use a proper FQCN(Fully Qualified Collection Name). Refer to the following example:

        tasks:
        - name: Get Bucket details
          dellemc.objectscale.dellemc_objectscale_bucket

  * For generating Ansible documentation for a specific module, embed the FQCN  before the module name. Refer to the following example:

        ansible-doc dellemc.objectscale.dellemc_objectscale_bucket

## Running Ansible Modules
The Ansible server must be configured with Python library for ObjectScale to run the Ansible playbooks. The [Documents](https://github.com/dell/ansible-objectscale/blob/main/docs/INSTALLATION.md) provide information on different Ansible modules along with their functions and syntax. The parameters table in the Product Guide provides information on various parameters which needs to be configured before running the modules.

## SSL Certificate Validation

* Copy the CA certificate to the "/etc/pki/ca-trust/source/anchors" path of the host by any external means.
* Set the "REQUESTS_CA_BUNDLE" environment variable to the path of the SSL certificate using the command:

        export REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/<<Certificate_Name>>
* Import the SSL certificate to host using the command:

        update-ca-trust extract
* If "TLS CA certificate bundle error" occurs, then follow below steps:
    * cd /etc/pki/tls/certs/
    * openssl x509 -in ca-bundle.crt -text -noout

## Results
Each module returns the updated state and details of the entity.
For example, if you are using the bucket module, all calls will return the updated details of the bucket.
Sample result is shown in each module's documentation.
