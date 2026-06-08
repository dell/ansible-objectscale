#!/bin/bash

# ObjectScale 4.3 CLI Testing Simulation
# This script simulates objctl functionality using curl commands
# to test the VDC Keystore modules

# Configuration
OBJECTSCALE_HOST="10.225.110.252"
OBJECTSCALE_PORT="4443"
OBJECTSCALE_USERNAME="admin1"
OBJECTSCALE_PASSWORD="ChangeMe"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ObjectScale 4.3 CLI Testing Simulation ===${NC}"
echo -e "${BLUE}Host: $OBJECTSCALE_HOST:$OBJECTSCALE_PORT${NC}"
echo -e "${BLUE}Username: $OBJECTSCALE_USERNAME${NC}"
echo ""

# Function to make authenticated curl request
function objctl_curl() {
    local endpoint="$1"
    local method="${2:-GET}"
    
    echo -e "${YELLOW}Request: $method $endpoint${NC}"
    
    response=$(curl -k -s -u "$OBJECTSCALE_USERNAME:$OBJECTSCALE_PASSWORD" \
        -X "$method" \
        -H "Content-Type: application/json" \
        "https://$OBJECTSCALE_HOST:$OBJECTSCALE_PORT$endpoint" 2>/dev/null)
    
    echo "$response"
}

# Function to extract certificate fingerprint
function extract_fingerprint() {
    local cert_content="$1"
    
    if command -v openssl >/dev/null 2>&1; then
        echo "$cert_content" | openssl x509 -noout -fingerprint -sha256 2>/dev/null | cut -d'=' -f2
    else
        echo "openssl not available"
    fi
}

# Function to extract certificate subject
function extract_subject() {
    local cert_content="$1"
    
    if command -v openssl >/dev/null 2>&1; then
        echo "$cert_content" | openssl x509 -noout -subject 2>/dev/null | sed 's/subject=//'
    else
        echo "openssl not available"
    fi
}

# Function to extract certificate expiry
function extract_expiry() {
    local cert_content="$1"
    
    if command -v openssl >/dev/null 2>&1; then
        echo "$cert_content" | openssl x509 -noout -dates 2>/dev/null | grep "notAfter" | cut -d'=' -f2
    else
        echo "openssl not available"
    fi
}

# Test 1: Try to find VDC certificate endpoint
echo -e "${GREEN}=== Test 1: Finding VDC Certificate Endpoint ===${NC}"

# Try different possible endpoints
endpoints=(
    "/api/v1/vdc/keystore"
    "/api/v1/vdc/certificate"
    "/api/v1/keystore/vdc"
    "/api/vdc/keystore"
    "/keystore/vdc"
    "/vdc/keystore"
)

vdc_endpoint=""
for endpoint in "${endpoints[@]}"; do
    echo -e "${YELLOW}Trying: $endpoint${NC}"
    response=$(objctl_curl "$endpoint")
    
    if [[ "$response" != *"Not Found"* ]] && [[ "$response" != *"Error"* ]]; then
        echo -e "${GREEN}Found VDC endpoint: $endpoint${NC}"
        vdc_endpoint="$endpoint"
        break
    fi
done

if [[ -z "$vdc_endpoint" ]]; then
    echo -e "${RED}Could not find VDC certificate endpoint${NC}"
else
    echo -e "${GREEN}VDC Certificate Response:${NC}"
    echo "$response" | head -10
fi

# Test 2: Try to find Object-cert certificate endpoint
echo ""
echo -e "${GREEN}=== Test 2: Finding Object-cert Certificate Endpoint ===${NC}"

obj_endpoints=(
    "/api/v1/object-cert/keystore"
    "/api/v1/object-cert/certificate"
    "/api/v1/keystore/object-cert"
    "/api/v1/object/keystore"
    "/api/object-cert/keystore"
    "/object-cert/keystore"
    "/object/keystore"
)

obj_endpoint=""
for endpoint in "${obj_endpoints[@]}"; do
    echo -e "${YELLOW}Trying: $endpoint${NC}"
    response=$(objctl_curl "$endpoint")
    
    if [[ "$response" != *"Not Found"* ]] && [[ "$response" != *"Error"* ]]; then
        echo -e "${GREEN}Found Object-cert endpoint: $endpoint${NC}"
        obj_endpoint="$endpoint"
        break
    fi
done

if [[ -z "$obj_endpoint" ]]; then
    echo -e "${RED}Could not find Object-cert certificate endpoint${NC}"
else
    echo -e "${GREEN}Object-cert Certificate Response:${NC}"
    echo "$response" | head -10
fi

# Test 3: Run Ansible modules for comparison
echo ""
echo -e "${GREEN}=== Test 3: Running Ansible Modules ===${NC}"

echo -e "${YELLOW}Running vdc_certificate_info module...${NC}"
cd /usr/shrinidhirao/collections/ansible_collections/dellemc/objectscale

ansible_output=$(ansible-playbook playbooks/modules/vdc_certificate_info.yml \
    -e "objectscale_host=$OBJECTSCALE_HOST" \
    -e "objectscale_username=$OBJECTSCALE_USERNAME" \
    -e "objectscale_password=$OBJECTSCALE_PASSWORD" \
    -e "validate_certs=false" 2>&1)

echo "$ansible_output" | grep -A 20 "vdc_certificate_details"

echo ""
echo -e "${YELLOW}Running vdc_certificate_chain_info module...${NC}"

ansible_chain_output=$(ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml \
    -e "objectscale_host=$OBJECTSCALE_HOST" \
    -e "objectscale_username=$OBJECTSCALE_USERNAME" \
    -e "objectscale_password=$OBJECTSCALE_PASSWORD" \
    -e "validate_certs=false" 2>&1)

echo "$ansible_chain_output" | grep -A 20 "vdc_certificate_chain_details"

# Test 4: Extract and compare information
echo ""
echo -e "${GREEN}=== Test 4: Information Comparison ===${NC}"

# Extract Ansible fingerprints
vdc_fingerprint=$(echo "$ansible_output" | grep -oP 'fingerprint.*?:\s*\K[^ ]+' | head -1)
obj_fingerprint=$(echo "$ansible_chain_output" | grep -oP 'fingerprint.*?:\s*\K[^ ]+' | head -1)

echo -e "${BLUE}VDC Certificate Fingerprint: $vdc_fingerprint${NC}"
echo -e "${BLUE}Object-cert Certificate Fingerprint: $obj_fingerprint${NC}"

# Extract subjects
vdc_subject=$(echo "$ansible_output" | grep -oP 'leaf_subject.*?:\s*\K[^ ]+' | head -1)
obj_subject=$(echo "$ansible_chain_output" | grep -oP 'leaf_subject.*?:\s*\K[^ ]+' | head -1)

echo -e "${BLUE}VDC Certificate Subject: $vdc_subject${NC}"
echo -e "${BLUE}Object-cert Certificate Subject: $obj_subject${NC}"

# Test 5: Summary
echo ""
echo -e "${GREEN}=== Test 5: Summary ===${NC}"

if [[ -n "$vdc_fingerprint" ]]; then
    echo -e "${GREEN}✓ VDC Certificate Info module working${NC}"
else
    echo -e "${RED}✗ VDC Certificate Info module failed${NC}"
fi

if [[ -n "$obj_fingerprint" ]]; then
    echo -e "${GREEN}✓ Object-cert Certificate Info module working${NC}"
else
    echo -e "${RED}✗ Object-cert Certificate Info module failed${NC}"
fi

if [[ -n "$vdc_endpoint" ]]; then
    echo -e "${GREEN}✓ Found VDC endpoint: $vdc_endpoint${NC}"
else
    echo -e "${RED}✗ Could not find VDC endpoint${NC}"
fi

if [[ -n "$obj_endpoint" ]]; then
    echo -e "${GREEN}✓ Found Object-cert endpoint: $obj_endpoint${NC}"
else
    echo -e "${RED}✗ Could not find Object-cert endpoint${NC}"
fi

echo ""
echo -e "${BLUE}=== Testing Complete ===${NC}"
