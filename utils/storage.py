from firebase_admin import storage


def get_video_url_from_firebase(file_name):
    # Create a reference to the Firebase storage
    bucket = storage.bucket()
    blob = bucket.blob(file_name)

    # Generate a signed URL for the blob; this URL is temporary
    return blob.generate_signed_url(version="v4", expiration=3600)
