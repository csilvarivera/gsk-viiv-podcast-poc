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

import pandas as pd
import streamlit as st
import time
from utils.parse_config import VERTEX_CFG, GCS_CFG, PAGES_CFG, BQ_CFG, TEMP_FOLDER
from utils import utils_vertex, utils_audio, utils_bigquery, utils_tts, utils_gcs

page_cfg = PAGES_CFG["1_Podcast_Creation"]

# Setting the page configuration
st.set_page_config(
    page_title=page_cfg["page_title"], 
    page_icon=page_cfg["page_icon"],
    layout=page_cfg["layout"]
)

# Set the vertex parameters
VERTEX_PROJECT = VERTEX_CFG["project_id"]
VERTEX_MODEL = VERTEX_CFG["model"]
VERTEX_LOCATION = VERTEX_CFG["location"]

# Set the GCS parameter
GCS_URI = GCS_CFG["uri"]

# Set the BQ parameters
BQ_PROJECT = BQ_CFG["project_id"]
BQ_DATASET = BQ_CFG["dataset"]
BQ_TABLE = BQ_CFG["table"]
BQ_LOCATION = BQ_CFG["location"]

# Initializing Pandas and Vertex Prediction
utils_vertex.initialize_vertex(VERTEX_PROJECT, VERTEX_LOCATION)
       
# State variables for session management
if "bq_client" not in st.session_state:
    st.session_state.bq_client = utils_bigquery.initialize_bigquery(BQ_PROJECT, BQ_LOCATION)
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""
if "podcast_file_name" not in st.session_state:
    st.session_state.podcast_file_name = ""
if "gcs_bucket" not in st.session_state:
    st.session_state.gcs_bucket = ""
if "gcs_folder_path" not in st.session_state:
    st.session_state.gcs_folder_path = ""
if "processed_text" not in st.session_state:
    st.session_state.processed_text = ""
if "original_text" not in st.session_state:
    st.session_state.original_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "saving_to_bigquery" not in st.session_state:
    st.session_state.saving_to_bigquery = False
if "updated_bigquery" not in st.session_state:
    st.session_state.updated_bigquery = False
if "ready_to_generate_audio" not in st.session_state:
    st.session_state.ready_to_generate_audio = False
if "audio_generated" not in st.session_state:
    st.session_state.audio_generated = False
if "script_generated" not in st.session_state:
    st.session_state.script_generated = False

cols = st.columns([15, 85])
with cols[0]:
    st.image(page_cfg["page_title_image"])
with cols[1]:
    st.title(page_cfg["page_title"])

st.write(
    """
    This page provides a guided process to create a podcast for ViiV Healthcare.
    The application supports only PDF files as input.
    """
) 

# 1. PDF Upload
uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False, type=["pdf"])
podcast_duration = st.selectbox("Select an approximate podcast duration", ("7-mins", "15-mins"))

# 2. Process PDF Button
if st.button("Generate Podcast Script", icon=":material/stylus_note:") and uploaded_file is not None:
    # Handle uploaded file
    with st.spinner("Running..."):
        my_bar = st.progress(0, text=f"Uploading to GCS")
        gcs_bucket, gcs_folder_path = utils_gcs.parse_gcs_uri(GCS_URI)
        st.session_state.uploaded_file_name = f"{uploaded_file.name[:-4]}-{utils_gcs.get_random_id(4)}.pdf"
        st.session_state.gcs_bucket = gcs_bucket
        st.session_state.gcs_folder_path = gcs_folder_path
        
        bucket_file_path = f"{gcs_folder_path}/{st.session_state.uploaded_file_name}"
        gcs_file_uri = f"gs://{gcs_bucket}/{bucket_file_path}"
        destination = utils_gcs.upload_file(gcs_bucket, bucket_file_path, uploaded_file)
        my_bar.progress(25, text=f"PDF file uploaded to GCS")
        is_long_podcast = True if podcast_duration == "15-mins" else False

        # Summarize
        my_bar.progress(30, text="Summarizing File")
        summary_model = utils_vertex.get_model(VERTEX_MODEL, utils_vertex.get_system_instructions_summarizer(), 0)
        summary = utils_vertex.get_gemini_response(summary_model, utils_vertex.get_summary_prompt(is_long_podcast), gcs_file_uri)
        my_bar.progress(35, text="File Summarized")
        # Create Podcast Script
        my_bar.progress(50, text="Generating Podcast Script")
        podcast_model = utils_vertex.get_model(VERTEX_MODEL, utils_vertex.get_system_instructions_podcast(), 1)
        podcast = utils_vertex.get_gemini_response(podcast_model, utils_vertex.get_podcast_prompt(summary, is_long_podcast))
        my_bar.progress(100, text="Podcast Script Created")
        
    # Updating session state
    st.session_state.original_text = podcast.replace("| ", "\n")
    st.session_state.processed_text = st.session_state.original_text
    st.session_state.summary = summary
    st.session_state.script_generated = True

    st.toast("Podcast Script Created!")
    time.sleep(1)
    st.rerun()

# 3. Conditional Text Area
if st.session_state.script_generated:
    if "text_area_key" not in st.session_state:  # Initialize the key
        st.session_state.text_area_key = 0

    final_script = st.text_area("Podcast Script",
                                value=st.session_state.processed_text,
                                height=450,
                                label_visibility="collapsed",
                                key=f"podcast_script_{st.session_state.text_area_key}")

    # Buttons Row
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Save Modifications", icon=":material/save:"):
            st.session_state.processed_text = final_script
            st.session_state.text_area_key += 1  # Increment the key to force recreation
            st.toast("Modifications saved!")  
    
    with col2:
        if st.button("Reset Script", icon=":material/keyboard_previous_language:"):
            st.session_state.processed_text = st.session_state.original_text
            st.session_state.text_area_key += 1  # Increment the key to force recreation
            st.toast("Script reset to the original text.")
            st.rerun()

    with col3:
        # 5. Generate Audio
        if st.button("Generate Podcast", icon=":material/podcasts:"):
            st.session_state.ready_to_generate_audio = True
            st.session_state.audio_generated = False
            st.rerun()

    # 6. Download Audio (Only show after generation)
    if st.session_state.ready_to_generate_audio:
        if not st.session_state.audio_generated:
            st.session_state.podcast_file_name = f"{st.session_state.uploaded_file_name[:-8]}{utils_gcs.get_random_id(4)}.wav"
        bucket_podcast_path = f"{st.session_state.gcs_folder_path}/{st.session_state.podcast_file_name}"
        gcs_podcast_uri = f"gs://{st.session_state.gcs_bucket}/{bucket_podcast_path}"
        if not st.session_state.audio_generated:
            local_podcast_path = f"{TEMP_FOLDER}/output.wav"
            my_bar = st.progress(0, text="Creating Speaker Flow")
            multi_speaker_markup = utils_tts.create_podcast_chapters(final_script.replace("\n", "| "))
            my_bar.progress(25, text="Combining Podcast Files")
            file_paths = utils_audio.get_audio_file_paths()
            utils_audio.concatenate_audio_files(file_paths)
            my_bar.progress(80, "Uploading the Podcast to GCS")
            destination = utils_gcs.upload_wav_file(st.session_state.gcs_bucket, bucket_podcast_path, local_podcast_path)
            utils_audio.delete_audio_files()
            my_bar.progress(100, text=f"Podcast saved on GCS: {destination}")
            st.toast("Podcast Audio Generated!")
            st.session_state.audio_generated = True
            st.rerun()
        try:
            audio_file_bytes = utils_gcs.download_file_as_bytes(st.session_state.gcs_bucket, bucket_podcast_path)
            st.audio(audio_file_bytes)

            download_col, save_bq_col, _ = st.columns(3)
            with download_col:
                st.download_button("Download Podcast", data=audio_file_bytes, file_name=st.session_state.podcast_file_name, mime="audio/wav", icon=":material/download:")

            with save_bq_col:
                # 4. Save to BigQuery
                if st.button("Save Podcast History", icon=":material/archive:") and final_script:
                    st.session_state.saving_to_bigquery = True

        except Exception as e:
            st.error(f"Error downloading audio: {e}")

    if st.session_state.saving_to_bigquery:
        with st.spinner("Updating BigQuery..."):
            gcs_podcast_uri = f"gs://{st.session_state.gcs_bucket}/{st.session_state.gcs_folder_path}/{st.session_state.podcast_file_name}"
            gcs_file_uri = f"gs://{st.session_state.gcs_bucket}/{st.session_state.gcs_folder_path}/{st.session_state.uploaded_file_name}"
            data = {
                "timestamp": [pd.Timestamp(time.time(), unit='s').floor("us")],
                "source_pdf": [st.session_state.uploaded_file_name[:-9]],
                "summary": [st.session_state.summary],
                "script": [st.session_state.processed_text],
                "podcast_gcs_uri": [gcs_podcast_uri],
                "pdf_gcs_uri": [gcs_file_uri]
            }
            utils_bigquery.save_to_podcast(
                df=pd.DataFrame(data),
                _client=st.session_state.bq_client,
                bq_dataset=BQ_DATASET,
                bq_table=BQ_TABLE)
        st.success("Podcast History Saved!")
        st.session_state.saving_to_bigquery = False
        st.balloons()
        time.sleep(5)
        st.cache_data.clear()
else:
    st.info("Please upload a file and generate the podcast script to begin.")