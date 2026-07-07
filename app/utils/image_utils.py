import shutil
from fastapi import UploadFile


def save_upload(file: UploadFile, dest_path: str):
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
