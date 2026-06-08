# Testing VDC Keystore Modules in ObjectScale 4.3 GUI

Complete guide for testing the four VDC Keystore modules using ObjectScale 4.3 management GUI.

---

## Prerequisites

- ObjectScale 4.3 cluster running and accessible
- Admin credentials for ObjectScale
- Web browser with HTTPS support
- Modules deployed in Ansible collection

---

## Part 1: Access ObjectScale 4.3 Management GUI

### Step 1: Open ObjectScale Management Console

1. Open your web browser
2. Navigate to: `https://<objectscale-management-ip>:4443`
   - Replace `<objectscale-management-ip>` with your ObjectScale management IP
   - Example: `https://10.0.0.100:4443`

3. You should see the ObjectScale 4.3 login page

### Step 2: Login to ObjectScale 4.3

1. Enter credentials:
   - **Username**: `admin` (or your admin user)
   - **Password**: Your admin password

2. Click **Login** or press Enter

3. You should now be in the ObjectScale 4.3 management dashboard

---

## Part 2: Locate Certificate Management in ObjectScale 4.3

### Finding Certificate Settings in ObjectScale 4.3

The certificate management location varies by ObjectScale version. Try these paths:

#### Path 1: Settings → Security
1. In the left sidebar, click **Settings**
2. Look for **Security** or **Certificates** section
3. You should see:
   - **VDC Certificate** (Management TLS)
   - **Object-cert Certificate** (S3/Object Storage TLS)

#### Path 2: Administration → Certificates
1. In the left sidebar, click **Administration**
2. Look for **Certificates** or **Security** subsection
3. You should see certificate management options

#### Path 3: System → Certificates
1. In the left sidebar, click **System**
2. Look for **Certificates** or **TLS Configuration**
3. You should see both VDC and Object-cert certificates

#### Path 4: Search Function
1. Use the search bar (usually at top of page)
2. Search for: "Certificate" or "TLS"
3. Navigate to the results

---

## Part 3: Verify VDC Certificate (vdc_certificate_info)

### Step 1: Locate VDC Certificate Section

1. Navigate to certificate settings (see Part 2)
2. Find the section labeled:
   - **VDC Certificate** or **Management Certificate**
   - **VDC TLS Certificate**
   - **Management Endpoint Certificate**

### Step 2: View VDC Certificate Details

You should see the following information:

**Certificate Details**:
```
Subject (CN):           CN=objectscale.example.com
Issuer:                 CN=Your-CA
Valid From:             2024-01-15 00:00:00 UTC
Valid Until (Expires):  2027-01-15 00:00:00 UTC
Fingerprint (SHA-256):  ABC123DEF456...
Serial Number:          FF01...
```

### Step 3: Note the Fingerprint

1. Copy the **SHA-256 Fingerprint** value
2. This is what the `vdc_certificate_info` module will return
3. Keep this for comparison with module output

### Step 4: Run Ansible Module and Compare

```bash
# Run the vdc_certificate_info module
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

**Expected Module Output**:
```yaml
vdc_certificate_details:
  fingerprint: "ABC123DEF456..."  # Should match GUI
  chain_length: 3
  leaf_subject: "CN=objectscale.example.com"  # Should match GUI
  not_after: "2027-01-15T00:00:00"  # Should match GUI
changed: false
```

### Step 5: Verify Match

| Detail | GUI Value | Module Output | Match? |
|--------|-----------|---------------|--------|
| Fingerprint | ABC123DEF456... | ABC123DEF456... | ✓ |
| Subject | CN=objectscale.example.com | CN=objectscale.example.com | ✓ |
| Expires | 2027-01-15 | 2027-01-15T00:00:00 | ✓ |
| Chain Length | 3 | 3 | ✓ |

---

## Part 4: Verify Object-cert Certificate (vdc_certificate_chain_info)

### Step 1: Locate Object-cert Certificate Section

1. In the same certificate settings area (Part 2)
2. Find the section labeled:
   - **Object-cert Certificate** or **S3 Certificate**
   - **Object Storage Certificate**
   - **Secondary Certificate**
   - **Object Endpoint Certificate**

### Step 2: View Object-cert Certificate Details

You should see similar information as VDC certificate:

**Certificate Details**:
```
Subject (CN):           CN=s3.objectscale.example.com
Issuer:                 CN=Your-CA
Valid From:             2024-06-01 00:00:00 UTC
Valid Until (Expires):  2027-06-01 00:00:00 UTC
Fingerprint (SHA-256):  XYZ789ABC123...
Serial Number:          FF02...
```

### Step 3: Note the Fingerprint

1. Copy the **SHA-256 Fingerprint** value
2. This is what the `vdc_certificate_chain_info` module will return
3. Keep this for comparison with module output

### Step 4: Run Ansible Module and Compare

```bash
# Run the vdc_certificate_chain_info module
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

**Expected Module Output**:
```yaml
vdc_certificate_chain_details:
  fingerprint: "XYZ789ABC123..."  # Should match GUI
  chain_length: 2
  leaf_subject: "CN=s3.objectscale.example.com"  # Should match GUI
  not_after: "2027-06-01T00:00:00"  # Should match GUI
changed: false
```

### Step 5: Verify Match

| Detail | GUI Value | Module Output | Match? |
|--------|-----------|---------------|--------|
| Fingerprint | XYZ789ABC123... | XYZ789ABC123... | ✓ |
| Subject | CN=s3.objectscale.example.com | CN=s3.objectscale.example.com | ✓ |
| Expires | 2027-06-01 | 2027-06-01T00:00:00 | ✓ |
| Chain Length | 2 | 2 | ✓ |

---

## Part 5: Test VDC Certificate Update (vdc_certificate)

### Step 1: Prepare Test Certificate

```bash
# Generate a self-signed test certificate
openssl req -x509 -newkey rsa:2048 \
  -keyout /tmp/test-vdc-key.pem \
  -out /tmp/test-vdc-cert.pem \
  -days 365 -nodes \
  -subj "/CN=test-vdc.objectscale.example.com"

# View the test certificate fingerprint
openssl x509 -in /tmp/test-vdc-cert.pem -noout -fingerprint -sha256
# Output: SHA256 Fingerprint=ABC123...
```

### Step 2: Run Module in Check Mode (Safe)

```bash
# Run in check mode - no actual change
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/tmp/test-vdc-key.pem" \
  -e "certificate_chain_path=/tmp/test-vdc-cert.pem" \
  --check
```

**Expected Output**:
```yaml
changed: true  # Would change if we actually ran it
vdc_certificate_details:
  fingerprint: "ABC123..."  # New certificate fingerprint
```

### Step 3: Verify No Change in GUI

1. Refresh the ObjectScale GUI (F5 or Ctrl+R)
2. Navigate back to VDC Certificate section
3. **Fingerprint should NOT have changed** (because we used `--check`)
4. Should still show the original fingerprint

### Step 4: Run Module Actually (Optional - Use Caution)

```bash
# Run without --check to actually update
# ⚠️ WARNING: This will change the certificate!
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/tmp/test-vdc-key.pem" \
  -e "certificate_chain_path=/tmp/test-vdc-cert.pem"
```

### Step 5: Verify Change in GUI

1. Refresh the ObjectScale GUI
2. Navigate to VDC Certificate section
3. **Fingerprint should have changed** to: `ABC123...`
4. Subject should now be: `CN=test-vdc.objectscale.example.com`

### Step 6: Restore Original Certificate

```bash
# Get the original certificate (you should have backed it up)
# Or restore from your certificate management system

ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/original-key.pem" \
  -e "certificate_chain_path=/path/to/original-cert.pem"
```

---

## Part 6: Test Object-cert Certificate Update (vdc_certificate_chain)

### Step 1: Prepare Test Certificate

```bash
# Generate a self-signed test certificate
openssl req -x509 -newkey rsa:2048 \
  -keyout /tmp/test-obj-cert-key.pem \
  -out /tmp/test-obj-cert-cert.pem \
  -days 365 -nodes \
  -subj "/CN=test-s3.objectscale.example.com"

# View the test certificate fingerprint
openssl x509 -in /tmp/test-obj-cert-cert.pem -noout -fingerprint -sha256
# Output: SHA256 Fingerprint=XYZ789...
```

### Step 2: Run Module in Check Mode (Safe)

```bash
# Run in check mode - no actual change
ansible-playbook playbooks/modules/vdc_certificate_chain.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/tmp/test-obj-cert-key.pem" \
  -e "certificate_chain_path=/tmp/test-obj-cert-cert.pem" \
  --check
```

**Expected Output**:
```yaml
changed: true  # Would change if we actually ran it
vdc_certificate_chain_details:
  fingerprint: "XYZ789..."  # New certificate fingerprint
```

### Step 3: Verify No Change in GUI

1. Refresh the ObjectScale GUI
2. Navigate to Object-cert Certificate section
3. **Fingerprint should NOT have changed** (because we used `--check`)
4. Should still show the original fingerprint

### Step 4: Run Module Actually (Optional - Use Caution)

```bash
# Run without --check to actually update
# ⚠️ WARNING: This will change the certificate!
ansible-playbook playbooks/modules/vdc_certificate_chain.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/tmp/test-obj-cert-key.pem" \
  -e "certificate_chain_path=/tmp/test-obj-cert-cert.pem"
```

### Step 5: Verify Change in GUI

1. Refresh the ObjectScale GUI
2. Navigate to Object-cert Certificate section
3. **Fingerprint should have changed** to: `XYZ789...`
4. Subject should now be: `CN=test-s3.objectscale.example.com`

### Step 6: Restore Original Certificate

```bash
# Restore from your certificate management system
ansible-playbook playbooks/modules/vdc_certificate_chain.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/original-key.pem" \
  -e "certificate_chain_path=/path/to/original-cert.pem"
```

---

## Part 7: Test Idempotency via GUI

### Step 1: Get Current Certificate Fingerprint

1. Navigate to VDC Certificate section in GUI
2. Note the current fingerprint: `ABC123...`

### Step 2: Run Module with Same Certificate

```bash
# Get the current certificate and re-apply it
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  | grep fingerprint
```

### Step 3: Re-apply Same Certificate

```bash
# Run update module with the same certificate
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "private_key_path=/path/to/current-key.pem" \
  -e "certificate_chain_path=/path/to/current-cert.pem"
```

**Expected Output**:
```yaml
changed: false  # No change because it's the same certificate
```

### Step 4: Verify in GUI

1. Refresh the ObjectScale GUI
2. Check the VDC Certificate fingerprint
3. **It should be the same**: `ABC123...`
4. **No change should have occurred**

---

## Part 8: Monitor Certificate Expiry in GUI

### Step 1: Check Expiry Date in GUI

1. Navigate to VDC Certificate section
2. Look for **Valid Until** or **Expires** field
3. Note the expiry date: `2027-01-15`

### Step 2: Run Info Module and Compare

```bash
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"
```

**Expected Output**:
```yaml
vdc_certificate_details:
  not_after: "2027-01-15T00:00:00"  # Should match GUI
```

### Step 3: Verify Match

- GUI Expiry: `2027-01-15`
- Module Output: `2027-01-15T00:00:00`
- **They should match** (same date)

### Step 4: Set Renewal Reminder

If certificate expires soon:
1. Note the expiry date
2. Set a calendar reminder (30 days before)
3. Plan certificate renewal before expiry

---

## Part 9: Security Verification in GUI

### Check 1: Verify Private Key Not Visible

1. In ObjectScale GUI, navigate to certificate details
2. Look for any field showing private key content
3. **Private key should NEVER be visible**
4. Only public certificate chain should be shown

### Check 2: Verify Certificate Chain Display

1. In certificate details, look for **Certificate Chain** section
2. You should see:
   - Leaf certificate (your certificate)
   - Intermediate certificates (if any)
   - Root certificate (if included)
3. **Each certificate should show**: Subject, Issuer, Expiry

### Check 3: Verify Fingerprint Consistency

1. Get fingerprint from GUI
2. Run info module and get fingerprint
3. **They must match exactly**
4. If they don't match, something is wrong

---

## Part 10: Troubleshooting GUI Issues

### Issue: Certificate Section Not Found

**Solution**:
1. Try different paths (see Part 2)
2. Use search function to find "Certificate"
3. Check ObjectScale 4.3 documentation for your version
4. Contact ObjectScale support if still not found

### Issue: Fingerprint Doesn't Match

**Possible Causes**:
1. GUI shows different hash algorithm (SHA-1 vs SHA-256)
2. GUI not refreshed after module update
3. Different certificate selected

**Solution**:
1. Check hash algorithm in GUI (should be SHA-256)
2. Hard refresh browser (Ctrl+Shift+Delete)
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

### Issue: Cannot Access GUI

**Solution**:
1. Verify ObjectScale is running: `curl -k https://10.0.0.100:4443`
2. Verify credentials are correct
3. Check network connectivity
4. Try different browser

---

## Part 11: GUI Testing Checklist

### Pre-Testing
- [ ] ObjectScale 4.3 is running
- [ ] You have admin credentials
- [ ] Browser can access management UI
- [ ] Modules are deployed in Ansible

### VDC Certificate Testing
- [ ] Can locate VDC Certificate section in GUI
- [ ] Can view VDC certificate details
- [ ] Can copy fingerprint from GUI
- [ ] Module output matches GUI fingerprint
- [ ] Module output matches GUI subject
- [ ] Module output matches GUI expiry date

### Object-cert Certificate Testing
- [ ] Can locate Object-cert Certificate section in GUI
- [ ] Can view Object-cert certificate details
- [ ] Can copy fingerprint from GUI
- [ ] Module output matches GUI fingerprint
- [ ] Module output matches GUI subject
- [ ] Module output matches GUI expiry date

### Update Testing
- [ ] Can run module in check mode
- [ ] GUI shows no change after check mode
- [ ] Can run module with actual update
- [ ] GUI shows change after actual update
- [ ] Can restore original certificate

### Idempotency Testing
- [ ] First run shows `changed: true` or `changed: false` (as expected)
- [ ] Second run shows `changed: false`
- [ ] GUI shows no change on second run

### Security Testing
- [ ] Private key never visible in GUI
- [ ] Private key never visible in module output
- [ ] Fingerprints match exactly
- [ ] Certificate chain properly displayed

---

## Part 12: Comparison Table Template

Create this table to document your testing:

| Detail | GUI Value | Module Output | Match? | Notes |
|--------|-----------|---------------|--------|-------|
| Fingerprint | | | | |
| Subject | | | | |
| Issuer | | | | |
| Valid From | | | | |
| Valid Until | | | | |
| Chain Length | | | | |
| Serial Number | | | | |

---

## Part 13: Next Steps

1. **Access ObjectScale 4.3 GUI**
   - Navigate to `https://<ip>:4443`
   - Login with admin credentials

2. **Locate Certificate Sections**
   - Find VDC Certificate
   - Find Object-cert Certificate

3. **Run Info Modules**
   - Execute vdc_certificate_info
   - Execute vdc_certificate_chain_info

4. **Compare Outputs**
   - Create comparison table
   - Verify fingerprints match
   - Verify subjects match
   - Verify expiry dates match

5. **Test Updates (Optional)**
   - Prepare test certificates
   - Run in check mode first
   - Verify no change in GUI
   - Run actual update
   - Verify change in GUI
   - Restore original

6. **Document Results**
   - Save screenshots
   - Fill in comparison table
   - Note any issues
   - Update JIRA with results

---

## Part 14: ObjectScale 4.3 Specific Notes

### GUI Differences by Version

**ObjectScale 4.3.0 - 4.3.2**:
- Certificate settings may be under **Settings → Security**
- May require admin role

**ObjectScale 4.3.3+**:
- Certificate settings may be under **Administration → Certificates**
- May have additional certificate options

### API Endpoints Used

The modules use these ObjectScale 4.3 API endpoints:
- `GET /vdc/keystore` — Query VDC certificate
- `PUT /vdc/keystore` — Update VDC certificate
- `GET /object-cert/keystore` — Query Object-cert certificate
- `PUT /object-cert/keystore` — Update Object-cert certificate

### Supported Certificate Formats

- **PEM format** (required)
- **RSA private keys** (2048-bit or higher)
- **X.509 certificates**
- **Certificate chains** (multiple certificates)

---

## Support

For issues or questions:
1. Check ObjectScale 4.3 documentation
2. Review module documentation in `docs/modules/`
3. Check test code for examples
4. Review example playbooks in `playbooks/modules/`

---

**Happy testing in ObjectScale 4.3! 🎉**
