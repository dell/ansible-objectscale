# VDC Keystore Modules — Testing Documentation Index

Complete testing documentation for the four VDC Keystore modules.

---

## 📚 Documentation Overview

### 1. **TESTING_README.md** (11 KB) — START HERE
**Purpose**: Overview and learning path  
**Audience**: Everyone  
**Time**: 5-10 minutes

- Quick start options
- Testing methods comparison
- Success criteria
- Environment setup
- Learning paths for different roles

**When to read**: First thing when starting testing

---

### 2. **TESTING_CHEATSHEET.md** (8.4 KB) — QUICK REFERENCE
**Purpose**: Quick command reference  
**Audience**: Developers, DevOps  
**Time**: 2-3 minutes

- One-liner commands
- Module matrix
- Expected outputs
- Verification checklist
- Troubleshooting quick fix

**When to use**: During testing for quick lookups

---

### 3. **TESTING_SUMMARY.md** (12 KB) — COMPREHENSIVE REFERENCE
**Purpose**: Detailed testing matrix and scenarios  
**Audience**: QA, Developers  
**Time**: 15-20 minutes

- Module testing matrix
- Testing scenarios (1-4)
- Unit test coverage details
- Functional tests overview
- Success criteria checklist

**When to read**: Planning your testing approach

---

### 4. **TESTING_GUIDE.md** (15 KB) — DETAILED PROCEDURES
**Purpose**: Step-by-step testing procedures  
**Audience**: Developers, QA, DevOps  
**Time**: 30-45 minutes

- Method 1: CLI with Ansible Playbooks
- Method 2: Direct Python Testing
- Method 3: ObjectScale GUI Testing
- Method 4: Unit Tests
- Method 5: Functional Tests (QE Repo)
- Troubleshooting section

**When to read**: When implementing specific testing methods

---

### 5. **GUI_TESTING_GUIDE.md** (9.1 KB) — OBJECTSCALE UI VERIFICATION
**Purpose**: Step-by-step GUI verification procedures  
**Audience**: Operators, QA  
**Time**: 30-40 minutes

- Access ObjectScale management UI
- Locate certificate information
- Verify module output against GUI
- Test certificate updates
- Test idempotency via GUI
- Monitor certificate expiry
- Troubleshooting GUI issues
- Security verification

**When to read**: When verifying modules against ObjectScale UI

---

### 6. **quick_test.sh** (4.7 KB) — AUTOMATED QUICK TEST
**Purpose**: Automated testing script  
**Audience**: Everyone  
**Time**: 2-5 minutes

- Checks connectivity
- Runs unit tests
- Executes info modules
- Provides summary

**When to use**: Quick validation of setup

---

## 🎯 Quick Navigation

### By Role

**👨‍💼 Manager/Lead**
1. Read TESTING_README.md (5 min)
2. Review TESTING_SUMMARY.md (10 min)
3. Check success criteria

**👨‍💻 Developer**
1. Read TESTING_README.md (5 min)
2. Read TESTING_GUIDE.md (30 min)
3. Run unit tests
4. Review test code

**🧪 QA/Tester**
1. Read TESTING_README.md (5 min)
2. Read TESTING_SUMMARY.md (15 min)
3. Read GUI_TESTING_GUIDE.md (30 min)
4. Run functional tests

**🚀 DevOps/Operator**
1. Read TESTING_CHEATSHEET.md (3 min)
2. Run quick_test.sh (2 min)
3. Follow TESTING_GUIDE.md Method 1 (15 min)
4. Verify in GUI (20 min)

### By Task

**I want to...**

- **Get started quickly**
  → Read TESTING_README.md + run quick_test.sh

- **Run unit tests**
  → See TESTING_GUIDE.md → Method 4

- **Test with Ansible**
  → See TESTING_GUIDE.md → Method 1

- **Verify in ObjectScale GUI**
  → Read GUI_TESTING_GUIDE.md

- **Run functional tests**
  → See TESTING_SUMMARY.md → Functional Tests

- **Find a command quickly**
  → Check TESTING_CHEATSHEET.md

- **Understand all testing methods**
  → Read TESTING_SUMMARY.md

- **Debug a failing test**
  → See TESTING_GUIDE.md → Troubleshooting

---

## 📋 Document Comparison

| Document | Scope | Detail Level | Best For |
|----------|-------|--------------|----------|
| TESTING_README.md | Overview | Medium | Getting started |
| TESTING_CHEATSHEET.md | Quick ref | Low | Quick lookups |
| TESTING_SUMMARY.md | Comprehensive | Medium-High | Planning |
| TESTING_GUIDE.md | Detailed | High | Implementation |
| GUI_TESTING_GUIDE.md | GUI-focused | High | GUI verification |
| quick_test.sh | Automated | N/A | Quick validation |

---

## 🚀 Recommended Reading Order

### For First-Time Users
1. TESTING_README.md (5 min)
2. quick_test.sh (2 min)
3. TESTING_CHEATSHEET.md (3 min)
4. TESTING_GUIDE.md (30 min)

### For Experienced Users
1. TESTING_CHEATSHEET.md (3 min)
2. quick_test.sh (2 min)
3. Specific section in TESTING_GUIDE.md (10-15 min)

### For GUI Verification
1. TESTING_README.md (5 min)
2. GUI_TESTING_GUIDE.md (30 min)
3. TESTING_CHEATSHEET.md (3 min)

---

## 📊 Testing Coverage

**Total Tests**: 158 (all passing)
- Unit tests: 158
- Functional tests: 15
- Code coverage: 92%

**Test Files**:
- test_vdc_certificate.py (88 tests)
- test_vdc_certificate_info.py (20 tests)
- test_vdc_certificate_chain.py (36 tests)
- test_vdc_certificate_chain_info.py (14 tests)
- test_vdc_keystore_api.py (20 tests)
- test_object_cert_keystore_api.py (20 tests)

---

## 🔗 Related Files

**Module Documentation**:
- docs/modules/vdc_certificate.rst
- docs/modules/vdc_certificate_info.rst
- docs/modules/vdc_certificate_chain.rst
- docs/modules/vdc_certificate_chain_info.rst

**Example Playbooks**:
- playbooks/modules/vdc_certificate.yml
- playbooks/modules/vdc_certificate_info.yml
- playbooks/modules/vdc_certificate_chain.yml
- playbooks/modules/vdc_certificate_chain_info.yml

**Functional Tests** (QE Repo):
- VDC_Certificate_Chain/ (10 test cases)
- VDC_Certificate_Chain_Info/ (5 test cases)

---

## ✅ Quick Checklist

Before you start:
- [ ] Read TESTING_README.md
- [ ] Understand the four modules
- [ ] Know your testing method
- [ ] Have ObjectScale access (if needed)
- [ ] Have credentials ready
- [ ] Have test certificates (if needed)

During testing:
- [ ] Follow the appropriate guide
- [ ] Verify expected outputs
- [ ] Check success criteria
- [ ] Document results

After testing:
- [ ] Review results
- [ ] Check for issues
- [ ] Update JIRA if needed
- [ ] Archive test output

---

## 🎓 Key Concepts

**Info Modules** (Read-only):
- vdc_certificate_info
- vdc_certificate_chain_info
- Always return `changed=false`
- Safe to run anytime

**State Modules** (Management):
- vdc_certificate
- vdc_certificate_chain
- Support idempotency
- Support check/diff mode

**Testing Methods**:
1. CLI with Ansible
2. Direct Python
3. ObjectScale GUI
4. Unit tests
5. Functional tests

**Safety Levels**:
- ✅ Safe: Info modules, check mode, unit tests
- ⚠️ Caution: State modules (actual changes)
- 🔒 Secure: Private keys never logged/exposed

---

## 📞 Support

For questions or issues:
1. Check the troubleshooting section in TESTING_GUIDE.md
2. Review module documentation
3. Check test code for examples
4. Review example playbooks

---

**Start with TESTING_README.md →**
