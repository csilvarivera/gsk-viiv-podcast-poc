# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility module to work with app config.
"""

from os.path import isfile
import tomllib

PAGES_TOML = "config/pages_config.toml"
GCP_TOML = "config/gcp_config.toml"

# Check if the config file exists
assert isfile(PAGES_TOML), f"Missing Pages Configuration file: {PAGES_TOML} should exist"
assert isfile(GCP_TOML), f"Missing GCP configuration file: {GCP_TOML} should exist"

with open(PAGES_TOML, "rb") as f:
    try:
        pages_config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print("Invalid configuration TOML file.")
        print(str(e))
        raise

with open(GCP_TOML, "rb") as f:
    try:
        gcp_config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print("Invalid configuration TOML file.")
        print(str(e))
        raise

assert "project" in gcp_config, f"No project configuration found in {GCP_TOML}" 
assert "project_id" in gcp_config["project"], f"No project ID found in {GCP_TOML}"
assert "location" in gcp_config["project"], f"No project location found in {GCP_TOML}"
assert "vertex_ai" in gcp_config, f"No Vertex AI configuration found in {GCP_TOML}"
assert "bigquery" in gcp_config, f"No BigQuery configuration found in {GCP_TOML}"
assert "gcs" in gcp_config, f"No GCS configuration found in {GCP_TOML}"
assert "uri" in gcp_config["gcs"], f"No GCS URI specified in {GCP_TOML}"
assert "pages" in pages_config, f"No pages configurations found in {PAGES_TOML}"

PROJECT_CFG = gcp_config["project"]

VERTEX_CFG = gcp_config["vertex_ai"]
if "project_id" not in VERTEX_CFG:
    VERTEX_CFG["project_id"] = PROJECT_CFG["project_id"]
if "location" not in VERTEX_CFG:
    VERTEX_CFG["location"] = PROJECT_CFG["location"]
if "model" not in VERTEX_CFG:
    VERTEX_CFG["model"] = "gemini-1.5-pro-002"

GCS_CFG = gcp_config["gcs"]

BQ_CFG = gcp_config["bigquery"]
if "project_id" not in BQ_CFG:
    BQ_CFG["project_id"] = PROJECT_CFG["project_id"]
if "location" not in BQ_CFG:
    BQ_CFG["location"] = PROJECT_CFG["location"]
if "dataset" not in BQ_CFG:
    BQ_CFG["dataset"] = "podcasts"
if "table" not in BQ_CFG:
    BQ_CFG["table"] = "history"

PAGES_CFG = pages_config["pages"]