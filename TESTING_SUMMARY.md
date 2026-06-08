# VDC Keystore Modules — Testing Summary

## Quick Start

### Option A: Run Quick Test Script (Fastest)
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale
./quick_test.sh
```

### Option B: Run Unit Tests
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate*.py -v
```

### Option C: Run Full Testing Guide
See `TESTING_GUIDE.md` for comprehensive testing procedures.

---

## Module Testing Matrix

### 1. `vdc_certificate_info` — VDC Certificate Query

**Type**: Info module (read-only)  
**Endpoint**: `GET /vdc/keystore`  
**Expected Behavior**: Always `changed=false`

| Test Case | Method | Command |
|-----------|--------|---------|
| Basic query | Ansible | `ansible-playbook playbooks/modules/vdc_certificate_info.yml` |
| Unit tests | Pytest | `pytest tests/unit/plugins/modules/test_vdc_certificate_info.py -v` |
| Check mode | Ansible | Add `check_mode: true` to playbook task |
| Error handling | Pytest | Tests for 401, 404, 500 errors included |

**Expected Output**:
```yaml
vdc_certificate_details:
  fingerprint: "abc123def456..."
  chain: "-----BEGIN CERTIFICATE-----\n..."
  chain_length: 3
  leaf_subject: "CN=objectscale.example.com"  # if cryptography installed
  not_after: "2027-01-01T00:00:00"            # if cryptography installed
changed: false
```

---

### 2. `vdc_certificate` — VDC Certificate Management

**Type**: State module (management)  
**Endpoint**: `PUT /vdc/keystore`  
**Expected Behavior**: Idempotent, supports check/diff mode

| Test Case | Method | Command |
|-----------|--------|---------|
| Update from file | Ansible | `ansible-playbook playbooks/modules/vdc_certificate.yml` |
| Update inline | Ansible | Pass `private_key_content` and `certificate_chain_content` |
| Idempotency | Ansible | Run twice, second should show `changed=false` |
| Check mode | Ansible | Add `check_mode: true` (no actual change) |
| Diff mode | Ansible | Add `diff: true` (shows fingerprint change) |
| Unit tests | Pytest | `pytest tests/unit/plugins/modules/test_vdc_certificate.py -v` |

**Expected Output (First Run)**:
```yaml
changed: true
vdc_certificate_details:
  fingerprint: "new_fingerprint_hash"
  chain_length: 3
```

**Expected Output (Second Run - Idempotent)**:
```yaml
changed: false
vdc_certificate_details:
  fingerprint: "new_fingerprint_hash"  # same as before
  chain_length: 3
```

---

### 3. `vdc_certificate_chain_info` — Object-cert Certificate Query

**Type**: Info module (read-only)  
**Endpoint**: `GET /object-cert/keystore`  
**Expected Behavior**: Always `changed=false`

| Test Case | Method | Command |
|-----------|--------|---------|
| Basic query | Ansible | `ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml` |
| Unit tests | Pytest | `pytest tests/unit/plugins/modules/test_vdc_certificate_chain_info.py -v` |
| Functional tests | Ansible | `ansible-playbook VDC_Certificate_Chain_Info/TC-01_get_certificate_chain_info.yml` |
| Check mode | Ansible | Add `check_mode: true` to playbook task |

**Expected Output**:
```yaml
vdc_certificate_chain_details:
  fingerprint: "xyz789abc123..."
  chain: "-----BEGIN CERTIFICATE-----\n..."
  chain_length: 2
  leaf_subject: "CN=s3.objectscale.example.com"  # if cryptography installed
  not_after: "2027-06-01T00:00:00"               # if cryptography installed
changed: false
```

---

### 4. `vdc_certificate_chain` — Object-cert Certificate Management

**Type**: State module (management)  
**Endpoint**: `PUT /object-cert/keystore`  
**Expected Behavior**: Idempotent, supports check/diff mode

| Test Case | Method | Command |
|-----------|--------|---------|
| Update from file | Ansible | `ansible-playbook playbooks/modules/vdc_certificate_chain.yml` |
| Update inline | Ansible | Pass `private_key_content` and `certificate_chain_content` |
| Idempotency | Ansible | Run twice, second should show `changed=false` |
| Check mode | Ansible | Add `check_mode: true` (no actual change) |
| Diff mode | Ansible | Add `diff: true` (shows fingerprint change) |
| Unit tests | Pytest | `pytest tests/unit/plugins/modules/test_vdc_certificate_chain.py -v` |
| Functional tests | Ansible | `ansible-playbook VDC_Certificate_Chain/TC-*.yml` |

**Expected Output (First Run)**:
```yaml
changed: true
vdc_certificate_chain_details:
  fingerprint: "new_chain_fingerprint"
  chain_length: 2
```

**Expected Output (Second Run - Idempotent)**:
```yaml
changed: false
vdc_certificate_chain_details:
  fingerprint: "new_chain_fingerprint"  # same as before
  chain_length: 2
```

---

## Testing Scenarios

### Scenario 1: Read Current Certificates (No Risk)

**Goal**: Query current certificates without making changes

```bash
# VDC Certificate
ansible-playbook -i localhost, -c local -e "objectscale_host=10.0.0.1" \
  playbooks/modules/vdc_certificate_info.yml

# Object-cert Certificate
ansible-playbook -i localhost, -c local -e "objectscale_host=10.0.0.1" \
  playbooks/modules/vdc_certificate_chain_info.yml
```

**Expected**: Both modules return certificate details with `changed=false`

---

### Scenario 2: Test Idempotency (Safe in Check Mode)

```bash
# Create test playbook
cat > test_idempotency.yml << 'EOF'
---
- name: Test Idempotency
  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    objectscale_host: "10.0.0.1"
    objectscale_username: "admin"
    objectscale_password: "password"

  tasks:
    - name: Get current VDC certificate
      dellemc.objectscale.vdc_certificate_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
      register: current_cert

    - name: Re-apply same certificate (check mode)
      dellemc.objectscale.vdc_certificate:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        state: present
        private_key_path: /path/to/current-key.pem
        certificate_chain_content: "{{ current_cert.vdc_certificate_details.chain }}"
      check_mode: true
      register: idempotent_result

    - name: Verify idempotency
      ansible.builtin.assert:
        that:
          - idempotent_result.changed == false
        fail_msg: "Idempotency test failed: expected changed=false"
EOF

ansible-playbook test_idempotency.yml
```

**Expected**: Second application shows `changed=false`

---

### Scenario 3: Test Error Handling (Negative Tests)

```bash
# Test with invalid credentials
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=invalid" \
  -e "objectscale_password=invalid" \
  playbooks/modules/vdc_certificate_info.yml

# Expected: Task fails with authentication error
```

---

### Scenario 4: Test Diff Mode (Security Check)

```bash
# Create diff test playbook
cat > test_diff_mode.yml << 'EOF'
---
- name: Test Diff Mode
  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    objectscale_host: "10.0.0.1"
    objectscale_username: "admin"
    objectscale_password: "password"

  tasks:
    - name: Update VDC certificate with diff mode
      dellemc.objectscale.vdc_certificate:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: false
        state: present
        private_key_path: /path/to/new-key.pem
        certificate_chain_path: /path/to/new-chain.pem
      diff: true
      check_mode: true
      register: diff_result

    - name: Verify private key not in diff
      ansible.builtin.assert:
        that:
          - "'PRIVATE KEY' not in (diff_result | string)"
        fail_msg: "SECURITY ISSUE: Private key leaked in diff!"
EOF

ansible-playbook test_diff_mode.yml
```

**Expected**: Diff shows fingerprint changes, **never shows private key content**

---

## Unit Test Coverage

### Test Files
- `test_vdc_certificate.py` — 88 tests
- `test_vdc_certificate_info.py` — Tests for info module
- `test_vdc_certificate_chain.py` — 36 tests for new chain module
- `test_vdc_certificate_chain_info.py` — Tests for new chain info module
- `test_vdc_keystore_api.py` — API wrapper tests
- `test_object_cert_keystore_api.py` — New API wrapper tests

### Run All Tests
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py -v --tb=short
```

### Coverage Report
```bash
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py \
  --cov=plugins/modules \
  --cov=plugins/module_utils \
  --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Functional Tests (QE Repo)

### VDC Certificate Chain Tests
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/ansible-objectscale-qe

# Pre-requisites
ansible-playbook VDC_Certificate_Chain/pre_req.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"

# Test cases
ansible-playbook VDC_Certificate_Chain/TC-01_set_certificate_chain_inline.yml
ansible-playbook VDC_Certificate_Chain/TC-02_idempotence_no_change.yml
ansible-playbook VDC_Certificate_Chain/TC-03_check_mode.yml
ansible-playbook VDC_Certificate_Chain/TC-04_diff_mode.yml
ansible-playbook VDC_Certificate_Chain/TC-05_missing_private_key_negative.yml
# ... etc for TC-06 through TC-10
```

### VDC Certificate Chain Info Tests
```bash
# Pre-requisites
ansible-playbook VDC_Certificate_Chain_Info/pre_req.yml

# Test cases
ansible-playbook VDC_Certificate_Chain_Info/TC-01_get_certificate_chain_info.yml
ansible-playbook VDC_Certificate_Chain_Info/TC-02_changed_always_false.yml
ansible-playbook VDC_Certificate_Chain_Info/TC-03_check_mode.yml
ansible-playbook VDC_Certificate_Chain_Info/TC-04_metadata_fields.yml
ansible-playbook VDC_Certificate_Chain_Info/TC-05_invalid_credentials_negative.yml
```

---

## Troubleshooting

### Issue: "Module not found"
```bash
# Verify collection is installed
ansible-galaxy collection list | grep objectscale

# If not found, install it
ansible-galaxy collection install /path/to/objectscale/collection
```

### Issue: "Connection refused"
```bash
# Verify ObjectScale is running
curl -k https://10.0.0.1:4443/api/v1/vdc/info

# Check firewall
telnet 10.0.0.1 4443
```

### Issue: "Authentication failed"
```bash
# Verify credentials
curl -k -u admin:password https://10.0.0.1:4443/api/v1/vdc/info
```

### Issue: "cryptography not installed"
```bash
pip install cryptography
```

---

## Success Criteria

✅ **All tests pass**:
- [ ] Unit tests: 158/158 passing
- [ ] Info modules return certificate details
- [ ] State modules support idempotency
- [ ] Check mode works without making changes
- [ ] Diff mode shows changes without leaking private keys
- [ ] Error handling works correctly
- [ ] Functional tests pass on real ObjectScale instance

---

## Next Steps

1. **Prepare test environment**:
   - Ensure ObjectScale cluster is accessible
   - Have admin credentials ready
   - Generate test certificates if needed

2. **Run quick test**:
   ```bash
   ./quick_test.sh
   ```

3. **Run comprehensive tests**:
   - Follow TESTING_GUIDE.md
   - Run all unit tests
   - Run functional tests from QE repo

4. **Verify in GUI**:
   - Access ObjectScale management UI
   - Compare module output with GUI display
   - Verify fingerprints and expiry dates match

5. **Document results**:
   - Save test output
   - Note any issues or deviations
   - Update JIRA with test results
