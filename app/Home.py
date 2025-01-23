# Copyright 2024 Google LLC
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


from  parse_config import PAGES_CFG
import pandas as pd
import streamlit as st
import base64

page_cfg = PAGES_CFG["home"]

# uncomment if developing locally
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'

st.set_page_config(
    page_title=page_cfg["page_title"], 
    page_icon=page_cfg["page_icon"]
)


st.sidebar.success("Select an option.")

file_name_1 = page_cfg["file_name_1"]
file_name_2 = page_cfg["file_name_2"]

with open(file_name_1, "rb") as fp:
    contents = fp.read()
    main_image_1 = base64.b64encode(contents).decode("utf-8")
    main_image_1 = 'data:image/png;base64,'+main_image_1

with open(file_name_2, "rb") as fp:
    contents = fp.read()
    main_image_2 = base64.b64encode(contents).decode("utf-8")
    main_image_2 = 'data:image/png;base64,'+main_image_2

cols = st.columns([15, 85])
with cols[0]:
    st.image(page_cfg["page_title_image"])
with cols[1]:
    st.title(page_cfg["page_title"])

st.write(
    """
    This application provides a guided way to create Podcast fas part of GSK HCPs Digital Education Programme.
    """
)

st.image (page_cfg["architecture_image"])

st.divider()
with st.expander("disclaimer: this is not an official Google product"):
    st.write("""
This is not an official Google product. This is a functional demo with a purpose to showcase capabilities of Google products.
""")

# Example usage:
# file_path = '/Users/csilvarivera/Documents/gsk-comms/app/sample.json' 
# df = utils_brandwatch.extract_data_from_json(file_path)
# print(df.head(5))
