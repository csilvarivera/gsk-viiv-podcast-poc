# Copyright 2023 Google LLC
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

APP_TOML = "app_config.toml"

# Check if the config file exists
assert isfile(APP_TOML), f"The file {APP_TOML} should exist"

with open(APP_TOML, "rb") as f:
    try:
        data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print("Invalid App Configuration TOML file.")
        print(str(e))
        raise

def merge(a: dict, b: dict):
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key])
            elif a[key] != b[key]:
                a[key] = b[key]
        else:
            a[key] = b[key]

assert "global" in data, "No global configurations in the config"
assert "pages" in data, "No page configurations found in the config"

GLOBAL_CFG = data["global"]
VERTEX_CFG = data["vertex_ai"]
GCS_CFG = data["gcs"]
BQ_CFG = data["BigQuery"]
PAGES_CFG = data["pages"]