import pandas as pd
import streamlit as st
import io
import pandas as pd
from parse_config import GLOBAL_CFG, VERTEX_CFG, PAGES_CFG,GCS_CFG, BQ_CFG
from utils import utils_vertex
from utils import utils_gcs
from utils import utils_tts
from utils import utils_audio
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

# Set the vertex parameters
MODEL = VERTEX_CFG["model"]

# Set the GCS parameter
PDF_BUCKET=GCS_CFG["pdf_bucket"]
TMP_BUCKET=GCS_CFG["tmp_bucket"]

# Set the BQ parameters
BQ_DATASET = BQ_CFG["bq_dataset"]
BQ_TABLE = BQ_CFG["bq_table"]

# Initialise Pandas and Vertex Prediction
pd.set_option('display.max_colwidth', None)
utils_vertex.initialise_vertex(PROJECT_ID, LOCATION)

cols = st.columns([15, 85])
with cols[0]:
    st.image(page_cfg["page_title_image"])
with cols[1]:
    st.title(page_cfg["page_title"])

st.write(
    """
    This page provides a guided process to create a podcast for ViiV Healthcare.
    """
) 

# Upload file
with st.expander("Podcast Config",expanded =True):
    with st.form("Parameters"):
        uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
        podcast_duration = st.selectbox ("Select an approximate podcast duration", ("7-mins","15-mins"))
        submitted = st.form_submit_button("Submit")
if submitted and uploaded_files:
    for uploaded_file in uploaded_files:
        # Handle uploaded file
        my_bar = st.progress(0, text="processing file")
        destination = utils_gcs.upload_file(PDF_BUCKET, uploaded_file.name, uploaded_file)
        uri = "gs://" + PDF_BUCKET + "/" + uploaded_file.name
        my_bar.progress(100, text=f"file processed at {uri}")
        # check if the podcast is a long one 
        is_long_podcast = True if podcast_duration == "15-mins" else False
        # Summarize the PDF
        my_bar = st.progress(0, text="Summarising File")
        summary_model = utils_vertex.get_model(MODEL,utils_vertex.get_system_instructions_summariser(),0)
        summary = utils_vertex.get_gemini_response(summary_model,utils_vertex.get_summary_prompt(is_long_podcast),uri)
        my_bar.progress (35, text="File Summarised")
        # Create podcast script
        my_bar.progress(50, text="Creating Podcast script")
        podcast_model = utils_vertex.get_model(MODEL,utils_vertex.get_system_instructions_podcast(),1)
        podcast = utils_vertex.get_gemini_response(podcast_model,utils_vertex.get_podcast_prompt(summary,is_long_podcast))
        my_bar.progress(100, text=" Podcast Script created")
        # construct the editable tetx area to hold the script
        with st.expander("Podcast Script"):
            final_script = st.text_area(label="Podcast Script", value = podcast.replace("|", "\n"), height=1500)
        # generate audio file
        my_bar = st.progress(50, text="Creating speaker flow")
        # create audio files
        multi_speaker_markup = utils_tts.create_podcast_chapters(podcast)
        my_bar.progress(70, text="Combining Podcast Files")
        #  combine all files into one single podcast
        file_paths = utils_audio.get_audio_file_paths()
        utils_audio.concatenate_audio_files(file_paths)
        podcast_name =  f"{uploaded_file.name}.wav"
        # upload the file to GCS for storage
        destination = utils_gcs.upload_wav_file(PDF_BUCKET, podcast_name, "tmp/output.wav")
        my_bar.progress(90, text="Storing the Podcast in GCS Bucket")
        print (destination)
        my_bar.progress(100, text="Podcast Created")
        # create the audo object
        audio_file = utils_gcs.download_file_as_string(PDF_BUCKET, podcast_name)
        st.audio(io.BytesIO(audio_file))
        # delete tmp files
        utils_audio.delete_audio_files(file_paths)
        
        ## uncomment if you want to save the podcast record into BigQuery
        # initialise the bq client
        # utils_bigquery.initialze_bigquery("us", PROJECT_ID)
        # # create a dataframe from the values 
        # # Create an empty dictionary with column names as keys
        # data = {
        #     'podcast_name': [],
        #     'file_name': [],
        #     'podcast_summary': [],
        #     'podcast_script': [],
        #     'podcast_location': []
        # }
        # df = pd.DataFrame(data)
        # df.loc[0] = [f"{uploaded_file.name} - show",uploaded_file.name,summary,final_script,f"gs://{PDF_BUCKET}/{podcast_name}"]
        # utils_bigquery.save_to_podcast(df,PROJECT_ID,BQ_DATASET,BQ_TABLE)



