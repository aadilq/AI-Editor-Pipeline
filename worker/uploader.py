from google.cloud import storage

def upload_public_file(bucket_name, source_file_path, destination_blob_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    blob.make_public()

    return blob.public_url
