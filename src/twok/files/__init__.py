from fastapi import UploadFile
from hashlib import sha256


async def save_upload_file(file: UploadFile) -> str:
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            buffer.write(chunk)

    return sha256(open(file_path, "rb").read()).hexdigest()
