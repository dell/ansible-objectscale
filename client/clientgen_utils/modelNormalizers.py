# Copyright (c) 2025 Dell Inc., or its subsidiaries. All Rights Reserved.

# Licensed under the Mozilla Public License Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://mozilla.org/MPL/2.0/


# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def _normalizeObjectScaleLink(json_obj: dict) -> dict:
    """
    Look recursively through all schemas.
    Any property that looks like a link, should be normalised to Link.
    """
    common_type = {
        "type": "object",
        "properties": {
            "rel": {
                "type": "string",
                "description": "Relationship type of the hyperlink"
            },
            "href": {
                "type": "string",
                "description": "Hyperlink URL to the related resource"
            }
        },
        "description": "Hyperlink to the details for this resource"
    }
    common_ref = {
        "$ref": "#/components/schemas/Link"
    }

    def _rec_helper(obj: any) -> bool:
        if obj == common_type:
            return True
        elif isinstance(obj, dict):
            for key, item in obj.items():
                if _rec_helper(item):
                    obj[key] = common_ref
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if _rec_helper(item):
                    obj[i] = common_ref
        return False
    _rec_helper(json_obj['components']['schemas'])
    json_obj['components']['schemas']['Link'] = common_type
    return json_obj


def NormalizeObjectScaleModels(json_obj: dict) -> dict:
    """
    Normalize ObjectScale specific models.
    Only Link normalization is needed for the namespace module.
    """
    ret = _normalizeObjectScaleLink(json_obj)
    return ret
