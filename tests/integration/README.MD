# Dell ObjectScale Ansible Collection - Functional Integration Tests

## Overview

This directory contains functional integration tests for the `dellemc.objectscale` Ansible collection.
Tests follow the `ansible-test network-integration` role-based pattern and are designed to run
against a live Dell ObjectScale environment.

## Prerequisites

- Ansible >= 2.17
- Python >= 3.11
- A running Dell ObjectScale instance with IAM enabled
- Valid credentials with admin privileges on the target namespace
- The `objectscale_client` Python package installed (`make install_client`)

## Configuration

1. **Edit the inventory file** `inventory.networking` with your ObjectScale environment details:

   ```ini
   [objectscale:vars]
   objectscale_host=<your-objectscale-host>
   objectscale_username=<admin-user>
   objectscale_password=<admin-password>
   objectscale_port=4443
   validate_certs=false
   objectscale_namespace=<your-namespace>
   ```

2. **Ensure the following IAM users exist** in the target namespace (for user-management tests):
   - `test-user-1`
   - `test-user-2`

3. **Ensure the following managed IAM policy exists** (or adjust `vars/main.yaml`):
   - `urn:ecs:iam:::policy/ECSS3ReadOnlyAccess`

## Running Tests

### Run all tests for the `iam_group` target

```bash
ansible-test network-integration iam_group --requirements
```

### Run a specific test case (e.g., only the create tests)

```bash
ansible-test network-integration iam_group -e testcase='create'
```

### Run with verbose output

```bash
ansible-test network-integration iam_group -vvvvvv --truncate 0
```

### Run with coverage

```bash
ansible-test network-integration iam_group --coverage
```

## Test Targets

| Target      | Description                                          |
| ----------- | ---------------------------------------------------- |
| `iam_group` | CRUD operations for IAM group management module      |

## Test Structure

Each target follows the standard Ansible integration test role structure:

```
targets/<target_name>/
  defaults/main.yaml          # Default variables (testcase pattern)
  vars/main.yaml              # Target-specific test variables
  meta/main.yaml              # Role dependencies
  tasks/main.yaml             # Dynamic test case discovery & runner
  tests/
    create.yaml               # Group creation tests
    modify_users.yaml          # User membership management tests
    modify_policies.yaml       # Managed policy management tests
    modify_inline_policies.yaml # Inline policy management tests
    absent.yaml                # Group deletion tests
    invalid.yaml               # Negative / error case tests
    _helper_cleanup.yaml       # Shared cleanup helper
    _helper_create_group.yaml  # Shared group creation helper
```

### Test Patterns

Every test file follows the **four-phase test pattern**:

1. **Check Mode (changes expected)** - Dry-run with `check_mode: true`
2. **Normal Mode** - Apply the change
3. **Check Mode (no changes expected)** - Dry-run again to verify idempotency
4. **Idempotence Mode** - Re-apply to confirm `changed: false`

All tests use `block/always` for guaranteed cleanup regardless of pass/fail.
