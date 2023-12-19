import hashlib


def calculate_hash(text):
    hash_object = hashlib.sha256(text.encode())
    full_hash = hash_object.hexdigest()
    return full_hash[:16]