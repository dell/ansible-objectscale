# VDC Keystore Modules Testing Guide

This guide covers testing the four VDC Keystore modules: `vdc_certificate`, `vdc_certificate_info`, `vdc_certificate_chain`, and `vdc_certificate_chain_info`.

## Prerequisites

1. **ObjectScale Cluster**: Running ObjectScale instance with management endpoint accessible
2. **Ansible**: Installed with the objectscale collection
3. **Python Libraries**:
   ```bash
   pip install pydantic urllib3 python-dateutil cryptography
   ```
4. **Credentials**: Admin access to ObjectScale management API

## Module Overview

| Module | Type | Endpoint | Purpose |
|--------|------|----------|---------|
| `vdc_certificate` | State | PUT `/vdc/keystore` | Manage VDC TLS certificate |
| `vdc_certificate_info` | Info | GET `/vdc/keystore` | Query VDC certificate |
| `vdc_certificate_chain` | State | PUT `/object-cert/keystore` | Manage Object-cert TLS certificate |
| `vdc_certificate_chain_info` | Info | GET `/object-cert/keystore` | Query Object-cert certificate |

---

## Method 1: CLI Testing with Ansible Playbooks

### Step 1: Create Test Playbook

Create `test_vdc_keystore.yml`:

```yaml
---
- name: VDC Keystore Modules Testing
  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    objectscale_host: "10.0.0.1"  # Replace with your ObjectScale IP
    objectscale_port: 4443
    objectscale_username: "admin"
    objectscale_password: "password"
    validate_certs: false
    timeout: 30

  tasks:
    # ===== VDC Certificate Info (Read-only) =====
    - name: "TEST 1: Get current VDC certificate info"
      dellemc.objectscale.vdc_certificate_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_port: "{{ objectscale_port }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
        timeout: "{{ timeout }}"
      register: vdc_cert_info

    - name: Display VDC certificate info
      ansible.builtin.debug:
        msg: |
          VDC Certificate Details:
          - Fingerprint: {{ vdc_cert_info.vdc_certificate_details.fingerprint }}
          - Chain Length: {{ vdc_cert_info.vdc_certificate_details.chain_length }}
          - Subject: {{ vdc_cert_info.vdc_certificate_details.leaf_subject | default('N/A') }}
          - Expires: {{ vdc_cert_info.vdc_certificate_details.not_after | default('N/A') }}

    # ===== Object-cert Certificate Info (Read-only) =====
    - name: "TEST 2: Get current Object-cert certificate info"
      dellemc.objectscale.vdc_certificate_chain_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_port: "{{ objectscale_port }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
        timeout: "{{ timeout }}"
      register: obj_cert_info

    - name: Display Object-cert certificate info
      ansible.builtin.debug:
        msg: |
          Object-cert Certificate Details:
          - Fingerprint: {{ obj_cert_info.vdc_certificate_chain_details.fingerprint }}
          - Chain Length: {{ obj_cert_info.vdc_certificate_chain_details.chain_length }}
          - Subject: {{ obj_cert_info.vdc_certificate_chain_details.leaf_subject | default('N/A') }}
          - Expires: {{ obj_cert_info.vdc_certificate_chain_details.not_after | default('N/A') }}

    # ===== VDC Certificate Update (State module) =====
    - name: "TEST 3: Update VDC certificate (check mode)"
      dellemc.objectscale.vdc_certificate:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_port: "{{ objectscale_port }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
        timeout: "{{ timeout }}"
        state: present
        private_key_path: /path/to/vdc-private.key
        certificate_chain_path: /path/to/vdc-chain.pem
      check_mode: true
      register: vdc_cert_update
      ignore_errors: true

    - name: Display VDC certificate update result
      ansible.builtin.debug:
        msg: |
          VDC Certificate Update (check mode):
          - Changed: {{ vdc_cert_update.changed | default('N/A') }}
          - Status: {{ vdc_cert_update.failed | default(false) | ternary('FAILED', 'OK') }}

    # ===== Object-cert Certificate Update (State module) =====
    - name: "TEST 4: Update Object-cert certificate (check mode)"
      dellemc.objectscale.vdc_certificate_chain:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_port: "{{ objectscale_port }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
        timeout: "{{ timeout }}"
        state: present
        private_key_path: /path/to/obj-cert-private.key
        certificate_chain_path: /path/to/obj-cert-chain.pem
      check_mode: true
      register: obj_cert_update
      ignore_errors: true

    - name: Display Object-cert certificate update result
      ansible.builtin.debug:
        msg: |
          Object-cert Certificate Update (check mode):
          - Changed: {{ obj_cert_update.changed | default('N/A') }}
          - Status: {{ obj_cert_update.failed | default(false) | ternary('FAILED', 'OK') }}

    # ===== Idempotency Test =====
    - name: "TEST 5: Verify idempotency (re-apply same VDC cert)"
      dellemc.objectscale.vdc_certificate:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_port: "{{ objectscale_port }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
        timeout: "{{ timeout }}"
        state: present
        private_key_content: "{{ lookup('file', '/path/to/vdc-private.key') }}"
        certificate_chain_content: "{{ vdc_cert_info.vdc_certificate_details.chain }}"
      register: vdc_idempotent
      ignore_errors: true

    - name: Display idempotency result
      ansible.builtin.debug:
        msg: |
          Idempotency Test:
          - Changed: {{ vdc_idempotent.changed | default('N/A') }}
          - Expected: false (no change when re-applying same cert)

    # ===== Diff Mode Test =====
    - name: "TEST 6: Show diff mode (no private key leak)"
      dellemc.objectscale.vdc_certificate:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_port: "{{ objectscale_port }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
        timeout: "{{ timeout }}"
        state: present
        private_key_path: /path/to/vdc-private.key
        certificate_chain_path: /path/to/vdc-chain.pem
      diff: true
      check_mode: true
      register: vdc_diff
      ignore_errors: true

    - name: Verify private key not in diff
      ansible.builtin.assert:
        that:
          - "'PRIVATE KEY' not in (vdc_diff | string)"
        fail_msg: "SECURITY ISSUE: Private key leaked in diff output!"
      when: vdc_diff.diff is defined
```

### Step 2: Run the Playbook

```bash
# Set environment variables
export OBJECTSCALE_HOST="10.0.0.1"
export OBJECTSCALE_USERNAME="admin"
export OBJECTSCALE_PASSWORD="your_password"

# Run with verbose output
ansible-playbook test_vdc_keystore.yml -vvv

# Run with extra debugging
ansible-playbook test_vdc_keystore.yml -vvv --extra-vars "validate_certs=false"
```

---

## Method 2: Direct Python Testing

Create `test_modules_direct.py`:

```python
#!/usr/bin/env python3
"""Direct Python testing of VDC Keystore modules."""

import sys
sys.path.insert(0, '/usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale')

from plugins.module_utils.vdc_keystore_api import VdcKeystoreApi, ObjectCertKeystoreApi
from plugins.module_utils import utils

# Configuration
config = {
    'host': '10.0.0.1',
    'port': 4443,
    'username': 'admin',
    'password': 'password',
    'verify_ssl': False,
}

def test_vdc_keystore_api():
    """Test VdcKeystoreApi directly."""
    print("\n=== Testing VdcKeystoreApi ===")
    try:
        # Create API client (requires objectscale_client)
        from plugins.module_utils.objectscale_client import api_client
        
        client = api_client.ApiClient(
            host=f"https://{config['host']}:{config['port']}",
            username=config['username'],
            password=config['password'],
            verify_ssl=config['verify_ssl'],
        )
        
        api = VdcKeystoreApi(client, timeout=30)
        
        # Test GET
        print("1. Getting VDC certificate chain...")
        result = api.get_certificate_chain()
        print(f"   ✓ Chain length: {len(result.get('chain', ''))} bytes")
        print(f"   ✓ Fingerprint: {result.get('fingerprint', 'N/A')}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")

def test_object_cert_keystore_api():
    """Test ObjectCertKeystoreApi directly."""
    print("\n=== Testing ObjectCertKeystoreApi ===")
    try:
        from plugins.module_utils.objectscale_client import api_client
        
        client = api_client.ApiClient(
            host=f"https://{config['host']}:{config['port']}",
            username=config['username'],
            password=config['password'],
            verify_ssl=config['verify_ssl'],
        )
        
        api = ObjectCertKeystoreApi(client, timeout=30)
        
        # Test GET
        print("1. Getting Object-cert certificate chain...")
        result = api.get_certificate_chain()
        print(f"   ✓ Chain length: {len(result.get('chain', ''))} bytes")
        print(f"   ✓ Fingerprint: {result.get('fingerprint', 'N/A')}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")

if __name__ == '__main__':
    test_vdc_keystore_api()
    test_object_cert_keystore_api()
```

Run it:
```bash
python3 test_modules_direct.py
```

---

## Method 3: ObjectScale GUI Testing

### Step 1: Access ObjectScale Management UI

1. Open browser: `https://<objectscale-ip>:4443`
2. Login with admin credentials
3. Navigate to **Settings** → **Certificates** (if available)

### Step 2: Verify Current Certificates

- Check **VDC Certificate** section
- Check **Object-cert Certificate** section (if available)
- Note the current fingerprints and expiry dates

### Step 3: Run Ansible Module and Verify

1. Run the test playbook (Method 1)
2. Refresh the GUI
3. Verify that:
   - Fingerprints match between module output and GUI
   - Expiry dates match
   - Chain lengths match

---

## Method 4: Unit Tests

Run the existing unit tests:

```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale

# Run all VDC Keystore tests
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate.py -v
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_info.py -v
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_chain.py -v
python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_chain_info.py -v
python3 -m pytest tests/unit/plugins/modules/test_vdc_keystore_api.py -v
python3 -m pytest tests/unit/plugins/modules/test_object_cert_keystore_api.py -v

# Run all together with coverage
python3 -m pytest tests/unit/plugins/modules/test_vdc*.py -v --cov=plugins/modules --cov=plugins/module_utils
```

---

## Method 5: Functional Tests (QE Repo)

Run the functional test suites:

```bash
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/ansible-objectscale-qe

# Run VDC Certificate Chain tests
ansible-playbook VDC_Certificate_Chain/pre_req.yml -e "objectscale_host=10.0.0.1" -e "objectscale_username=admin" -e "objectscale_password=password"
ansible-playbook VDC_Certificate_Chain/TC-01_set_certificate_chain_inline.yml -e "objectscale_host=10.0.0.1" -e "objectscale_username=admin" -e "objectscale_password=password"
ansible-playbook VDC_Certificate_Chain/TC-02_idempotence_no_change.yml -e "objectscale_host=10.0.0.1" -e "objectscale_username=admin" -e "objectscale_password=password"

# Run VDC Certificate Chain Info tests
ansible-playbook VDC_Certificate_Chain_Info/pre_req.yml -e "objectscale_host=10.0.0.1" -e "objectscale_username=admin" -e "objectscale_password=password"
ansible-playbook VDC_Certificate_Chain_Info/TC-01_get_certificate_chain_info.yml -e "objectscale_host=10.0.0.1" -e "objectscale_username=admin" -e "objectscale_password=password"
```

---

## Troubleshooting

### Issue: "Connection refused"
**Solution**: Verify ObjectScale endpoint is accessible
```bash
curl -k https://10.0.0.1:4443/api/v1/vdc/info
```

### Issue: "Authentication failed (401)"
**Solution**: Verify credentials
```bash
# Test with curl
curl -k -u admin:password https://10.0.0.1:4443/api/v1/vdc/info
```

### Issue: "Module not found"
**Solution**: Verify collection is installed
```bash
ansible-galaxy collection list | grep objectscale
# If not installed:
ansible-galaxy collection install dellemc.objectscale
```

### Issue: "cryptography not installed"
**Solution**: Install the library
```bash
pip install cryptography
```

---

## Expected Test Results

### Info Modules (Read-only)
- ✅ `changed` = `false` (always)
- ✅ Returns `vdc_certificate_details` or `vdc_certificate_chain_details`
- ✅ Includes `fingerprint`, `chain`, `chain_length`
- ✅ Optionally includes `leaf_subject`, `not_after`, `leaf_serial` (if cryptography available)

### State Modules (Management)
- ✅ First run: `changed` = `true` (if certificate differs)
- ✅ Second run (same cert): `changed` = `false` (idempotent)
- ✅ Check mode: `changed` = `true` (predicted) but no actual change
- ✅ Diff mode: Shows before/after fingerprints, **no private key leakage**

---

## Security Checklist

- [ ] Private key content never logged
- [ ] Private key never appears in diff output
- [ ] Credentials passed securely (no_log)
- [ ] SSL verification configurable
- [ ] Error messages don't leak sensitive data

---

## Next Steps

1. **Prepare test certificates** (if testing state modules):
   ```bash
   # Generate self-signed cert for testing
   openssl req -x509 -newkey rsa:2048 -keyout test-key.pem -out test-cert.pem -days 365 -nodes
   ```

2. **Run the test playbook** with your ObjectScale instance

3. **Verify results** match expectations above

4. **Check logs** for any errors or warnings

5. **Run unit tests** to ensure code quality
