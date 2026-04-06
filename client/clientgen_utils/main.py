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

from modelNormalizers import NormalizeObjectScaleModels
from commonUtils import ProcessOpenapiSpec
from requiredApis import RequiredAPIs
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


parser = argparse.ArgumentParser(
    description='Process ObjectScale OpenAPI spec.')
parser.add_argument(
    '--input',
    help='Input ObjectScale OpenAPI spec file path.',
    required=True)
parser.add_argument(
    '--output',
    help='Output filtered ObjectScale OpenAPI spec file path.',
    required=True)

args = parser.parse_args()

# common processing of OpenAPI spec
filtered_json = ProcessOpenapiSpec(args.input, RequiredAPIs)

# ObjectScale specific processing


def AddObjectScaleMarker(json_obj: dict) -> dict:
    """
    Add ObjectScale specific marker to the OpenAPI spec.
    Adds 'x-is-paginated' to any model with 'NextMarker' object.
    Adds 'x-is-paginated-resp' to any property of type array within the paginated model.
    These are later used to add pagination related getters in the generated code.
    """
    for _unused, obj in json_obj['components']['schemas'].items():
        if 'properties' in obj and 'NextMarker' in obj['properties']:
            obj['x-is-paginated'] = "true"
            for _unused_prop, prop in obj['properties'].items():
                if prop.get('type') == 'array':
                    prop['x-is-paginated-resp'] = 'true'
    return json_obj


filtered_json = AddObjectScaleMarker(filtered_json)
filtered_json = NormalizeObjectScaleModels(filtered_json)

# write to file
with open(args.output, 'w') as outfile:
    json.dump(filtered_json, outfile, indent="\t")

print(f"Filtered spec written to {args.output}")
