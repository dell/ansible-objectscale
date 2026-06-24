# Changelog

## [1.0.0] - 2026-06-22

### Added
- Initial release of Dell ObjectScale Ansible Collection
- Comprehensive module set for ObjectScale management
- Bucket Management modules for object storage operations
- Identity & Access Management modules for IAM operations
- Namespace Management modules for namespace operations
- Replication modules for replication group management
- Storage Pool Management modules for storage pool operations
- VDC Management modules for Virtual Data Center operations
- VDC Certificate Management modules for certificate lifecycle
- Management User and Object User modules

### Features
- **Bucket Management**: Create, modify, delete, and get information about buckets
- **IAM Management**: Full IAM support including users, groups, roles, policies, access keys, inline policies, identity providers, and policy attachments
- **Namespace Management**: Create, modify, delete, and get information about namespaces
- **Replication**: Manage replication groups for disaster recovery
- **Storage Pool Management**: Manage storage pools and retrieve storage pool information
- **VDC Management**: Query VDC details, manage VDC certificates and certificate chains
- **User Management**: Manage management users and object users
- **Info Modules**: Comprehensive information gathering for all resources
- **Standardized Structure**: Follows Dell Ansible collection patterns
- **Idempotency**: All modules support idempotent operations

### Module Details
- `dellemc.objectscale.bucket` - Manage ObjectScale buckets
- `dellemc.objectscale.bucket_info` - Get bucket information
- `dellemc.objectscale.iam_group` - Manage IAM groups
- `dellemc.objectscale.iam_group_info` - Get IAM group information
- `dellemc.objectscale.iam_identity_provider` - Manage IAM SAML identity providers
- `dellemc.objectscale.iam_identity_provider_info` - Get IAM identity provider information
- `dellemc.objectscale.iam_inline_policy` - Manage IAM inline policies
- `dellemc.objectscale.iam_inline_policy_info` - Get IAM inline policy information
- `dellemc.objectscale.iam_policy` - Manage IAM policies
- `dellemc.objectscale.iam_policy_info` - Get IAM policy information
- `dellemc.objectscale.iam_policy_attachment` - Manage IAM policy attachments
- `dellemc.objectscale.iam_policy_attachment_info` - Get IAM policy attachment information
- `dellemc.objectscale.iam_role` - Manage IAM roles
- `dellemc.objectscale.iam_role_info` - Get IAM role information
- `dellemc.objectscale.iam_user` - Manage IAM users
- `dellemc.objectscale.iam_user_info` - Get IAM user information
- `dellemc.objectscale.iam_user_access_key` - Manage IAM user access keys
- `dellemc.objectscale.iam_user_access_key_info` - Get IAM user access key information
- `dellemc.objectscale.management_user` - Manage management users
- `dellemc.objectscale.management_user_info` - Get management user information
- `dellemc.objectscale.namespace` - Manage namespaces
- `dellemc.objectscale.namespace_info` - Get namespace information
- `dellemc.objectscale.object_user` - Manage object users
- `dellemc.objectscale.object_user_info` - Get object user information
- `dellemc.objectscale.replication_group` - Manage replication groups
- `dellemc.objectscale.replication_group_info` - Get replication group information
- `dellemc.objectscale.storage_pool` - Manage storage pools
- `dellemc.objectscale.storage_pool_info` - Get storage pool information
- `dellemc.objectscale.vdc_certificate` - Manage VDC certificates
- `dellemc.objectscale.vdc_certificate_chain` - Manage VDC certificate chains
- `dellemc.objectscale.vdc_certificate_info` - Get VDC certificate information
- `dellemc.objectscale.vdc_certificate_chain_info` - Get VDC certificate chain information
- `dellemc.objectscale.vdc_info` - Get VDC information

### Dependencies
- Python >= 3.11
- objectscale-sdk >= 1.0.0
- Ansible >= 2.17
- urllib3 >= 2.6.3
- packaging

### Documentation
- Comprehensive README with installation and usage instructions
- Module documentation with examples
- Categorized module listing by functionality

### License
- GPL-3.0-or-later

### Support
- Dell Community forums
- GitHub Issues
