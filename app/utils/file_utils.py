import os
import uuid

TEMP_DIR = "temp"


def get_temp_path(filename: str) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    ext = os.path.splitext(filename)[1]
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")


def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)
