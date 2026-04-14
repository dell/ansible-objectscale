# -*- coding: utf-8 -*-
# Ensure the collection root is importable as ansible_collections.*
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys
import pytest

# Walk up from the repo root to the collections ancestor so that
# 'ansible_collections.dellemc.objectscale' is importable.
_repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
_collections_root = os.path.dirname(os.path.dirname(_repo))
sys.path.insert(0, _collections_root)

# Skip the entire module-level test directory when the generated
# ObjectScale client cannot be imported (e.g. Python < 3.9 without
# pydantic).  The client uses modern typing constructs that cause
# SyntaxError / ImportError on older interpreters.
try:
    import ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client  # noqa: F401  pylint: disable=unused-import
except Exception:
    pytest.skip(
        "objectscale_client is not importable on this Python",
        allow_module_level=True,
    )
