from fastapi import HTTPException, UploadFile
from hashlib import sha256
from pathlib import Path

from twok.database.crud import DB


async def save_upload_file(file: UploadFile) -> str:
    """
    Saves an uploaded file to the uploads directory and returns the sha256 hash of the file.

    You may suggest to upload the file to some form of object storage instead of the filesystem.
    But we won't be storing an endless amount of files. Files, like posts, will be deleted after a
    certain amount of time.
    """
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            buffer.write(chunk)

    return sha256(open(file_path, "rb").read()).hexdigest()


def delete_file(file, db: DB):
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = Path(f"uploads/{file.file_name}")
    file_path.unlink()

    db.file.delete(file)
