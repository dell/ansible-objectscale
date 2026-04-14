# Integration Tests for ansible-objectscale

## Directory Layout

```
tests/integration/
├── README.md                    # This file
├── run_tests.yaml               # Main playbook entry point
├── inventory.networking         # Inventory with ObjectScale connection details
├── network-integration.cfg      # Ansible configuration for integration tests
└── targets/
    └── iam_user/                # IAM User integration test role
        ├── defaults/main.yaml   # Default variables (testcase pattern)
        ├── meta/main.yaml       # Role metadata
        ├── tasks/main.yaml      # Test case discovery and execution
        ├── vars/main.yaml       # Test-specific variables
        └── tests/               # Individual test files
            ├── _helper_cleanup.yaml       # Reusable cleanup helper
            ├── _helper_create_user.yaml   # Reusable user creation helper
            ├── absent.yaml                # TC-05 – TC-08: Deletion tests
            ├── access_keys.yaml           # TC-19 – TC-23: Access key tests
            ├── create.yaml                # TC-01 – TC-04: Creation tests
            ├── invalid.yaml               # TC-09 – TC-10: Negative tests
            ├── modify_groups.yaml         # TC-17 – TC-18: Group membership tests
            ├── modify_policies.yaml       # TC-15 – TC-16: Policy management tests
            └── modify_tags.yaml           # TC-11 – TC-14: Tag management tests
```

## Running Tests

### Full Suite
```bash
cd tests/integration
ansible-playbook run_tests.yaml -i inventory.networking -v
```

### Single Test File
```bash
cd tests/integration
ansible-playbook run_tests.yaml -i inventory.networking -v \
  -e '{"testcase": "create"}'
```

### Prerequisites

1. A running ObjectScale cluster accessible at the host/port in `inventory.networking`
2. The `objectscale_client` Python package installed (`make build_client && make install_client`)
3. The `dellemc.objectscale` collection installed or available in the Ansible collection path
4. The managed policy `urn:ecs:iam:::policy/ECSS3ReadOnlyAccess` must exist on the system

## Test Pattern

Every test case follows the **four-phase** pattern:

1. **Check mode** (changes expected) — verifies `changed=true` without modifying state
2. **Normal mode** (apply) — applies the change, asserts `changed=true` + validates return data
3. **Check mode** (no changes expected) — verifies `changed=false` after the change is applied
4. **Idempotence** (re-apply) — re-runs the same task, asserts `changed=false`

All tests use `block/always` to guarantee cleanup regardless of test pass/fail.

## Test Cases

| ID    | File               | Description                             |
|-------|--------------------|-----------------------------------------|
| TC-01 | create.yaml        | Create basic user (4-phase)             |
| TC-02 | create.yaml        | Create user with tags (4-phase)         |
| TC-03 | create.yaml        | Create user with tags + boundary        |
| TC-04 | create.yaml        | Create user with diff mode              |
| TC-05 | absent.yaml        | Delete existing user (4-phase)          |
| TC-06 | absent.yaml        | Delete non-existent user (no-op)        |
| TC-07 | absent.yaml        | Force delete user with access key       |
| TC-08 | absent.yaml        | Delete with diff mode                   |
| TC-09 | invalid.yaml       | Missing required user_name              |
| TC-10 | invalid.yaml       | Invalid namespace                       |
| TC-11 | modify_tags.yaml   | Add tags to existing user (4-phase)     |
| TC-12 | modify_tags.yaml   | Update tag value (4-phase)              |
| TC-13 | modify_tags.yaml   | Purge extra tags (purge_tags=true)      |
| TC-14 | modify_tags.yaml   | Keep extra tags (purge_tags=false)      |
| TC-15 | modify_policies.yaml | Attach managed policy (4-phase)       |
| TC-16 | modify_policies.yaml | Purge managed policies                |
| TC-17 | modify_groups.yaml | Add user to group (4-phase)             |
| TC-18 | modify_groups.yaml | Verify with iam_user_info include_groups|
| TC-19 | access_keys.yaml   | Create access key                       |
| TC-20 | access_keys.yaml   | Deactivate access key (4-phase)         |
| TC-21 | access_keys.yaml   | Idempotent key status                   |
| TC-22 | access_keys.yaml   | Delete access key                       |
| TC-23 | access_keys.yaml   | Verify via iam_user_info include_access_keys |
