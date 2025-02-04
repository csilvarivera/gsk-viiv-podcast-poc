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

from utils.parse_config import PAGES_CFG
import streamlit as st

page_cfg = PAGES_CFG["Home"]

st.set_page_config(
    page_title=page_cfg["page_title"], 
    page_icon=page_cfg["page_icon"]
)

st.sidebar.success("Select an option.")

cols = st.columns([15, 85])
with cols[0]:
    st.image(page_cfg["page_title_image"])
with cols[1]:
    st.title(page_cfg["page_title"])

st.write(
    """
    This application is built as a proof-of-concept to demonstrate how to generate a podcast using
    for ViiV Healthcare using PDF documents as input.
    This was developed as part of GSK HCPs Digital Education Programme.

    In the sidebar, you can select two options:
    * *Podcast Creation*
    * *Podcast History*

    *Podcast Creation* contains a simple process to generate a podcast from a PDF file.  
    *Podcast History* displays all previous podcasts that have been generated and saved. 
    """)

st.divider()
with st.expander("Disclaimer: this is not an official Google product"):
    st.write("""
This is a functional demo with the purpose to showcase capabilities of Google products.
""")
