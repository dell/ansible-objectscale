"""API response object."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from typing import Generic, Mapping, Optional, TypeVar

try:
    from pydantic import BaseModel
except ImportError:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import BaseModel  # stub
try:
    from pydantic import Field
except ImportError:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import Field  # stub
try:
    from pydantic import StrictBytes
except ImportError:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import StrictBytes  # stub
try:
    from pydantic import StrictInt
except ImportError:
    from ansible_collections.dellemc.objectscale.plugins.module_utils.objectscale_client._stubs import StrictInt  # stub

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    API response object
    """

    status_code: StrictInt = Field(description="HTTP status code")
    headers: Optional[Mapping[str, str]] = Field(None, description="HTTP headers")
    data: T = Field(description="Deserialized data given the data type")
    raw_data: StrictBytes = Field(description="Raw data (HTTP response body)")

    model_config = {
        "arbitrary_types_allowed": True
    }
