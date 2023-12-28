import io
from firebase_admin import storage


def upload_audio_to_firebase(audio_bytes, file_name):
    # Convert bytes to a file-like object
    audio_stream = io.BytesIO(audio_bytes)

    # Create a reference to the Firebase storage
    bucket = storage.bucket()
    blob = bucket.blob(file_name)

    # Upload the file
    blob.upload_from_file(audio_stream, content_type='audio/mpeg')

    # Get the file's URL
    return blob.public_url
