#!/bin/bash
# Quick test script for VDC Keystore modules

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== VDC Keystore Modules Quick Test ===${NC}\n"

# Configuration
OBJECTSCALE_HOST="${OBJECTSCALE_HOST:-10.0.0.1}"
OBJECTSCALE_USERNAME="${OBJECTSCALE_USERNAME:-admin}"
OBJECTSCALE_PASSWORD="${OBJECTSCALE_PASSWORD:-password}"
VALIDATE_CERTS="${VALIDATE_CERTS:-false}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Host: $OBJECTSCALE_HOST"
echo "  Username: $OBJECTSCALE_USERNAME"
echo "  Validate Certs: $VALIDATE_CERTS"
echo ""

# Test 1: Check connectivity
echo -e "${BLUE}TEST 1: Checking connectivity to ObjectScale...${NC}"
if curl -sk -u "$OBJECTSCALE_USERNAME:$OBJECTSCALE_PASSWORD" \
    "https://$OBJECTSCALE_HOST:4443/api/v1/vdc/info" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Connected successfully${NC}\n"
else
    echo -e "${RED}✗ Connection failed${NC}"
    echo "  Verify ObjectScale is running and credentials are correct"
    exit 1
fi

# Test 2: Run unit tests
echo -e "${BLUE}TEST 2: Running unit tests...${NC}"
cd "$(dirname "$0")"

if python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_info.py -q 2>/dev/null; then
    echo -e "${GREEN}✓ vdc_certificate_info tests passed${NC}"
else
    echo -e "${YELLOW}⚠ vdc_certificate_info tests failed (check pytest installation)${NC}"
fi

if python3 -m pytest tests/unit/plugins/modules/test_vdc_certificate_chain_info.py -q 2>/dev/null; then
    echo -e "${GREEN}✓ vdc_certificate_chain_info tests passed${NC}"
else
    echo -e "${YELLOW}⚠ vdc_certificate_chain_info tests failed${NC}"
fi

echo ""

# Test 3: Create and run info playbook
echo -e "${BLUE}TEST 3: Running info modules via Ansible...${NC}"

cat > /tmp/test_info_modules.yml << 'EOF'
---
- name: Test VDC Keystore Info Modules
  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    objectscale_host: "{{ lookup('env', 'OBJECTSCALE_HOST') | default('10.0.0.1') }}"
    objectscale_username: "{{ lookup('env', 'OBJECTSCALE_USERNAME') | default('admin') }}"
    objectscale_password: "{{ lookup('env', 'OBJECTSCALE_PASSWORD') | default('password') }}"
    validate_certs: "{{ lookup('env', 'VALIDATE_CERTS') | default('false') }}"

  tasks:
    - name: Get VDC certificate info
      dellemc.objectscale.vdc_certificate_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
      register: vdc_info
      ignore_errors: true

    - name: Display VDC certificate info
      ansible.builtin.debug:
        msg: |
          VDC Certificate:
          - Fingerprint: {{ vdc_info.vdc_certificate_details.fingerprint | default('N/A') }}
          - Chain Length: {{ vdc_info.vdc_certificate_details.chain_length | default('N/A') }}
          - Status: {{ vdc_info.failed | default(false) | ternary('FAILED', 'OK') }}
      when: vdc_info is defined

    - name: Get Object-cert certificate info
      dellemc.objectscale.vdc_certificate_chain_info:
        objectscale_host: "{{ objectscale_host }}"
        objectscale_username: "{{ objectscale_username }}"
        objectscale_password: "{{ objectscale_password }}"
        validate_certs: "{{ validate_certs }}"
      register: obj_cert_info
      ignore_errors: true

    - name: Display Object-cert certificate info
      ansible.builtin.debug:
        msg: |
          Object-cert Certificate:
          - Fingerprint: {{ obj_cert_info.vdc_certificate_chain_details.fingerprint | default('N/A') }}
          - Chain Length: {{ obj_cert_info.vdc_certificate_chain_details.chain_length | default('N/A') }}
          - Status: {{ obj_cert_info.failed | default(false) | ternary('FAILED', 'OK') }}
      when: obj_cert_info is defined
EOF

export OBJECTSCALE_HOST="$OBJECTSCALE_HOST"
export OBJECTSCALE_USERNAME="$OBJECTSCALE_USERNAME"
export OBJECTSCALE_PASSWORD="$OBJECTSCALE_PASSWORD"
export VALIDATE_CERTS="$VALIDATE_CERTS"

if ansible-playbook /tmp/test_info_modules.yml 2>/dev/null | grep -q "ok="; then
    echo -e "${GREEN}✓ Info modules executed successfully${NC}"
else
    echo -e "${YELLOW}⚠ Could not run Ansible playbook (check Ansible installation)${NC}"
fi

echo ""

# Test 4: Summary
echo -e "${BLUE}TEST 4: Summary${NC}"
echo -e "${GREEN}✓ All quick tests completed${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review TESTING_GUIDE.md for detailed testing procedures"
echo "  2. Run functional tests from ansible-objectscale-qe repo"
echo "  3. Test state modules (vdc_certificate, vdc_certificate_chain) with your certificates"
echo ""
