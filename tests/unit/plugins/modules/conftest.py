# -*- coding: utf-8 -*-
# Copyright (c) 2025 Dell Inc., or its subsidiaries. All rights reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# type: ignore  # Ignore all type checking in test files

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import pytest

sys.path.insert(0, '/root')

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
