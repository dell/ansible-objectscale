# ObjectScale 4.3 Testing Quick Reference

Quick commands for testing VDC Keystore modules using ObjectScale 4.3 GUI and CLI (objctl).

---

## 🚀 Quick Start

### Option 1: GUI Testing (Visual)
1. Open: `https://<objectscale-ip>:4443`
2. Navigate to: **Settings → Security → Certificates** (or similar)
3. Compare GUI values with Ansible module output

### Option 2: CLI Testing (Command-line)
1. Configure objctl: `objctl config set host 10.0.0.100`
2. Query certificate: `objctl certificate get vdc`
3. Compare with Ansible module output

---

## 📋 Command Comparison

### Query VDC Certificate

**GUI**:
1. Navigate to VDC Certificate section
2. View fingerprint, subject, expiry date

**CLI (objctl)**:
```bash
# Get all details
objctl certificate get vdc

# Get JSON format
objctl certificate get vdc --format json

# Get specific fields
objctl certificate get vdc --format json | jq '.fingerprint'
objctl certificate get vdc --format json | jq '.subject'
objctl certificate get vdc --format json | jq '.validUntil'
```

**Ansible Module**:
```bash
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

---

### Query Object-cert Certificate

**GUI**:
1. Navigate to Object-cert Certificate section
2. View fingerprint, subject, expiry date

**CLI (objctl)**:
```bash
# Get all details
objctl certificate get object-cert

# Get JSON format
objctl certificate get object-cert --format json

# Get specific fields
objctl certificate get object-cert --format json | jq '.fingerprint'
objctl certificate get object-cert --format json | jq '.subject'
```

**Ansible Module**:
```bash
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

---

### Update VDC Certificate

**GUI**:
1. Navigate to VDC Certificate section
2. Click **Update** or **Upload**
3. Select new certificate and key files
4. Confirm update

**CLI (objctl)**:
```bash
# Update certificate
objctl certificate set vdc \
  --key /path/to/key.pem \
  --cert /path/to/cert.pem

# Verify update
objctl certificate get vdc --format json | jq '.fingerprint'
```

**Ansible Module (Check Mode - Safe)**:
```bash
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/key.pem" \
  -e "certificate_chain_path=/path/to/cert.pem" \
  --check
```

**Ansible Module (Actual Update)**:
```bash
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/key.pem" \
  -e "certificate_chain_path=/path/to/cert.pem"
```

---

### Update Object-cert Certificate

**GUI**:
1. Navigate to Object-cert Certificate section
2. Click **Update** or **Upload**
3. Select new certificate and key files
4. Confirm update

**CLI (objctl)**:
```bash
# Update certificate
objctl certificate set object-cert \
  --key /path/to/key.pem \
  --cert /path/to/cert.pem

# Verify update
objctl certificate get object-cert --format json | jq '.fingerprint'
```

**Ansible Module (Check Mode - Safe)**:
```bash
ansible-playbook playbooks/modules/vdc_certificate_chain.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/key.pem" \
  -e "certificate_chain_path=/path/to/cert.pem" \
  --check
```

---

## 🔍 Verification Checklist

### Info Modules (Read-only)

```bash
# VDC Certificate Info
✓ Can query via GUI
✓ Can query via objctl
✓ Can query via Ansible
✓ Fingerprints match
✓ Subjects match
✓ Expiry dates match
✓ changed=false in Ansible
```

### State Modules (Management)

```bash
# VDC Certificate Update
✓ Can run in check mode (safe)
✓ Can run actual update
✓ GUI reflects changes
✓ objctl reflects changes
✓ Ansible module reflects changes
✓ Idempotency works (second run shows changed=false)
✓ Can restore original
```

---

## 📊 Comparison Table Template

| Detail | GUI | objctl | Ansible | Match? |
|--------|-----|--------|---------|--------|
| Fingerprint | | | | |
| Subject | | | | |
| Issuer | | | | |
| Valid Until | | | | |
| Chain Length | | | | |

---

## 🧪 Test Scenarios

### Scenario 1: Query Current Certificates (Safest)

```bash
# GUI: Navigate to certificate section and view details
# objctl: objctl certificate get vdc
# Ansible: ansible-playbook playbooks/modules/vdc_certificate_info.yml
# Result: All three should show same fingerprint
```

### Scenario 2: Test Check Mode (Safe)

```bash
# Prepare test certificate
openssl req -x509 -newkey rsa:2048 -keyout test-key.pem -out test-cert.pem -days 365 -nodes

# Run Ansible in check mode
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "private_key_path=test-key.pem" \
  -e "certificate_chain_path=test-cert.pem" \
  --check

# GUI: Fingerprint should NOT change
# objctl: objctl certificate get vdc should show original fingerprint
# Ansible: changed=true (predicted) but no actual change
```

### Scenario 3: Test Actual Update (Use Caution)

```bash
# Backup current certificate
objctl certificate get vdc --format pem > backup-vdc-cert.pem

# Update via Ansible
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "private_key_path=test-key.pem" \
  -e "certificate_chain_path=test-cert.pem"

# Verify via all three methods
# GUI: Fingerprint should change
# objctl: objctl certificate get vdc should show new fingerprint
# Ansible: changed=true, shows new fingerprint

# Restore
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "certificate_chain_path=backup-vdc-cert.pem"
```

### Scenario 4: Test Idempotency

```bash
# Run Ansible module twice with same certificate
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "private_key_path=current-key.pem" \
  -e "certificate_chain_path=current-cert.pem"

# First run: changed=true or changed=false (depends on if cert differs)
# Second run: changed=false (idempotent)

# Verify via objctl
objctl certificate get vdc --format json | jq '.fingerprint'
# Should be same both times
```

---

## 🔐 Security Verification

```bash
# Verify private key NOT visible in GUI
# GUI should only show public certificate chain

# Verify private key NOT visible in objctl output
objctl certificate get vdc --format json | grep -i "private"
# Should return: (nothing)

# Verify private key NOT visible in Ansible output
ansible-playbook playbooks/modules/vdc_certificate_info.yml -vvv 2>&1 | grep -i "private"
# Should return: (nothing)

# Verify fingerprints match across all three methods
gui_fp="ABC123..."
objctl_fp=$(objctl certificate get vdc --format json | jq -r '.fingerprint')
ansible_fp=$(ansible-playbook playbooks/modules/vdc_certificate_info.yml 2>&1 | grep -oP 'fingerprint.*?:\s*\K[^ ]+')

[ "$gui_fp" = "$objctl_fp" ] && [ "$objctl_fp" = "$ansible_fp" ] && echo "✓ All match!"
```

---

## 📈 Monitoring

### Check Certificate Expiry

**GUI**:
```
Navigate to certificate section → View "Valid Until" or "Expires" date
```

**CLI (objctl)**:
```bash
# Get expiry date
objctl certificate get vdc --format json | jq '.validUntil'

# Calculate days until expiry
expiry=$(objctl certificate get vdc --format json | jq -r '.validUntil')
days=$(($(date -d "$expiry" +%s) - $(date +%s)) / 86400)
echo "Days until expiry: $days"

# Alert if expiring soon
[ $days -lt 30 ] && echo "⚠️ Certificate expires in less than 30 days!"
```

**Ansible Module**:
```bash
ansible-playbook playbooks/modules/vdc_certificate_info.yml 2>&1 | grep "not_after"
```

---

## 🛠️ Troubleshooting

| Issue | GUI | objctl | Ansible |
|-------|-----|--------|---------|
| Connection refused | Check URL and network | `objctl vdc info` | Check host/port |
| Authentication failed | Check credentials | `objctl config set password` | Check credentials |
| Certificate not found | Check menu path | `objctl certificate get vdc` | Check module |
| Fingerprint mismatch | Refresh page | Check hash algorithm | Check module output |

---

## 📚 Documentation Files

- **OBJECTSCALE_4.3_GUI_TESTING.md** — Detailed GUI testing guide
- **OBJECTSCALE_4.3_CLI_TESTING.md** — Detailed CLI (objctl) testing guide
- **OBJECTSCALE_4.3_QUICK_REFERENCE.md** — This file

---

## ✅ Testing Workflow

```
1. Query Current Certificates
   ├─ GUI: Navigate and view
   ├─ objctl: objctl certificate get vdc
   └─ Ansible: ansible-playbook vdc_certificate_info.yml

2. Compare Outputs
   ├─ Fingerprints match?
   ├─ Subjects match?
   └─ Expiry dates match?

3. Test Check Mode (Safe)
   ├─ Prepare test certificate
   ├─ Run Ansible with --check
   ├─ Verify no change in GUI
   └─ Verify no change via objctl

4. Test Actual Update (Optional)
   ├─ Backup current certificate
   ├─ Run Ansible without --check
   ├─ Verify change in GUI
   ├─ Verify change via objctl
   └─ Restore original

5. Test Idempotency
   ├─ Run Ansible twice
   ├─ Second run should show changed=false
   └─ Verify fingerprint unchanged

6. Document Results
   ├─ Fill comparison table
   ├─ Save screenshots
   └─ Update JIRA
```

---

## 🎯 Success Criteria

- [ ] Can access ObjectScale 4.3 GUI
- [ ] Can query certificates via GUI
- [ ] Can query certificates via objctl
- [ ] Can query certificates via Ansible
- [ ] All three methods show same fingerprint
- [ ] All three methods show same subject
- [ ] All three methods show same expiry date
- [ ] Check mode works (no actual change)
- [ ] Actual update works (change reflected)
- [ ] Idempotency works (second run shows no change)
- [ ] Private key never exposed
- [ ] Can restore original certificate

---

## 🚀 Next Steps

1. **Access ObjectScale 4.3**
   - Open GUI: `https://<ip>:4443`
   - Configure objctl: `objctl config set host <ip>`

2. **Query Certificates**
   - Via GUI: Navigate to certificate section
   - Via objctl: `objctl certificate get vdc`
   - Via Ansible: Run info modules

3. **Compare Outputs**
   - Create comparison table
   - Verify fingerprints match
   - Verify subjects match

4. **Test Updates (Optional)**
   - Prepare test certificate
   - Run in check mode first
   - Run actual update
   - Restore original

5. **Document Results**
   - Save screenshots
   - Fill comparison table
   - Update JIRA

---

**Happy testing! 🎉**
