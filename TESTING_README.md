# VDC Keystore Modules — Testing Documentation

Complete testing guide for the four VDC Keystore modules:
- `vdc_certificate` — VDC TLS certificate management
- `vdc_certificate_info` — VDC TLS certificate query
- `vdc_certificate_chain` — Object-cert TLS certificate management
- `vdc_certificate_chain_info` — Object-cert TLS certificate query

---

## 📚 Documentation Files

| Document | Purpose | Audience |
|----------|---------|----------|
| **TESTING_SUMMARY.md** | Quick reference for all testing methods | Everyone |
| **TESTING_GUIDE.md** | Comprehensive testing procedures | QA/Developers |
| **GUI_TESTING_GUIDE.md** | ObjectScale UI verification steps | Operators/QA |
| **quick_test.sh** | Automated quick test script | DevOps/Automation |

---

## 🚀 Quick Start (5 minutes)

### Option 1: Run Quick Test Script
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale
./quick_test.sh
```

### Option 2: Run Unit Tests
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate*.py -v
```

### Option 3: Run Info Modules
```bash
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"

ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

---

## 📋 Testing Methods

### Method 1: CLI with Ansible Playbooks ⭐ Recommended
**Best for**: Testing against real ObjectScale instance

```bash
# Query current certificates (safe, read-only)
ansible-playbook playbooks/modules/vdc_certificate_info.yml
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml

# Test update in check mode (safe, no actual change)
ansible-playbook playbooks/modules/vdc_certificate.yml --check
ansible-playbook playbooks/modules/vdc_certificate_chain.yml --check
```

**Advantages**:
- Tests against real ObjectScale instance
- Verifies actual API integration
- Can be run in check mode (safe)
- Easy to automate

**See**: TESTING_GUIDE.md → Method 1

---

### Method 2: Unit Tests with Pytest
**Best for**: Code quality and regression testing

```bash
# Run all VDC Keystore tests
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py -v

# Run specific module tests
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_chain.py -v
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_chain_info.py -v

# Run with coverage report
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py \
  --cov=plugins/modules \
  --cov=plugins/module_utils \
  --cov-report=html
```

**Test Coverage**:
- 158 total tests (all passing)
- 70 new tests for chain modules
- 91-92% coverage on new code
- Tests for idempotency, check/diff mode, error handling, security

**See**: TESTING_GUIDE.md → Method 4

---

### Method 3: Direct Python Testing
**Best for**: Debugging and API integration testing

```bash
# Create test script (see TESTING_GUIDE.md for full code)
python3 test_modules_direct.py
```

**Advantages**:
- Direct API testing
- No Ansible overhead
- Good for debugging

**See**: TESTING_GUIDE.md → Method 2

---

### Method 4: ObjectScale GUI Verification
**Best for**: Operator validation and visual confirmation

1. Open ObjectScale management UI: `https://<ip>:4443`
2. Navigate to Settings → Certificates
3. Compare module output with GUI display
4. Verify fingerprints, expiry dates, chain lengths match

**Advantages**:
- Visual confirmation
- Operator-friendly
- Validates end-to-end functionality

**See**: GUI_TESTING_GUIDE.md

---

### Method 5: Functional Tests (QE Repo)
**Best for**: Integration testing and QA validation

```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/ansible-objectscale-qe

# VDC Certificate Chain tests (10 test cases)
ansible-playbook VDC_Certificate_Chain/TC-01_set_certificate_chain_inline.yml
ansible-playbook VDC_Certificate_Chain/TC-02_idempotence_no_change.yml
ansible-playbook VDC_Certificate_Chain/TC-03_check_mode.yml
# ... etc

# VDC Certificate Chain Info tests (5 test cases)
ansible-playbook VDC_Certificate_Chain_Info/TC-01_get_certificate_chain_info.yml
ansible-playbook VDC_Certificate_Chain_Info/TC-02_changed_always_false.yml
# ... etc
```

**Test Coverage**:
- 10 tests for vdc_certificate_chain
- 5 tests for vdc_certificate_chain_info
- Covers: basic operations, idempotency, check/diff mode, error handling

**See**: TESTING_SUMMARY.md → Functional Tests

---

## 🎯 Testing Scenarios

### Scenario 1: Query Current Certificates (Safe)
```bash
# No changes, read-only operations
ansible-playbook playbooks/modules/vdc_certificate_info.yml
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml
```
**Expected**: Both return certificate details with `changed=false`

---

### Scenario 2: Test Idempotency (Safe in Check Mode)
```bash
# Run twice, second should show no change
ansible-playbook playbooks/modules/vdc_certificate.yml --check
ansible-playbook playbooks/modules/vdc_certificate.yml --check
```
**Expected**: Both runs show `changed=false` (idempotent)

---

### Scenario 3: Test Check Mode (Safe, No Changes)
```bash
# Predict changes without making them
ansible-playbook playbooks/modules/vdc_certificate.yml --check
```
**Expected**: Shows what would change, but doesn't actually change anything

---

### Scenario 4: Test Diff Mode (Security Check)
```bash
# Show before/after without exposing private keys
ansible-playbook playbooks/modules/vdc_certificate.yml --diff --check
```
**Expected**: Shows fingerprint changes, **never shows private key content**

---

### Scenario 5: Update Certificate (Requires Real Cert)
```bash
# Prepare test certificate
openssl req -x509 -newkey rsa:2048 -keyout test-key.pem -out test-cert.pem -days 365 -nodes

# Update in check mode first
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "private_key_path=test-key.pem" \
  -e "certificate_chain_path=test-cert.pem" \
  --check

# Then actually update
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "private_key_path=test-key.pem" \
  -e "certificate_chain_path=test-cert.pem"
```
**Expected**: First run shows `changed=true`, second run shows `changed=false`

---

## ✅ Success Criteria

### Unit Tests
- [ ] All 158 tests pass
- [ ] Coverage ≥ 90% on new code
- [ ] No test failures or errors

### Functional Tests
- [ ] All 15 functional tests pass
- [ ] Info modules return correct data
- [ ] State modules support idempotency
- [ ] Check/diff modes work correctly

### Integration Tests
- [ ] Module output matches ObjectScale GUI
- [ ] Fingerprints match exactly
- [ ] Expiry dates match
- [ ] Chain lengths match

### Security Tests
- [ ] Private key never logged
- [ ] Private key never in diff output
- [ ] Credentials handled securely
- [ ] Error messages don't leak secrets

---

## 🔧 Environment Setup

### Prerequisites
```bash
# Install Python dependencies
pip install pydantic urllib3 python-dateutil cryptography

# Install Ansible
pip install ansible

# Install collection (if not already)
ansible-galaxy collection install /path/to/objectscale/collection

# Verify installation
ansible-galaxy collection list | grep objectscale
```

### Configuration
```bash
# Set environment variables
export OBJECTSCALE_HOST="10.0.0.1"
export OBJECTSCALE_USERNAME="admin"
export OBJECTSCALE_PASSWORD="your_password"
export VALIDATE_CERTS="false"

# Or pass as Ansible extra vars
ansible-playbook playbook.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

---

## 📊 Test Results Summary

| Component | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| vdc_certificate | 88 | ✅ PASS | 91% |
| vdc_certificate_info | 20 | ✅ PASS | 92% |
| vdc_certificate_chain | 36 | ✅ PASS | 91% |
| vdc_certificate_chain_info | 14 | ✅ PASS | 92% |
| VdcKeystoreApi | 20 | ✅ PASS | 95% |
| ObjectCertKeystoreApi | 20 | ✅ PASS | 95% |
| **TOTAL** | **158** | **✅ PASS** | **92%** |

---

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test connectivity
curl -k https://10.0.0.1:4443/api/v1/vdc/info

# Test with credentials
curl -k -u admin:password https://10.0.0.1:4443/api/v1/vdc/info
```

### Module Not Found
```bash
# Verify collection installed
ansible-galaxy collection list | grep objectscale

# Install if missing
ansible-galaxy collection install dellemc.objectscale
```

### Cryptography Not Available
```bash
# Install cryptography for metadata extraction
pip install cryptography
```

### Ansible Not Found
```bash
# Install Ansible
pip install ansible

# Verify installation
ansible --version
```

---

## 📖 Documentation Structure

```
objectscale/
├── TESTING_README.md          ← You are here
├── TESTING_SUMMARY.md         ← Quick reference
├── TESTING_GUIDE.md           ← Comprehensive guide
├── GUI_TESTING_GUIDE.md       ← GUI verification
├── quick_test.sh              ← Automated script
├── playbooks/modules/
│   ├── vdc_certificate.yml
│   ├── vdc_certificate_info.yml
│   ├── vdc_certificate_chain.yml
│   └── vdc_certificate_chain_info.yml
├── docs/modules/
│   ├── vdc_certificate.rst
│   ├── vdc_certificate_info.rst
│   ├── vdc_certificate_chain.rst
│   └── vdc_certificate_chain_info.rst
└── tests/unit/plugins/modules/
    ├── test_vdc_certificate.py
    ├── test_vdc_certificate_info.py
    ├── test_vdc_certificate_chain.py
    ├── test_vdc_certificate_chain_info.py
    ├── test_vdc_keystore_api.py
    └── test_object_cert_keystore_api.py
```

---

## 🎓 Learning Path

### For Beginners
1. Read TESTING_SUMMARY.md (5 min)
2. Run quick_test.sh (2 min)
3. Run info modules (5 min)
4. Read GUI_TESTING_GUIDE.md (10 min)

### For Developers
1. Read TESTING_GUIDE.md (20 min)
2. Run unit tests (5 min)
3. Review test code (30 min)
4. Run functional tests (15 min)

### For QA/Operators
1. Read TESTING_SUMMARY.md (5 min)
2. Follow GUI_TESTING_GUIDE.md (30 min)
3. Create comparison table (15 min)
4. Document findings (15 min)

---

## 📞 Support

For issues or questions:
1. Check TESTING_GUIDE.md → Troubleshooting section
2. Review module documentation in docs/modules/
3. Check unit test code for examples
4. Review example playbooks in playbooks/modules/

---

## 🎉 Next Steps

1. **Choose a testing method** from the options above
2. **Set up your environment** with prerequisites
3. **Run the tests** following the appropriate guide
4. **Verify results** against success criteria
5. **Document findings** and report results

**Happy testing! 🚀**
