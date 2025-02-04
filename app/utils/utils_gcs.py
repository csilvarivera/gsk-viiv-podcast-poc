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

from google.cloud import storage
from urllib.parse import urlparse
import streamlit as st
import string
import random


def convert_https_to_gs_for_display(https_url):
    """Converts https://storage.mtls.cloud.google.com URL to gs:// URI for display ONLY."""
    try:
        parsed_url = urlparse(https_url)
        if parsed_url.netloc != "storage.mtls.cloud.google.com":
            return None

        path_parts = parsed_url.path.split("/")
        if len(path_parts) < 3:
            return None

        bucket_id = path_parts[1]
        gcs_path = "/".join(path_parts[2:])
        return f"gs://{bucket_id}/{gcs_path}"
    except Exception as e:
        st.error(f"Error converting URL: {e}")
        return None

def upload_file(bucket:str, destination_blob_name:str,  file) -> str:
    """ Uploads file to a given GCS bucket"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)
    return blob.public_url

def upload_wav_file(bucket:str, destination_blob_name:str, file) -> str:
    """ Uploads a wav file to a GCS bucket """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file, content_type='audio/wav')
    return blob.path

def download_file_as_string(bucket:str, blob_name:str):
    """ Downloads a file from a given GCS bucket"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(blob_name)
    # Download the file to a local file
    file_as_string = blob.download_as_string()
    print (f"File downloaded from GCS in bucket {bucket} for file {blob_name}")
    return file_as_string

def download_file_as_bytes(bucket:str, blob_name:str):
    """ Downloads a file from a given GCS bucket"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(blob_name)
    # Download the file to a local file
    file_as_bytes = blob.download_as_bytes()
    print (f"File downloaded from GCS in bucket {bucket} for file {blob_name}")
    return file_as_bytes

def delete_file(project:str, bucket:str, blob_name:str):
    """ Deletes a file from a given GCS bucket"""
    storage_client = storage.Client(project=project)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(blob_name)
    # Delete the file from the bucket
    blob.delete()
    print (f"file deleted from GCS in bucket {bucket} for file {blob_name}")
    return True

def get_random_id(length=4):  # You can adjust the length of the ID
    """Generates a random alphanumeric ID."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def parse_gcs_uri(gcs_uri: str) -> tuple[str, str]:
    """Parses a GCS URI to extract the bucket name and folder path.
       Distinguishes between files and folders using the presence of a '.'
       in the last part of the path.

    Args:
        gcs_uri: The GCS URI (e.g., "gs://my-bucket/path/to/folder/").

    Returns:
        A tuple containing the bucket name and folder path.
        Returns (None, None) if the URI is invalid or doesn't follow
        the expected "gs://bucket/path" format.  If it's a file,
        the folder path will be the path *leading up to* the file.
    """

    try:
        parsed_uri = urlparse(gcs_uri)

        if parsed_uri.scheme != "gs":
            return None, None  # Not a GCS URI

        path = parsed_uri.path.lstrip("/")

        if not path:  # Empty path means root of the bucket
            return parsed_uri.netloc, ""

        bucket_name = parsed_uri.netloc

        parts = path.split("/")
        last_part = parts[-1]

        if "." in last_part:  # It's a file (or at least looks like one)
            folder_path = "/".join(parts[:-1]) if len(parts) > 1 else ""  # Path before the filename
        else:  # It's a folder (or doesn't have a file extension)
            folder_path = path.rstrip("/") if path.endswith("/") else path  # Remove trailing slash if present

        return bucket_name, folder_path

    except Exception:
        return None, None  # Handle parsing errors