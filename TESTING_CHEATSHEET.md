# VDC Keystore Modules — Testing Cheatsheet

Quick reference for testing the four VDC Keystore modules.

---

## 🚀 Quick Commands

### Run Quick Test (All-in-One)
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale
./quick_test.sh
```

### Run Unit Tests
```bash
# All tests
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py -v

# Specific module
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_chain.py -v

# With coverage
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py --cov=plugins/modules
```

### Run Info Modules (Safe, Read-Only)
```bash
# VDC Certificate
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"

# Object-cert Certificate
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

### Run State Modules (Check Mode - Safe)
```bash
# VDC Certificate (check mode)
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/key.pem" \
  -e "certificate_chain_path=/path/to/chain.pem" \
  --check

# Object-cert Certificate (check mode)
ansible-playbook playbooks/modules/vdc_certificate_chain.yml \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/key.pem" \
  -e "certificate_chain_path=/path/to/chain.pem" \
  --check
```

### Run Functional Tests (QE Repo)
```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/ansible-objectscale-qe

# VDC Certificate Chain
ansible-playbook VDC_Certificate_Chain/TC-01_set_certificate_chain_inline.yml
ansible-playbook VDC_Certificate_Chain/TC-02_idempotence_no_change.yml
ansible-playbook VDC_Certificate_Chain/TC-03_check_mode.yml

# VDC Certificate Chain Info
ansible-playbook VDC_Certificate_Chain_Info/TC-01_get_certificate_chain_info.yml
ansible-playbook VDC_Certificate_Chain_Info/TC-02_changed_always_false.yml
```

---

## 📋 Module Matrix

| Module | Type | Endpoint | Safe? | Command |
|--------|------|----------|-------|---------|
| `vdc_certificate_info` | Info | GET /vdc/keystore | ✅ Yes | `ansible-playbook playbooks/modules/vdc_certificate_info.yml` |
| `vdc_certificate` | State | PUT /vdc/keystore | ⚠️ Check mode | `ansible-playbook playbooks/modules/vdc_certificate.yml --check` |
| `vdc_certificate_chain_info` | Info | GET /object-cert/keystore | ✅ Yes | `ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml` |
| `vdc_certificate_chain` | State | PUT /object-cert/keystore | ⚠️ Check mode | `ansible-playbook playbooks/modules/vdc_certificate_chain.yml --check` |

---

## 🔍 Expected Output

### Info Module Output
```yaml
changed: false
vdc_certificate_details:
  fingerprint: "ABC123DEF456..."
  chain: "-----BEGIN CERTIFICATE-----\n..."
  chain_length: 3
  leaf_subject: "CN=objectscale.example.com"
  not_after: "2027-01-15T00:00:00"
```

### State Module Output (First Run)
```yaml
changed: true
vdc_certificate_details:
  fingerprint: "NEW_FINGERPRINT..."
  chain_length: 3
```

### State Module Output (Second Run - Idempotent)
```yaml
changed: false
vdc_certificate_details:
  fingerprint: "NEW_FINGERPRINT..."
  chain_length: 3
```

---

## ✅ Verification Checklist

### Info Modules
- [ ] Returns `changed=false`
- [ ] Returns `vdc_certificate_details` or `vdc_certificate_chain_details`
- [ ] Includes `fingerprint`, `chain`, `chain_length`
- [ ] Optionally includes `leaf_subject`, `not_after` (if cryptography installed)

### State Modules (First Run)
- [ ] Returns `changed=true`
- [ ] Returns certificate details
- [ ] Fingerprint is new value

### State Modules (Second Run)
- [ ] Returns `changed=false` (idempotent)
- [ ] Fingerprint is same as first run

### Check Mode
- [ ] Returns `changed=true` (predicted)
- [ ] No actual change made
- [ ] GUI shows no change

### Diff Mode
- [ ] Shows fingerprint changes
- [ ] **Never shows private key content**
- [ ] Shows before/after comparison

---

## 🔐 Security Checks

```bash
# Verify private key NOT in diff
ansible-playbook playbooks/modules/vdc_certificate.yml --diff --check | grep -i "private"
# Should return: (nothing)

# Verify private key NOT in logs
ansible-playbook playbooks/modules/vdc_certificate.yml -vvv 2>&1 | grep -i "private"
# Should return: (nothing)

# Verify credentials NOT logged
ansible-playbook playbooks/modules/vdc_certificate.yml -vvv 2>&1 | grep "password"
# Should return: (nothing or only masked values)
```

---

## 🧪 Test Scenarios

### Scenario 1: Query Certificates (Safest)
```bash
# No risk - read-only
ansible-playbook playbooks/modules/vdc_certificate_info.yml
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml
```

### Scenario 2: Test Idempotency (Safe)
```bash
# Check mode - no actual change
ansible-playbook playbooks/modules/vdc_certificate.yml --check
ansible-playbook playbooks/modules/vdc_certificate.yml --check
# Both should show: changed=false
```

### Scenario 3: Test Diff Mode (Safe)
```bash
# Check mode + diff - shows changes without making them
ansible-playbook playbooks/modules/vdc_certificate.yml --check --diff
# Should show fingerprint changes, never private key
```

### Scenario 4: Actual Update (Requires Real Cert)
```bash
# Generate test cert
openssl req -x509 -newkey rsa:2048 -keyout test-key.pem -out test-cert.pem -days 365 -nodes

# Update (actual change)
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "private_key_path=test-key.pem" \
  -e "certificate_chain_path=test-cert.pem"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | `curl -k https://10.0.0.1:4443/api/v1/vdc/info` |
| Authentication failed | `curl -k -u admin:password https://10.0.0.1:4443/api/v1/vdc/info` |
| Module not found | `ansible-galaxy collection list \| grep objectscale` |
| Cryptography not available | `pip install cryptography` |
| Pytest not found | `pip install pytest` |

---

## 📊 Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| vdc_certificate | 88 | ✅ PASS |
| vdc_certificate_info | 20 | ✅ PASS |
| vdc_certificate_chain | 36 | ✅ PASS |
| vdc_certificate_chain_info | 14 | ✅ PASS |
| VdcKeystoreApi | 20 | ✅ PASS |
| ObjectCertKeystoreApi | 20 | ✅ PASS |
| **TOTAL** | **158** | **✅ PASS** |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| TESTING_README.md | Overview (start here) |
| TESTING_SUMMARY.md | Quick reference |
| TESTING_GUIDE.md | Comprehensive guide |
| GUI_TESTING_GUIDE.md | ObjectScale UI verification |
| quick_test.sh | Automated script |
| TESTING_CHEATSHEET.md | This file |

---

## 🎯 Testing Workflow

```
1. Run quick_test.sh
   ↓
2. Run unit tests
   ↓
3. Run info modules (read-only)
   ↓
4. Run state modules in check mode
   ↓
5. Verify in ObjectScale GUI
   ↓
6. Run functional tests (QE repo)
   ↓
7. Document results
```

---

## 🚀 One-Liner Commands

```bash
# Quick test
./quick_test.sh

# All unit tests
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py -v

# Info modules
ansible-playbook playbooks/modules/vdc_certificate_info.yml && \
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml

# Check mode (safe)
ansible-playbook playbooks/modules/vdc_certificate.yml --check && \
ansible-playbook playbooks/modules/vdc_certificate_chain.yml --check

# Diff mode (safe)
ansible-playbook playbooks/modules/vdc_certificate.yml --check --diff && \
ansible-playbook playbooks/modules/vdc_certificate_chain.yml --check --diff
```

---

## 💡 Pro Tips

1. **Always use `--check` first** before actual updates
2. **Use `--diff` to preview changes** without exposing secrets
3. **Run info modules first** to understand current state
4. **Verify in GUI** after any changes
5. **Check logs** for any warnings or errors
6. **Use environment variables** to avoid hardcoding credentials

---

## 🎓 Learning Resources

- **TESTING_GUIDE.md** — Full procedures for each method
- **GUI_TESTING_GUIDE.md** — Step-by-step GUI verification
- **docs/modules/vdc_certificate*.rst** — Module documentation
- **playbooks/modules/vdc_certificate*.yml** — Example playbooks
- **tests/unit/plugins/modules/test_vdc*.py** — Test code examples

---

**Happy Testing! 🎉**
