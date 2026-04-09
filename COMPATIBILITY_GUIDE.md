# ObjectScale Ansible Collection - Python Compatibility Guide

## Overview

This document describes the process for testing and regenerating the ObjectScale client code to ensure compatibility across different Python versions, particularly focusing on Python 3.7, 3.8, and newer versions.

## Compatibility Issues Encountered

### 1. Python 3.7 Compatibility Issues

#### Missing Typing Features
Python 3.7 lacks several typing features that are used in the generated client code:

- **Literal**: Not available in Python 3.7 (added in 3.8)
- **ClassVar**: Not available in Python 3.7 (added in 3.8)  
- **TypedDict**: Not available in Python 3.7 (added in 3.8)

#### Solution
Created stub implementations in `_stubs.py`:
```python
class Literal:
    """Stub Literal for Python 3.7 compatibility."""
    def __getitem__(self, item):
        return item
    def __class_getitem__(cls, item):
        return cls
```

### 2. Python 3.8 Compatibility Issues

#### Missing typing_extensions Features
Python 3.8 doesn't have `typing_extensions` installed by default, causing import errors for:

- **NotRequired**: Not available in Python 3.8 (added in 3.11)
- **Self**: Not available in Python 3.8 (added in 3.11)
- **Annotated**: Not available in Python 3.8 (added in 3.11)

#### Solution
1. Created stub implementations in `_stubs.py`
2. Added fallback imports in affected files:
```python
try:
    from typing_extensions import NotRequired, Self
except ImportError:
    try:
        from typing import NotRequired, Self  # Python 3.11+
    except ImportError:
        pass

# Fallback for Python 3.8 where the types are still undefined
try:
    NotRequired
except NameError:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import NotRequired
```

### 3. Type Annotation Issues

#### Self in Return Type Annotations
Python 3.8 doesn't support `-> Self` in type annotations.

#### Solution
Modified `fix_sanity.py` to replace `-> Self` with `-> 'Self'`:
```python
def fix_self_type_annotations(text: str) -> str:
    """Replace Self in type annotations with a string fallback for Python 3.8."""
    text = re.sub(r'->\s*Self\b', "-> 'Self'", text)
    return text
```

## Testing Process

### 1. Local Testing with Different Python Versions

#### Prerequisites
```bash
# Install multiple Python versions using pyenv
pyenv install 3.7.17
pyenv install 3.8.20
pyenv install 3.14.3

# Install typing_extensions for Python 3.7
export PATH="/root/.pyenv/versions/3.7.17/bin:$PATH"
pip install typing_extensions==3.10.0.2
```

#### Testing Commands

**Python 3.7 (with typing_extensions):**
```bash
export PATH="/root/.pyenv/versions/3.7.17/bin:$PATH"
export ANSIBLE_COLLECTIONS_PATH=/root
python -c "import sys; sys.path.insert(0, '/root'); import ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client; print('Success')"
python -m pytest tests/unit/plugins/modules/ -q -o addopts=""
```

**Python 3.8 (without typing_extensions):**
```bash
export PATH="/root/.pyenv/versions/3.8.20/bin:$PATH"
export ANSIBLE_COLLECTIONS_PATH=/root
# Ensure typing_extensions is NOT installed
pip uninstall typing_extensions -y
python -c "import sys; sys.path.insert(0, '/root'); import ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client; print('Success')"
python -m pytest tests/unit/plugins/modules/ -q -o addopts=""
```

**Python 3.14+ (with full typing support):**
```bash
export PATH="/root/.pyenv/versions/3.14.3/bin:$PATH"
export ANSIBLE_COLLECTIONS_PATH=/root
python -c "import sys; sys.path.insert(0, '/root'); import ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client; print('Success')"
python -m pytest tests/unit/plugins/modules/ -q -o addopts=""
```

### 2. GitHub Actions Testing

The CI pipeline tests against multiple Python/Ansible combinations:
- Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- Ansible stable-2.16, stable-2.17, stable-2.18, stable-2.19, stable-2.20, devel

## Regeneration Process

### 1. Clean and Regenerate Client
```bash
make clean_client
make generate
```

### 2. The fix_sanity.py Process

The `fix_sanity.py` script automatically handles compatibility issues:

1. **Creates stubs** in `_stubs.py` for missing types
2. **Wraps imports** in try/except blocks with fallbacks
3. **Fixes type annotations** for older Python versions
4. **Handles third-party imports** (pydantic, urllib3, dateutil)

### 3. Manual Fixes Required

After regeneration, some manual fixes may be needed:

1. **Update configuration.py** imports:
   ```python
   try:
       from typing import Any, ClassVar, Dict, List, Literal, Optional, TypedDict, Union
   except ImportError:
       # Python 3.7 - some types are not available
       from typing import Any, Dict, List, Optional, Union
       from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import ClassVar, Literal, TypedDict
   ```

2. **Add fallback imports** for typing_extensions:
   ```python
   try:
       NotRequired
   except NameError:
       from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import NotRequired
   ```

## Common Issues and Solutions

### 1. "function object is not subscriptable"
**Cause**: Stub functions can't be used with `[]` syntax
**Solution**: Make stubs classes with `__getitem__` and `__class_getitem__`

### 2. "cannot import name 'X' from 'typing'"
**Cause**: Type not available in Python version
**Solution**: Add stub implementation and fallback import

### 3. pytest dependency issues on Python 3.7/3.8
**Cause**: New pytest versions require typing_extensions
**Solution**: Use older pytest version:
```bash
pip install "pytest<7"
pip uninstall pytest-cov exceptiongroup -y
```

### 4. Duplicate stub definitions
**Cause**: Regeneration overwrites _stubs.py
**Solution**: Update fix_sanity.py template to include all necessary stubs

## Best Practices

1. **Always test on Python 3.7** after changes
2. **Test without typing_extensions** on Python 3.8
3. **Check GHA logs** for all Python versions
4. **Keep stub implementations minimal** but functional
5. **Document any new typing features** added to the client

## File Locations

- **Stubs file**: `plugins/module_utils/objectscale_client/_stubs.py`
- **Fix script**: `client/clientgen_utils/fix_sanity.py`
- **Configuration**: `plugins/module_utils/objectscale_client/configuration.py`
- **API files**: `plugins/module_utils/objectscale_client/api/*.py`

## Verification Checklist

- [ ] Client imports successfully on Python 3.7
- [ ] Client imports successfully on Python 3.8 (without typing_extensions)
- [ ] Client imports successfully on Python 3.14+
- [ ] Unit tests pass on all Python versions
- [ ] GHA sanity tests pass
- [ ] GHA unit tests pass
- [ ] No lint errors
