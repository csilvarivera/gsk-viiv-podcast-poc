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
from google.cloud import bigquery
import streamlit as st

@st.cache_resource
def initialize_bigquery(project_id: str, location: str):
    client = bigquery.Client(project=project_id, location=location)
    return client

@st.cache_data  
def get_podcasts(_client: bigquery.Client, bq_dataset: str, bq_table: str):
    """Obtain podcast previously saved in BQ using the standard client."""
    client = _client
    try:
      query = f"SELECT * FROM `{client.project}.{bq_dataset}.{bq_table}` ORDER BY 1 DESC"
      query_job = client.query(query)  # Make an API request.
      results = query_job.result()  # Waits for query to complete.
      df = results.to_dataframe() #Convert the results to a Pandas DataFrame
      return df
    except Exception as e:
        if "Not found" in str(e):
            st.write("No history available.")
            data = {
                "timestamp": [],
                "source_pdf": [],
                "summary": [],
                "script": [],
                "podcast_gcs_uri": [],
                "pdf_gcs_uri": []
                }
            df = pd.DataFrame(data)
            return df    
        else:
            st.error(f"Error retrieving data from BigQuery: {e}")

@st.cache_data
def save_to_podcast(df: pd.DataFrame, _client: bigquery.Client, bq_dataset: str, bq_table: str):
    """Save DataFrame to BigQuery using the standard client."""
    client = _client

    table_ref = f"{client.project}.{bq_dataset}.{bq_table}"

    # Check if the dataset exists
    dataset_ref = f"{client.project}.{bq_dataset}"
    try:
        client.get_dataset(dataset_ref)  # API request
        print(f"Dataset {bq_dataset} already exists.")
    except Exception as e:  # Catching exceptions is a good practice
        if "Not found" in str(e):  # Checking if the exception is related to not found dataset
            print(f"Dataset {bq_dataset} does not exist. Creating it.")
            dataset = bigquery.Dataset(dataset_ref)
            client.create_dataset(dataset)  # API request
        else:
            raise e  # Re-raise the exception if it's not a "not found" error

    schema = [
        bigquery.SchemaField(name="timestamp", field_type="DATETIME"),
        bigquery.SchemaField(name="source_pdf",field_type="STRING"),
        bigquery.SchemaField(name="summary", field_type="STRING"),
        bigquery.SchemaField(name="script", field_type="STRING"),
        bigquery.SchemaField(name="podcast_gcs_uri", field_type="STRING"),
        bigquery.SchemaField(name="pdf_gcs_uri", field_type="STRING")
    ]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        create_disposition="CREATE_IF_NEEDED",
        write_disposition="WRITE_APPEND",  # Append to the table
    )
    load_job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)  # Make an API request
    load_job.result()  # Wait for the job to complete.
    print(f"Loaded {load_job.output_rows} rows and {len(df.columns)} columns to {table_ref}")