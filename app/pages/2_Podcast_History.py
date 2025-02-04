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

import streamlit as st
from utils.parse_config import PAGES_CFG,BQ_CFG
from utils import utils_bigquery

# set page config
page_cfg = PAGES_CFG["2_Podcast_History"]
st.set_page_config(
    page_title=page_cfg["page_title"], 
    page_icon=page_cfg["page_icon"],
    layout=page_cfg["layout"]
)

# Set the BQ parameters
BQ_PROJECT = BQ_CFG["project_id"]
BQ_LOCATION = BQ_CFG["location"]
BQ_DATASET = BQ_CFG["dataset"]
BQ_TABLE = BQ_CFG["table"]

# State variables for session management
if "bq_client" not in st.session_state:
    st.session_state.bq_client = utils_bigquery.initialize_bigquery(BQ_PROJECT, BQ_LOCATION)

cols = st.columns([15, 85])
with cols[0]:
    st.image(page_cfg["page_title_image"])
with cols[1]:
    st.title(page_cfg["page_title"])

st.write(
    """
    This page shows all previous podcasts created by ViiV Healthcare.
    """
) 

with st.spinner("Loading data..."):
    # Read data from BigQuery
    df = utils_bigquery.get_podcasts(
        _client=st.session_state.bq_client,
        bq_dataset=BQ_DATASET,
        bq_table=BQ_TABLE
        )
    #choose only the columns we need

    df = df[["timestamp","summary","script","podcast_gcs_uri", "pdf_gcs_uri"]]
    df["podcast_gcs_uri"] = df["podcast_gcs_uri"].apply(lambda x: x.replace("gs://", "https://storage.mtls.cloud.google.com/"))  
    df["pdf_gcs_uri"] = df["pdf_gcs_uri"].apply(lambda x: x.replace("gs://", "https://storage.mtls.cloud.google.com/"))
    
    column_config = {
        "timestamp": st.column_config.DatetimeColumn(
            label="Timestamp",
            pinned=True,
            help="The time when the podcast was created.",
            disabled=True
        ),
        "summary": st.column_config.TextColumn(
            label="Summary",
            help="The summary of the PDF used to generate the podcast script.",
            disabled=True
        ),
        "script": st.column_config.TextColumn(
            label="Podcast Script",
            help="The podcast script generated from the PDF.",
            disabled=True
        ),                             
        "podcast_gcs_uri": st.column_config.LinkColumn(
            label="Podcast Audio File",
            pinned=True,
            help="The authenticated link to the podcast file in GCS.",
            display_text=r"https://storage\.mtls\.cloud\.google\.com/.*/+(.*\.wav)",
            disabled=True
        ),
        "pdf_gcs_uri": st.column_config.LinkColumn(
            label="Source PDF File",
            pinned=True,
            help="The authenticated link to the source PDF file in GCS.",
            display_text=r"https://storage\.mtls\.cloud\.google\.com/.*/+(.*\.pdf)",
            disabled=True
        )
    }

    if len(df):
        st.dataframe(df, hide_index=True, use_container_width=True, column_config=column_config)