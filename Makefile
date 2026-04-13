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

OPENAPI_CMD?=java -Xmx16G -jar openapi-generator-cli-7.21.0.jar
OPENAPI_GEN_DIR=plugins/module_utils/objectscale_client
OPENAPI_GEN_TMPDIR:=$(shell mktemp -d)
OPENAPI_GEN_NESTED=${OPENAPI_GEN_TMPDIR}/ansible_collections/dellemc/objectscale/plugins/module_utils/objectscale_client
OPENAPI_SOURCE_DIR=client/build
OPENAPI_FULL_PATH=${OPENAPI_SOURCE_DIR}/openapi_4.1
OPENAPI_FILTERED_PATH=${OPENAPI_SOURCE_DIR}/openapi_4.1_filtered.json
CLIENTGEN_UTILS_DIR=client/clientgen_utils
SANITY_IGNORE_FILE=tests/sanity/ignore-2.20.txt
SANITY_SKIP_TESTS=

default: help

help:
	@echo "Available targets:"
	@echo "  download_openapi - Download openapi-generator-cli-7.21.0.jar from Maven Central"
	@echo "  build_spec   - Filter the raw OpenAPI spec to only required APIs"
	@echo "  build_client - Generate Python client into plugins/module_utils/storage/dell/"
	@echo "  generate     - Full pipeline: build_spec + build_client"
	@echo "  sanity_ignores - Regenerate tests/sanity/ignore-2.20.txt from generated client files"
	@echo "  lint         - Run ansible-lint on the collection"
	@echo "  test         - Run unit tests"

download_openapi:
	@if [ ! -f openapi-generator-cli-7.21.0.jar ]; then \
		echo "Downloading openapi-generator-cli-7.21.0.jar..."; \
		curl -L -o openapi-generator-cli-7.21.0.jar \
			https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.21.0/openapi-generator-cli-7.21.0.jar; \
		echo "Downloaded openapi-generator-cli-7.21.0.jar"; \
	else \
		echo "openapi-generator-cli-7.21.0.jar already exists"; \
	fi

build_spec: download_openapi
	python3 ${CLIENTGEN_UTILS_DIR}/main.py --input ${OPENAPI_FULL_PATH} --output ${OPENAPI_FILTERED_PATH}

build_client: build_spec
	# Remove all generated files except manually maintained ones.
	# The COMPLETE list of manually maintained files are:
	# - _stubs.py
	# - api_client.py
	# - api_response.py
	# - configuration.py
	# - exceptions.py
	# - rest.py
	# - __init__.py (managed by fix_sanity.py in api/ and models/ subdirectories)
	find ${OPENAPI_GEN_DIR} -name "*.py" ! -name "_stubs.py" ! -name "api_client.py" ! -name "api_response.py" ! -name "configuration.py" ! -name "exceptions.py" ! -name "rest.py" ! -name "__init__.py" -delete
	rm -rf ${OPENAPI_GEN_DIR}/api ${OPENAPI_GEN_DIR}/models
	${OPENAPI_CMD} generate \
		-i ${OPENAPI_FILTERED_PATH} \
		-g python \
		-o ${OPENAPI_GEN_TMPDIR} \
		--global-property apis,models,modelTests=false,apiTests=false,modelDocs=false,apiDocs=false \
		-c ${CLIENTGEN_UTILS_DIR}/config.yaml
	# The dotted packageName produces a nested directory tree matching the
	# full import path.  Move only API and models, preserve supporting files.
	mv ${OPENAPI_GEN_NESTED}/api ${OPENAPI_GEN_DIR}/
	mv ${OPENAPI_GEN_NESTED}/models ${OPENAPI_GEN_DIR}/
	rm -rf ${OPENAPI_GEN_TMPDIR}
	# Remove stray artifacts that the generator places inside the package
	find ${OPENAPI_GEN_DIR} -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	find ${OPENAPI_GEN_DIR} -name 'py.typed' -delete 2>/dev/null || true

generate: build_client format_client fix_sanity sanity_ignores

format_client:
	@echo "Formatting generated client with autoflake + isort + autopep8..."
	find $(OPENAPI_GEN_DIR) -name '*.py' ! -name '_stubs.py' ! -name 'api_client.py' ! -name 'api_response.py' ! -name 'configuration.py' ! -name 'exceptions.py' ! -name 'rest.py' ! -name '__init__.py' -print0 | xargs -0 autoflake --in-place --remove-all-unused-imports
	find $(OPENAPI_GEN_DIR) -name '*.py' ! -name '_stubs.py' ! -name 'api_client.py' ! -name 'api_response.py' ! -name 'configuration.py' ! -name 'exceptions.py' ! -name 'rest.py' ! -name '__init__.py' -print0 | xargs -0 isort
	find $(OPENAPI_GEN_DIR) -name '*.py' ! -name '_stubs.py' ! -name 'api_client.py' ! -name 'api_response.py' ! -name 'configuration.py' ! -name 'exceptions.py' ! -name 'rest.py' ! -name '__init__.py' -print0 | xargs -0 autopep8 --in-place --aggressive --max-line-length 160
	@echo "Formatting complete"

fix_sanity:
	@echo "Post-processing generated client for ansible-test sanity..."
	python3 $(CLIENTGEN_UTILS_DIR)/fix_sanity.py $(OPENAPI_GEN_DIR)

sanity_ignores:
	@mkdir -p tests/sanity
	@for ver in 2.16 2.17; do \
		ignore="tests/sanity/ignore-$$ver.txt"; \
		: > "$$ignore"; \
		case "$$ver" in \
			2.16|2.17) \
				echo "plugins/module_utils/objectscale_client/__init__.py empty-init!skip # generated client" >> "$$ignore"; \
				echo "plugins/module_utils/objectscale_client/api/__init__.py empty-init!skip # generated client" >> "$$ignore"; \
				echo "plugins/module_utils/objectscale_client/models/__init__.py empty-init!skip # generated client" >> "$$ignore"; \
				;; \
		esac; \
		echo "Generated $$ignore with $$(wc -l < "$$ignore") ignore entries"; \
	done

lint:
	ansible-lint

test:
	python -m pytest tests/unit/

.PHONY: default help download_openapi build_spec build_client format_client fix_sanity generate sanity_ignores lint test
