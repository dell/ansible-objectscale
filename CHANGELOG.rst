# Changelog

## [Unreleased]

### Added
- `vdc_info` module for querying VDC (Virtual Data Center) details from ObjectScale.
  Supports listing all VDCs in a single site or multi-site federation, querying
  a specific VDC by name or by ID, and retrieving local VDC details.
  The `secretKeys` field is always omitted from output to prevent credential exposure.

## [1.0.0] - 2024-03-26

### Added
- Initial release of Dell ObjectScale Ansible Collection
- Basic collection structure based on PowerScale collection
- Integrated OpenAPI-generated SDK support
- `info` module for gathering ObjectScale system information
- Comprehensive documentation and examples
- Unit test framework setup
- Logging infrastructure
- Module utilities for common operations

### Features
- **Integrated OpenAPI Library**: Uses custom objectscale-sdk for API interactions
- **Standardized Structure**: Follows Dell Ansible collection patterns
- **Comprehensive Documentation**: Detailed README, module docs, and examples
- **Testing Framework**: Unit tests and integration test structure
- **Logging Support**: Custom logging handlers for debugging
- **Error Handling**: Standardized error handling and validation

### Module Details
- `dellemc.objectscale.info` - Gather system information including version, capacity, and node status

### Dependencies
- Python >= 3.6
- objectscale-sdk >= 1.0.0
- Ansible >= 2.15.0
- urllib3 >= 2.6.3
- packaging

### Documentation
- Complete README with installation and usage instructions
- Module documentation with examples
- Development setup guide
- Testing instructions

### License
- GPL-3.0-or-later

### Support
- Dell Community forums
- GitHub Issues
