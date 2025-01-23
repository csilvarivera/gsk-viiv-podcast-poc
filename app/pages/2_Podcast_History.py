import pandas as pd
import streamlit as st
import io
from parse_config import GLOBAL_CFG, PAGES_CFG,GCS_CFG,BQ_CFG
from utils import utils_bigquery

# set page config
page_cfg = PAGES_CFG["1_Podcast_Creation"]
st.set_page_config(
    page_title=page_cfg["page_title"], 
    page_icon=page_cfg["page_icon"],
    layout='wide'
)

# Set the global parameters
PROJECT_ID = GLOBAL_CFG["project_id"]
LOCATION = GLOBAL_CFG["location"]

# Set the BQ parameters
BQ_DATASET = BQ_CFG["bq_dataset"]
BQ_TABLE = BQ_CFG["bq_table"]

# Initialise Pandas and Vertex Prediction
pd.set_option('display.max_colwidth', None)

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

# Initialise BigQuery
utils_bigquery.initialze_bigquery(
project_id=PROJECT_ID,
location="us",
)
pd.set_option('display.max_colwidth', None)

with st.spinner("Loading data..."):
    # Read data from BigQuery
    df = utils_bigquery.get_podcasts(
        project_id=PROJECT_ID,
        bq_dataset=BQ_DATASET,
        bq_table=BQ_TABLE,
    )
#choose only the columns we need
df = df[['podcast_name','file_name','podcast_summary','podcast_script','podcast_location']]
df.columns =['podcast_name','file_name','podcast_summary','podcast_script','podcast_location']
rows = len(df)
st.dataframe(df, hide_index=True)

