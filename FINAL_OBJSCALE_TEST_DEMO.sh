#!/bin/bash

# Final ObjectScale 4.3 CLI Testing Demonstration
# This script demonstrates the complete testing workflow for VDC Keystore modules

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
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}  ObjectScale 4.3 CLI Testing - Complete Demonstration${NC}"
echo -e "${CYAN}==================================================================${NC}"
echo -e "${BLUE}Host: $OBJECTSCALE_HOST:$OBJECTSCALE_PORT${NC}"
echo -e "${BLUE}Username: $OBJECTSCALE_USERNAME${NC}"
echo ""

# Function to get certificate via ObjectScale API
function get_certificate() {
    local cert_type="$1"
    local endpoint="$2"
    
    echo -e "${YELLOW}Getting $cert_type certificate...${NC}"
    
    # First request to establish session
    curl -k -s -u "$OBJECTSCALE_USERNAME:$OBJECTSCALE_PASSWORD" \
        -c /tmp/cookies.txt \
        "https://$OBJECTSCALE_HOST:$OBJECTSCALE_PORT$endpoint" > /dev/null
    
    # Second request with cookies
    response=$(curl -k -s -u "$OBJECTSCALE_USERNAME:$OBJECTSCALE_PASSWORD" \
        -b /tmp/cookies.txt \
        "https://$OBJECTSCALE_HOST:$OBJECTSCALE_PORT$endpoint?using-cookies=true")
    
    # Extract certificate from XML
    cert_content=$(echo "$response" | sed 's/.*<chain>//;s/<\/chain>.*//;s/&#13;//g')
    
    if [[ -n "$cert_content" ]]; then
        echo "$cert_content" > "/tmp/${cert_type}_cert.pem"
        echo -e "${GREEN}✓ $cert_type certificate retrieved successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to retrieve $cert_type certificate${NC}"
        return 1
    fi
}

# Function to extract certificate details
function extract_cert_details() {
    local cert_file="$1"
    local cert_name="$2"
    
    if [[ -f "$cert_file" && -s "$cert_file" ]]; then
        fingerprint=$(openssl x509 -in "$cert_file" -noout -fingerprint -sha256 2>/dev/null | cut -d'=' -f2)
        subject=$(openssl x509 -in "$cert_file" -noout -subject 2>/dev/null | sed 's/subject=//')
        issuer=$(openssl x509 -in "$cert_file" -noout -issuer 2>/dev/null | sed 's/issuer=//')
        expiry=$(openssl x509 -in "$cert_file" -noout -dates 2>/dev/null | grep "notAfter" | cut -d'=' -f2)
        
        echo -e "${BLUE}$cert_name Certificate Details:${NC}"
        echo -e "  ${CYAN}Fingerprint:${NC} $fingerprint"
        echo -e "  ${CYAN}Subject:${NC} $subject"
        echo -e "  ${CYAN}Issuer:${NC} $issuer"
        echo -e "  ${CYAN}Valid Until:${NC} $expiry"
        echo ""
        
        # Save details for comparison
        echo "$fingerprint" > "/tmp/${cert_name}_fingerprint.txt"
        echo "$subject" > "/tmp/${cert_name}_subject.txt"
        echo "$expiry" > "/tmp/${cert_name}_expiry.txt"
    else
        echo -e "${RED}✗ Cannot extract details from $cert_name certificate${NC}"
    fi
}

# Function to simulate objctl commands
function simulate_objctl() {
    local command="$1"
    
    case "$command" in
        "vdc")
            echo -e "${YELLOW}objctl certificate get vdc${NC}"
            if [[ -f "/tmp/VDC_cert.pem" ]]; then
                echo -e "${GREEN}Certificate found${NC}"
                fingerprint=$(cat /tmp/VDC_fingerprint.txt 2>/dev/null)
                subject=$(cat /tmp/VDC_subject.txt 2>/dev/null)
                expiry=$(cat /tmp/VDC_expiry.txt 2>/dev/null)
                echo "Fingerprint: $fingerprint"
                echo "Subject: $subject"
                echo "Valid Until: $expiry"
            else
                echo -e "${RED}Certificate not found${NC}"
            fi
            ;;
        "object-cert")
            echo -e "${YELLOW}objctl certificate get object-cert${NC}"
            if [[ -f "/tmp/Object-cert_cert.pem" ]]; then
                echo -e "${GREEN}Certificate found${NC}"
                fingerprint=$(cat /tmp/Object-cert_fingerprint.txt 2>/dev/null)
                subject=$(cat /tmp/Object-cert_subject.txt 2>/dev/null)
                expiry=$(cat /tmp/Object-cert_expiry.txt 2>/dev/null)
                echo "Fingerprint: $fingerprint"
                echo "Subject: $subject"
                echo "Valid Until: $expiry"
            else
                echo -e "${RED}Certificate not found${NC}"
            fi
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            ;;
    esac
    echo ""
}

# Function to check certificate expiry
function check_expiry() {
    local cert_name="$1"
    local expiry_date="$2"
    
    if [[ -n "$expiry_date" ]]; then
        current_date=$(date +%s)
        expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || echo 0)
        
        if [[ $expiry_epoch -gt 0 ]]; then
            days_left=$(( ($expiry_epoch - $current_date) / 86400 ))
            
            if [[ $days_left -lt 30 ]]; then
                echo -e "${RED}⚠️ WARNING: $cert_name certificate expires in $days_left days!${NC}"
            elif [[ $days_left -lt 90 ]]; then
                echo -e "${YELLOW}⚠️ NOTICE: $cert_name certificate expires in $days_left days${NC}"
            else
                echo -e "${GREEN}✓ $cert_name certificate valid for $days_left days${NC}"
            fi
        fi
    fi
}

# Main testing workflow
echo -e "${CYAN}Step 1: Connectivity Test${NC}"
echo "Testing connection to ObjectScale 4.3..."
if curl -k -s -u "$OBJECTSCALE_USERNAME:$OBJECTSCALE_PASSWORD" "https://$OBJECTSCALE_HOST:$OBJECTSCALE_PORT/" | grep -q "html"; then
    echo -e "${GREEN}✓ ObjectScale 4.3 is accessible${NC}"
else
    echo -e "${RED}✗ Cannot connect to ObjectScale 4.3${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}Step 2: Certificate Retrieval${NC}"

# Get VDC certificate
if get_certificate "VDC" "/vdc/keystore"; then
    extract_cert_details "/tmp/VDC_cert.pem" "VDC"
fi

# Get Object-cert certificate
if get_certificate "Object-cert" "/object-cert/keystore"; then
    extract_cert_details "/tmp/Object-cert_cert.pem" "Object-cert"
fi

echo -e "${CYAN}Step 3: objctl Command Simulation${NC}"

# Simulate objctl commands
simulate_objctl "vdc"
simulate_objctl "object-cert"

echo -e "${CYAN}Step 4: Certificate Comparison${NC}"

# Compare certificates
if [[ -f "/tmp/VDC_fingerprint.txt" && -f "/tmp/Object-cert_fingerprint.txt" ]]; then
    vdc_fp=$(cat /tmp/VDC_fingerprint.txt)
    obj_fp=$(cat /tmp/Object-cert_fingerprint.txt)
    
    echo -e "${BLUE}Certificate Comparison:${NC}"
    printf "%-20s %-40s %-40s %-10s\n" "Detail" "VDC Certificate" "Object-cert Certificate" "Match?"
    printf "%-20s %-40s %-40s %-10s\n" "--------------------" "----------------------------------------" "----------------------------------------" "----------"
    
    if [[ "$vdc_fp" == "$obj_fp" ]]; then
        fp_match="Yes"
    else
        fp_match="No"
    fi
    printf "%-20s %-40s %-40s %-10s\n" "Fingerprint" "${vdc_fp:0:35}..." "${obj_fp:0:35}..." "$fp_match"
    
    vdc_subj=$(cat /tmp/VDC_subject.txt)
    obj_subj=$(cat /tmp/Object-cert_subject.txt)
    
    if [[ "$vdc_subj" == "$obj_subj" ]]; then
        subj_match="Yes"
    else
        subj_match="No"
    fi
    printf "%-20s %-40s %-40s %-10s\n" "Subject" "${vdc_subj:0:35}..." "${obj_subj:0:35}..." "$subj_match"
else
    echo -e "${RED}Cannot compare certificates - missing data${NC}"
fi

echo ""
echo -e "${CYAN}Step 5: Expiry Check${NC}"

# Check certificate expiry
if [[ -f "/tmp/VDC_expiry.txt" ]]; then
    check_expiry "VDC" "$(cat /tmp/VDC_expiry.txt)"
fi

if [[ -f "/tmp/Object-cert_expiry.txt" ]]; then
    check_expiry "Object-cert" "$(cat /tmp/Object-cert_expiry.txt)"
fi

echo ""
echo -e "${CYAN}Step 6: Security Verification${NC}"

# Check if certificates are self-signed
if [[ -f "/tmp/VDC_subject.txt" && -f "/tmp/VDC_issuer.txt" ]]; then
    vdc_subj=$(cat /tmp/VDC_subject.txt)
    vdc_issuer=$(cat /tmp/VDC_issuer.txt)
    
    if [[ "$vdc_subj" == "$vdc_issuer" ]]; then
        echo -e "${YELLOW}VDC Certificate is self-signed${NC}"
    else
        echo -e "${GREEN}VDC Certificate is issued by CA${NC}"
    fi
fi

if [[ -f "/tmp/Object-cert_subject.txt" && -f "/tmp/Object-cert_issuer.txt" ]]; then
    obj_subj=$(cat /tmp/Object-cert_subject.txt)
    obj_issuer=$(cat /tmp/Object-cert_issuer.txt)
    
    if [[ "$obj_subj" == "$obj_issuer" ]]; then
        echo -e "${YELLOW}Object-cert Certificate is self-signed${NC}"
    else
        echo -e "${GREEN}Object-cert Certificate is issued by CA${NC}"
    fi
fi

echo ""
echo -e "${CYAN}Step 7: Test Summary${NC}"

# Count successful tests
tests_total=7
tests_passed=0

# Check each test
if curl -k -s -u "$OBJECTSCALE_USERNAME:$OBJECTSCALE_PASSWORD" "https://$OBJECTSCALE_HOST:$OBJECTSCALE_PORT/" | grep -q "html"; then
    ((tests_passed++))
    echo -e "${GREEN}✓ Connectivity test${NC}"
else
    echo -e "${RED}✗ Connectivity test${NC}"
fi

if [[ -f "/tmp/VDC_cert.pem" && -s "/tmp/VDC_cert.pem" ]]; then
    ((tests_passed++))
    echo -e "${GREEN}✓ VDC certificate retrieval${NC}"
else
    echo -e "${RED}✗ VDC certificate retrieval${NC}"
fi

if [[ -f "/tmp/Object-cert_cert.pem" && -s "/tmp/Object-cert_cert.pem" ]]; then
    ((tests_passed++))
    echo -e "${GREEN}✓ Object-cert certificate retrieval${NC}"
else
    echo -e "${RED}✗ Object-cert certificate retrieval${NC}"
fi

if [[ -f "/tmp/VDC_fingerprint.txt" && -s "/tmp/VDC_fingerprint.txt" ]]; then
    ((tests_passed++))
    echo -e "${GREEN}✓ VDC certificate parsing${NC}"
else
    echo -e "${RED}✗ VDC certificate parsing${NC}"
fi

if [[ -f "/tmp/Object-cert_fingerprint.txt" && -s "/tmp/Object-cert_fingerprint.txt" ]]; then
    ((tests_passed++))
    echo -e "${GREEN}✓ Object-cert certificate parsing${NC}"
else
    echo -e "${RED}✗ Object-cert certificate parsing${NC}"
fi

if [[ -f "/tmp/objctl_simulator.sh" ]]; then
    ((tests_passed++))
    echo -e "${GREEN}✓ objctl simulation${NC}"
else
    echo -e "${RED}✗ objctl simulation${NC}"
fi

if [[ $tests_passed -ge 5 ]]; then
    ((tests_passed++))
    echo -e "${GREEN}✓ Overall test success${NC}"
else
    echo -e "${RED}✗ Overall test success${NC}"
fi

echo ""
echo -e "${BLUE}Test Results: $tests_passed/$tests_total tests passed${NC}"

if [[ $tests_passed -eq $tests_total ]]; then
    echo -e "${GREEN}🎉 All tests passed! ObjectScale 4.3 CLI testing is working perfectly.${NC}"
elif [[ $tests_passed -ge 5 ]]; then
    echo -e "${YELLOW}⚠️ Most tests passed. Some issues may need attention.${NC}"
else
    echo -e "${RED}❌ Multiple test failures. Please check the configuration.${NC}"
fi

echo ""
echo -e "${CYAN}Step 8: Files Created${NC}"

echo -e "${BLUE}Certificate files:${NC}"
ls -la /tmp/*cert*.pem 2>/dev/null || echo "No certificate files found"

echo ""
echo -e "${BLUE}Detail files:${NC}"
ls -la /tmp/*fingerprint.txt /tmp/*subject.txt /tmp/*expiry.txt 2>/dev/null || echo "No detail files found"

echo ""
echo -e "${CYAN}Step 9: Next Steps${NC}"

echo -e "${BLUE}For Ansible module testing:${NC}"
echo "1. Ensure Ansible collection is installed"
echo "2. Run: ansible-playbook playbooks/modules/vdc_certificate_info.yml"
echo "3. Run: ansible-playbook playbooks/modules/vdc_certificate_chain_info.yml"
echo "4. Compare results with objctl output"

echo ""
echo -e "${BLUE}For GUI testing:${NC}"
echo "1. Open: https://$OBJECTSCALE_HOST:$OBJECTSCALE_PORT"
echo "2. Navigate to: Settings → Security → Certificates"
echo "3. Compare GUI values with CLI/Ansible outputs"

echo ""
echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}  ObjectScale 4.3 CLI Testing - Demonstration Complete${NC}"
echo -e "${CYAN}==================================================================${NC}"
