# ObjectScale GUI Testing Guide for VDC Keystore Modules

This guide explains how to verify the VDC Keystore modules using the ObjectScale management GUI.

## Prerequisites

- ObjectScale cluster running and accessible
- Admin credentials
- Web browser with HTTPS support
- Modules already tested via CLI/Ansible

---

## Part 1: Access ObjectScale Management UI

### Step 1: Open Management Console

1. Open your web browser
2. Navigate to: `https://<objectscale-ip>:4443`
   - Replace `<objectscale-ip>` with your ObjectScale management IP
   - Example: `https://10.0.0.1:4443`

3. You should see the ObjectScale login page

### Step 2: Login

1. Enter credentials:
   - **Username**: `admin` (or your admin user)
   - **Password**: Your admin password

2. Click **Login**

3. You should now be in the ObjectScale management dashboard

---

## Part 2: Locate Certificate Information

### Finding VDC Certificate

1. In the left sidebar, navigate to:
   - **Settings** → **Certificates** (or similar path depending on UI version)
   - OR **Administration** → **Security** → **Certificates**

2. Look for a section labeled:
   - **VDC Certificate** or **Management Certificate**
   - **TLS Certificate** or **SSL Certificate**

3. You should see:
   - Certificate subject (CN=...)
   - Issuer information
   - Expiry date
   - Fingerprint (SHA-256 or similar)
   - Certificate chain details

### Finding Object-cert Certificate

1. In the same **Certificates** section, look for:
   - **Object-cert Certificate** or **S3 Certificate**
   - **Object Storage Certificate**
   - **Secondary Certificate**

2. You should see similar information as VDC certificate

---

## Part 3: Verify Module Output Against GUI

### Step 1: Run Info Module

```bash
# Terminal 1: Run Ansible module
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  playbooks/modules/vdc_certificate_info.yml
```

### Step 2: Compare Output

**Module Output** (from terminal):
```yaml
vdc_certificate_details:
  fingerprint: "A1B2C3D4E5F6..."
  chain_length: 3
  leaf_subject: "CN=objectscale.example.com"
  not_after: "2027-01-15T00:00:00"
```

**GUI Display** (in browser):
- Navigate to Certificates section
- Look for the same information:
  - Fingerprint should match exactly
  - Chain length should match (count of certificates)
  - Subject should match
  - Expiry date should match

### Step 3: Verify Fingerprint

1. In GUI, find the certificate fingerprint
2. In terminal output, find the fingerprint from module
3. **They must match exactly** (same hash value)

```
Module:  A1B2C3D4E5F6...
GUI:     A1B2C3D4E5F6...
         ✓ Match!
```

---

## Part 4: Test Certificate Update (Advanced)

### Step 1: Prepare New Certificate

```bash
# Generate a test self-signed certificate
openssl req -x509 -newkey rsa:2048 \
  -keyout /tmp/test-key.pem \
  -out /tmp/test-cert.pem \
  -days 365 -nodes \
  -subj "/CN=test.objectscale.example.com"
```

### Step 2: Run Update Module (Check Mode)

```bash
# Run in check mode (no actual change)
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/tmp/test-key.pem" \
  -e "certificate_chain_path=/tmp/test-cert.pem" \
  playbooks/modules/vdc_certificate.yml \
  --check
```

### Step 3: Verify No Change in GUI

1. Refresh the ObjectScale GUI
2. Check the certificate fingerprint
3. **It should NOT have changed** (because we used `--check` mode)

### Step 4: Run Update Module (Actual)

```bash
# Run without --check to actually update
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/tmp/test-key.pem" \
  -e "certificate_chain_path=/tmp/test-cert.pem" \
  playbooks/modules/vdc_certificate.yml
```

### Step 5: Verify Change in GUI

1. Refresh the ObjectScale GUI
2. Check the certificate fingerprint
3. **It should have changed** to the new certificate's fingerprint
4. Subject should now be `CN=test.objectscale.example.com`

---

## Part 5: Test Idempotency via GUI

### Step 1: Get Current Certificate

```bash
# Run info module to get current certificate
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  playbooks/modules/vdc_certificate_info.yml
```

Note the fingerprint: `ABC123...`

### Step 2: Re-apply Same Certificate

```bash
# Run update module with same certificate
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/current-key.pem" \
  -e "certificate_chain_path=/path/to/current-chain.pem" \
  playbooks/modules/vdc_certificate.yml
```

### Step 3: Verify Idempotency

**Module Output**:
```
changed: false
```

**GUI Verification**:
1. Refresh the ObjectScale GUI
2. Check the certificate fingerprint
3. **It should be the same** as before: `ABC123...`

---

## Part 6: Monitor Certificate Expiry

### Step 1: Run Info Module

```bash
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  playbooks/modules/vdc_certificate_info.yml
```

### Step 2: Check Expiry in Module Output

```yaml
vdc_certificate_details:
  not_after: "2027-01-15T00:00:00"
```

### Step 3: Verify in GUI

1. Navigate to Certificates section
2. Look for **Expiry Date** or **Valid Until**
3. **It should match** the module output: `2027-01-15`

### Step 4: Set Reminder

If certificate expires soon:
1. Note the expiry date
2. Set a calendar reminder
3. Plan certificate renewal before expiry

---

## Part 7: Troubleshooting GUI Issues

### Issue: Certificate Information Not Visible

**Possible Causes**:
1. Wrong menu path (varies by ObjectScale version)
2. Insufficient permissions
3. Certificate not yet installed

**Solution**:
1. Check ObjectScale documentation for your version
2. Verify admin permissions
3. Run info module to check if certificate exists

### Issue: Fingerprint Doesn't Match

**Possible Causes**:
1. GUI shows different hash algorithm (SHA-1 vs SHA-256)
2. GUI not refreshed after module update
3. Different certificate selected

**Solution**:
1. Check hash algorithm in GUI (should be SHA-256)
2. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
3. Verify you're looking at the correct certificate

### Issue: Certificate Update Not Reflected in GUI

**Possible Causes**:
1. Module ran in check mode (no actual change)
2. Browser cache not cleared
3. Update failed silently

**Solution**:
1. Check module output for `changed: true`
2. Hard refresh browser (Ctrl+Shift+Delete)
3. Check module logs for errors

---

## Part 8: Security Verification

### Verify Private Key Not Exposed

1. In ObjectScale GUI, look for certificate details
2. **Private key should NEVER be visible**
3. Only public certificate chain should be shown

### Verify Diff Mode Security

```bash
# Run module with diff mode
ansible-playbook -i localhost, -c local \
  -e "objectscale_host=10.0.0.1" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/tmp/test-key.pem" \
  -e "certificate_chain_path=/tmp/test-cert.pem" \
  playbooks/modules/vdc_certificate.yml \
  --diff --check
```

**Verify in output**:
- ✅ Shows fingerprint changes
- ✅ Shows certificate chain changes
- ❌ **Never shows private key content**

---

## Part 9: Comparison Table

Create a comparison table to verify all details match:

| Detail | Module Output | GUI Display | Match? |
|--------|---------------|-------------|--------|
| Fingerprint | ABC123... | ABC123... | ✓ |
| Chain Length | 3 | 3 | ✓ |
| Subject | CN=obs.example.com | CN=obs.example.com | ✓ |
| Issuer | CN=CA | CN=CA | ✓ |
| Not Before | 2024-01-15 | 2024-01-15 | ✓ |
| Not After | 2027-01-15 | 2027-01-15 | ✓ |
| Serial | FF01... | FF01... | ✓ |

---

## Part 10: Final Verification Checklist

- [ ] Can access ObjectScale management UI
- [ ] Can locate VDC Certificate section
- [ ] Can locate Object-cert Certificate section
- [ ] Info module output matches GUI display
- [ ] Fingerprints match exactly
- [ ] Expiry dates match
- [ ] Chain lengths match
- [ ] Certificate update reflected in GUI
- [ ] Idempotency verified (no change on re-apply)
- [ ] Private key never exposed in GUI or module output
- [ ] Diff mode shows changes without leaking secrets

---

## Next Steps

1. **Document findings**: Save screenshots of GUI showing certificate details
2. **Compare outputs**: Create comparison table above
3. **Test all modules**: Repeat for both VDC and Object-cert certificates
4. **Report results**: Update JIRA with GUI verification results
5. **Monitor expiry**: Set reminders for certificate renewal

---

## Additional Resources

- ObjectScale Documentation: Check your version's admin guide
- Ansible Collection Docs: See `docs/modules/vdc_certificate*.rst`
- Example Playbooks: See `playbooks/modules/vdc_certificate*.yml`
