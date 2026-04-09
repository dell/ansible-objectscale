# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import pytest

sys.path.insert(0, '/root/Storage/collections')

try:
    import ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client  # noqa: F401  pylint: disable=unused-import
except Exception:
    pytest.skip(
        "objectscale_client is not importable on this Python",
        allow_module_level=True,
    )
