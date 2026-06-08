# Testing VDC Keystore Modules with ObjectScale 4.3 CLI (objctl)

Complete guide for testing the four VDC Keystore modules using ObjectScale 4.3 command-line interface (objctl).

---

## Prerequisites

- ObjectScale 4.3 cluster running and accessible
- `objctl` CLI tool installed and configured
- Admin credentials for ObjectScale
- Access to ObjectScale management node or remote access configured
- Modules deployed in Ansible collection

---

## Part 1: Setup objctl CLI

### Step 1: Verify objctl Installation

```bash
# Check if objctl is installed
objctl version

# Expected output:
# objctl version 4.3.x
# API version: v1
```

### Step 2: Configure objctl Connection

```bash
# Set ObjectScale management endpoint
export OBJECTSCALE_HOST="10.0.0.100"
export OBJECTSCALE_PORT="4443"
export OBJECTSCALE_USERNAME="admin"
export OBJECTSCALE_PASSWORD="your_password"

# Or configure via config file
objctl config set host 10.0.0.100
objctl config set port 4443
objctl config set username admin
objctl config set password your_password
```

### Step 3: Verify Connection

```bash
# Test connection to ObjectScale
objctl vdc info

# Expected output:
# VDC Information:
# - Name: objectscale-vdc
# - Status: Active
# - Version: 4.3.x
```

---

## Part 2: Query VDC Certificate via objctl

### Method 1: Get VDC Certificate Details

```bash
# Query VDC certificate information
objctl certificate get vdc

# Expected output:
# VDC Certificate:
# - Subject: CN=objectscale.example.com
# - Issuer: CN=Your-CA
# - Valid From: 2024-01-15 00:00:00 UTC
# - Valid Until: 2027-01-15 00:00:00 UTC
# - Fingerprint (SHA-256): ABC123DEF456...
# - Serial Number: FF01...
# - Chain Length: 3
```

### Method 2: Get VDC Certificate in JSON Format

```bash
# Get certificate details in JSON format
objctl certificate get vdc --format json

# Expected output:
# {
#   "subject": "CN=objectscale.example.com",
#   "issuer": "CN=Your-CA",
#   "validFrom": "2024-01-15T00:00:00Z",
#   "validUntil": "2027-01-15T00:00:00Z",
#   "fingerprint": "ABC123DEF456...",
#   "serialNumber": "FF01...",
#   "chainLength": 3
# }
```

### Method 3: Extract Specific Certificate Fields

```bash
# Get only the fingerprint
objctl certificate get vdc --format json | jq '.fingerprint'
# Output: "ABC123DEF456..."

# Get only the expiry date
objctl certificate get vdc --format json | jq '.validUntil'
# Output: "2027-01-15T00:00:00Z"

# Get only the subject
objctl certificate get vdc --format json | jq '.subject'
# Output: "CN=objectscale.example.com"
```

### Method 4: Compare with Ansible Module Output

```bash
# Get VDC certificate via objctl
objctl_fingerprint=$(objctl certificate get vdc --format json | jq -r '.fingerprint')

# Get VDC certificate via Ansible module
ansible_output=$(ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -v 2>&1)

# Extract fingerprint from Ansible output
ansible_fingerprint=$(echo "$ansible_output" | grep -oP 'fingerprint.*?:\s*\K[^ ]+')

# Compare
if [ "$objctl_fingerprint" = "$ansible_fingerprint" ]; then
  echo "✓ Fingerprints match!"
else
  echo "✗ Fingerprints don't match!"
  echo "objctl: $objctl_fingerprint"
  echo "Ansible: $ansible_fingerprint"
fi
```

---

## Part 3: Query Object-cert Certificate via objctl

### Method 1: Get Object-cert Certificate Details

```bash
# Query Object-cert certificate information
objctl certificate get object-cert

# Expected output:
# Object-cert Certificate:
# - Subject: CN=s3.objectscale.example.com
# - Issuer: CN=Your-CA
# - Valid From: 2024-06-01 00:00:00 UTC
# - Valid Until: 2027-06-01 00:00:00 UTC
# - Fingerprint (SHA-256): XYZ789ABC123...
# - Serial Number: FF02...
# - Chain Length: 2
```

### Method 2: Get Object-cert Certificate in JSON Format

```bash
# Get certificate details in JSON format
objctl certificate get object-cert --format json

# Expected output:
# {
#   "subject": "CN=s3.objectscale.example.com",
#   "issuer": "CN=Your-CA",
#   "validFrom": "2024-06-01T00:00:00Z",
#   "validUntil": "2027-06-01T00:00:00Z",
#   "fingerprint": "XYZ789ABC123...",
#   "serialNumber": "FF02...",
#   "chainLength": 2
# }
```

### Method 3: Extract Specific Fields

```bash
# Get only the fingerprint
objctl certificate get object-cert --format json | jq '.fingerprint'
# Output: "XYZ789ABC123..."

# Get only the subject
objctl certificate get object-cert --format json | jq '.subject'
# Output: "CN=s3.objectscale.example.com"

# Get expiry date
objctl certificate get object-cert --format json | jq '.validUntil'
# Output: "2027-06-01T00:00:00Z"
```

### Method 4: Compare with Ansible Module Output

```bash
# Get Object-cert certificate via objctl
objctl_fingerprint=$(objctl certificate get object-cert --format json | jq -r '.fingerprint')

# Get Object-cert certificate via Ansible module
ansible_output=$(ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -v 2>&1)

# Extract fingerprint from Ansible output
ansible_fingerprint=$(echo "$ansible_output" | grep -oP 'fingerprint.*?:\s*\K[^ ]+')

# Compare
if [ "$objctl_fingerprint" = "$ansible_fingerprint" ]; then
  echo "✓ Fingerprints match!"
else
  echo "✗ Fingerprints don't match!"
fi
```

---

## Part 4: Update VDC Certificate via objctl

### Step 1: Prepare Test Certificate

```bash
# Generate a test certificate
openssl req -x509 -newkey rsa:2048 \
  -keyout /tmp/test-vdc-key.pem \
  -out /tmp/test-vdc-cert.pem \
  -days 365 -nodes \
  -subj "/CN=test-vdc.objectscale.example.com"

# View the fingerprint
openssl x509 -in /tmp/test-vdc-cert.pem -noout -fingerprint -sha256
# Output: SHA256 Fingerprint=ABC123...
```

### Step 2: Get Current VDC Certificate (Backup)

```bash
# Get current certificate and save it
objctl certificate get vdc --format pem > /tmp/backup-vdc-cert.pem

# Get current private key (if accessible)
# Note: Private key may not be retrievable via CLI for security reasons
```

### Step 3: Update VDC Certificate via objctl

```bash
# Update VDC certificate
objctl certificate set vdc \
  --key /tmp/test-vdc-key.pem \
  --cert /tmp/test-vdc-cert.pem

# Expected output:
# Certificate updated successfully
# New fingerprint: ABC123...
```

### Step 4: Verify Update via objctl

```bash
# Verify the certificate was updated
objctl certificate get vdc --format json | jq '.fingerprint'
# Output: "ABC123..."

# Verify the subject changed
objctl certificate get vdc --format json | jq '.subject'
# Output: "CN=test-vdc.objectscale.example.com"
```

### Step 5: Verify Update via Ansible Module

```bash
# Run the info module to verify
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"

# Expected output:
# vdc_certificate_details:
#   fingerprint: "ABC123..."
#   leaf_subject: "CN=test-vdc.objectscale.example.com"
```

### Step 6: Restore Original Certificate

```bash
# Get the original certificate details from backup
# Restore using objctl
objctl certificate set vdc \
  --key /path/to/original-key.pem \
  --cert /tmp/backup-vdc-cert.pem

# Verify restoration
objctl certificate get vdc --format json | jq '.fingerprint'
```

---

## Part 5: Update Object-cert Certificate via objctl

### Step 1: Prepare Test Certificate

```bash
# Generate a test certificate
openssl req -x509 -newkey rsa:2048 \
  -keyout /tmp/test-obj-cert-key.pem \
  -out /tmp/test-obj-cert-cert.pem \
  -days 365 -nodes \
  -subj "/CN=test-s3.objectscale.example.com"

# View the fingerprint
openssl x509 -in /tmp/test-obj-cert-cert.pem -noout -fingerprint -sha256
# Output: SHA256 Fingerprint=XYZ789...
```

### Step 2: Get Current Object-cert Certificate (Backup)

```bash
# Get current certificate and save it
objctl certificate get object-cert --format pem > /tmp/backup-obj-cert.pem
```

### Step 3: Update Object-cert Certificate via objctl

```bash
# Update Object-cert certificate
objctl certificate set object-cert \
  --key /tmp/test-obj-cert-key.pem \
  --cert /tmp/test-obj-cert-cert.pem

# Expected output:
# Certificate updated successfully
# New fingerprint: XYZ789...
```

### Step 4: Verify Update via objctl

```bash
# Verify the certificate was updated
objctl certificate get object-cert --format json | jq '.fingerprint'
# Output: "XYZ789..."

# Verify the subject changed
objctl certificate get object-cert --format json | jq '.subject'
# Output: "CN=test-s3.objectscale.example.com"
```

### Step 5: Verify Update via Ansible Module

```bash
# Run the info module to verify
ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password"

# Expected output:
# vdc_certificate_chain_details:
#   fingerprint: "XYZ789..."
#   leaf_subject: "CN=test-s3.objectscale.example.com"
```

### Step 6: Restore Original Certificate

```bash
# Restore using objctl
objctl certificate set object-cert \
  --key /path/to/original-key.pem \
  --cert /tmp/backup-obj-cert.pem

# Verify restoration
objctl certificate get object-cert --format json | jq '.fingerprint'
```

---

## Part 6: Test Idempotency via objctl

### Step 1: Get Current Certificate Fingerprint

```bash
# Get current VDC certificate fingerprint
current_fp=$(objctl certificate get vdc --format json | jq -r '.fingerprint')
echo "Current fingerprint: $current_fp"
```

### Step 2: Run Ansible Module with Same Certificate

```bash
# Get current certificate
objctl certificate get vdc --format pem > /tmp/current-vdc-cert.pem

# Run Ansible module with same certificate
ansible-playbook playbooks/modules/vdc_certificate.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -e "certificate_chain_content=$(cat /tmp/current-vdc-cert.pem)"
```

### Step 3: Verify Idempotency

```bash
# Expected output: changed=false

# Verify fingerprint didn't change
new_fp=$(objctl certificate get vdc --format json | jq -r '.fingerprint')

if [ "$current_fp" = "$new_fp" ]; then
  echo "✓ Idempotency verified - fingerprint unchanged"
else
  echo "✗ Idempotency failed - fingerprint changed"
fi
```

---

## Part 7: Monitor Certificate Expiry via objctl

### Step 1: Get Expiry Date

```bash
# Get VDC certificate expiry date
objctl certificate get vdc --format json | jq '.validUntil'
# Output: "2027-01-15T00:00:00Z"

# Get Object-cert certificate expiry date
objctl certificate get object-cert --format json | jq '.validUntil'
# Output: "2027-06-01T00:00:00Z"
```

### Step 2: Check Days Until Expiry

```bash
# Calculate days until expiry for VDC certificate
expiry_date=$(objctl certificate get vdc --format json | jq -r '.validUntil')
expiry_epoch=$(date -d "$expiry_date" +%s)
current_epoch=$(date +%s)
days_left=$(( ($expiry_epoch - $current_epoch) / 86400 ))

echo "Days until VDC certificate expires: $days_left"

# Alert if expiring soon
if [ $days_left -lt 30 ]; then
  echo "⚠️ WARNING: Certificate expires in less than 30 days!"
fi
```

### Step 3: Set Renewal Reminder

```bash
# Create a cron job to check certificate expiry daily
cat > /tmp/check-cert-expiry.sh << 'EOF'
#!/bin/bash
EXPIRY=$(objctl certificate get vdc --format json | jq -r '.validUntil')
DAYS_LEFT=$(( ($(date -d "$EXPIRY" +%s) - $(date +%s)) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
  echo "Certificate expires in $DAYS_LEFT days" | mail -s "Certificate Expiry Alert" admin@example.com
fi
EOF

chmod +x /tmp/check-cert-expiry.sh

# Add to crontab
# 0 8 * * * /tmp/check-cert-expiry.sh
```

---

## Part 8: Compare objctl and Ansible Module Outputs

### Create Comparison Script

```bash
#!/bin/bash
# Script to compare objctl and Ansible module outputs

echo "=== VDC Certificate Comparison ==="

# Get via objctl
echo "Getting VDC certificate via objctl..."
objctl_vdc=$(objctl certificate get vdc --format json)

# Get via Ansible
echo "Getting VDC certificate via Ansible..."
ansible_vdc=$(ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" \
  -v 2>&1 | grep -A 10 "vdc_certificate_details")

# Extract and compare fingerprints
objctl_fp=$(echo "$objctl_vdc" | jq -r '.fingerprint')
ansible_fp=$(echo "$ansible_vdc" | grep -oP 'fingerprint.*?:\s*\K[^ ]+')

echo "objctl fingerprint:   $objctl_fp"
echo "Ansible fingerprint:  $ansible_fp"

if [ "$objctl_fp" = "$ansible_fp" ]; then
  echo "✓ Fingerprints match!"
else
  echo "✗ Fingerprints don't match!"
fi

# Compare subjects
objctl_subject=$(echo "$objctl_vdc" | jq -r '.subject')
ansible_subject=$(echo "$ansible_vdc" | grep -oP 'leaf_subject.*?:\s*\K[^ ]+')

echo "objctl subject:   $objctl_subject"
echo "Ansible subject:  $ansible_subject"

if [ "$objctl_subject" = "$ansible_subject" ]; then
  echo "✓ Subjects match!"
else
  echo "✗ Subjects don't match!"
fi

echo ""
echo "=== Object-cert Certificate Comparison ==="

# Similar comparison for Object-cert certificate
objctl_obj=$(objctl certificate get object-cert --format json)
objctl_obj_fp=$(echo "$objctl_obj" | jq -r '.fingerprint')

echo "objctl fingerprint: $objctl_obj_fp"
# ... continue with Ansible comparison
```

---

## Part 9: Batch Certificate Management via objctl

### Update Multiple Certificates

```bash
#!/bin/bash
# Script to update both certificates

echo "Updating VDC certificate..."
objctl certificate set vdc \
  --key /tmp/new-vdc-key.pem \
  --cert /tmp/new-vdc-cert.pem

echo "Updating Object-cert certificate..."
objctl certificate set object-cert \
  --key /tmp/new-obj-cert-key.pem \
  --cert /tmp/new-obj-cert-cert.pem

echo "Verifying updates..."
echo "VDC fingerprint: $(objctl certificate get vdc --format json | jq -r '.fingerprint')"
echo "Object-cert fingerprint: $(objctl certificate get object-cert --format json | jq -r '.fingerprint')"
```

---

## Part 10: objctl CLI Testing Checklist

### Pre-Testing
- [ ] objctl is installed and accessible
- [ ] Connection to ObjectScale is configured
- [ ] Can run `objctl vdc info` successfully
- [ ] Have admin credentials
- [ ] Modules are deployed in Ansible

### VDC Certificate Testing
- [ ] Can query VDC certificate via `objctl certificate get vdc`
- [ ] Can get JSON format output
- [ ] Can extract fingerprint via jq
- [ ] Can extract subject via jq
- [ ] Can extract expiry date via jq
- [ ] Fingerprint matches Ansible module output
- [ ] Subject matches Ansible module output
- [ ] Expiry date matches Ansible module output

### Object-cert Certificate Testing
- [ ] Can query Object-cert certificate via `objctl certificate get object-cert`
- [ ] Can get JSON format output
- [ ] Can extract fingerprint via jq
- [ ] Can extract subject via jq
- [ ] Can extract expiry date via jq
- [ ] Fingerprint matches Ansible module output
- [ ] Subject matches Ansible module output
- [ ] Expiry date matches Ansible module output

### Update Testing
- [ ] Can backup current certificate
- [ ] Can update certificate via `objctl certificate set`
- [ ] Can verify update via `objctl certificate get`
- [ ] Can verify update via Ansible module
- [ ] Can restore original certificate

### Idempotency Testing
- [ ] Can get current certificate fingerprint
- [ ] Can re-apply same certificate via Ansible
- [ ] Ansible module returns `changed=false`
- [ ] Fingerprint remains unchanged

### Expiry Monitoring
- [ ] Can extract expiry date via objctl
- [ ] Can calculate days until expiry
- [ ] Can set up expiry alerts

---

## Part 11: Useful objctl Commands

### Certificate Query Commands

```bash
# Get VDC certificate
objctl certificate get vdc

# Get Object-cert certificate
objctl certificate get object-cert

# Get in JSON format
objctl certificate get vdc --format json

# Get in PEM format
objctl certificate get vdc --format pem

# Get specific fields
objctl certificate get vdc --format json | jq '.fingerprint'
objctl certificate get vdc --format json | jq '.subject'
objctl certificate get vdc --format json | jq '.validUntil'
```

### Certificate Update Commands

```bash
# Update VDC certificate
objctl certificate set vdc --key key.pem --cert cert.pem

# Update Object-cert certificate
objctl certificate set object-cert --key key.pem --cert cert.pem

# Update with validation
objctl certificate set vdc --key key.pem --cert cert.pem --validate
```

### Certificate Verification Commands

```bash
# Verify certificate format
openssl x509 -in cert.pem -text -noout

# Verify certificate fingerprint
openssl x509 -in cert.pem -noout -fingerprint -sha256

# Verify certificate expiry
openssl x509 -in cert.pem -noout -dates

# Verify certificate chain
openssl verify -CAfile ca.pem cert.pem
```

---

## Part 12: Troubleshooting objctl Issues

### Issue: objctl command not found

```bash
# Solution: Add to PATH
export PATH=$PATH:/path/to/objctl/bin

# Or install objctl
# Follow ObjectScale 4.3 installation guide
```

### Issue: Connection refused

```bash
# Verify ObjectScale is running
objctl vdc info

# Check network connectivity
ping 10.0.0.100
telnet 10.0.0.100 4443

# Verify credentials
objctl config get username
objctl config get host
```

### Issue: Authentication failed

```bash
# Verify credentials
objctl config set username admin
objctl config set password your_password

# Test connection
objctl vdc info
```

### Issue: Certificate command not found

```bash
# Check objctl version
objctl version

# Verify certificate commands are available
objctl certificate --help

# Update objctl if needed
# Follow ObjectScale 4.3 upgrade guide
```

---

## Part 13: Integration with Ansible

### Run Ansible Module and Verify with objctl

```bash
#!/bin/bash
# Script to run Ansible module and verify with objctl

echo "Running Ansible module..."
ansible-playbook playbooks/modules/vdc_certificate_info.yml \
  -e "objectscale_host=10.0.0.100" \
  -e "objectscale_username=admin" \
  -e "objectscale_password=password" > /tmp/ansible_output.txt

echo "Getting certificate via objctl..."
objctl certificate get vdc --format json > /tmp/objctl_output.json

echo "Comparing outputs..."
ansible_fp=$(grep -oP 'fingerprint.*?:\s*\K[^ ]+' /tmp/ansible_output.txt)
objctl_fp=$(jq -r '.fingerprint' /tmp/objctl_output.json)

if [ "$ansible_fp" = "$objctl_fp" ]; then
  echo "✓ Outputs match!"
else
  echo "✗ Outputs don't match!"
  echo "Ansible: $ansible_fp"
  echo "objctl: $objctl_fp"
fi
```

---

## Part 14: Next Steps

1. **Install and configure objctl**
   - Verify installation
   - Configure connection to ObjectScale

2. **Query certificates via objctl**
   - Get VDC certificate details
   - Get Object-cert certificate details
   - Extract specific fields

3. **Run Ansible modules**
   - Execute vdc_certificate_info
   - Execute vdc_certificate_chain_info

4. **Compare outputs**
   - Verify fingerprints match
   - Verify subjects match
   - Verify expiry dates match

5. **Test updates (Optional)**
   - Backup current certificates
   - Update via objctl
   - Verify via Ansible module
   - Restore original

6. **Monitor expiry**
   - Check expiry dates
   - Set up alerts
   - Plan renewals

---

## Support

For issues or questions:
1. Check ObjectScale 4.3 CLI documentation
2. Review module documentation in `docs/modules/`
3. Check test code for examples
4. Review example playbooks in `playbooks/modules/`

---

**Happy testing with ObjectScale 4.3 CLI! 🎉**
