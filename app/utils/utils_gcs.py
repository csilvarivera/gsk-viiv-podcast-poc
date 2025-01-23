from google.cloud import storage
import base64

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

def download_file_as_string( bucket:str, blob_name:str):
    """ Downloads a file from a given GCS bucket"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(blob_name)
    # Download the file to a local file
    file_as_string = blob.download_as_string()
    print (f"file downloaded from GCS in bucket {bucket} for file {blob_name}")
    return file_as_string

def delete_file(project:str, bucket:str, blob_name:str):
    """ Deletes a file from a given GCS bucket"""
    storage_client = storage.Client(project=project)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(blob_name)
    # Delete the file from the bucket
    blob.delete()
    print (f"file deleted from GCS in bucket {bucket} for file {blob_name}")
    return True