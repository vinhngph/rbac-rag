from os import makedirs
from os.path import abspath, join as path_join, dirname
from fastapi import UploadFile
from anyio import open_file

from app.core.config import settings


class StoreService:
    def __init__(self) -> None:
        self.storage_dir = abspath(settings.STORAGE_DIR)
        self.quarantine_dir = path_join(self.storage_dir, "quarantine")
        self.safe_dir = path_join(self.storage_dir, "safe")

        makedirs(self.quarantine_dir, exist_ok=True)
        makedirs(self.safe_dir, exist_ok=True)

    def get_quarantine_path(self, relative_path: str):
        full_path = abspath(path_join(self.quarantine_dir, relative_path))

        if not full_path.startswith(self.quarantine_dir):
            raise ValueError("Security Alert: Path Traversal attack detected!")

        return full_path

    async def save_to_quarantine_zone(self, file: UploadFile, relative_path: str):
        """Save uploaded file to quarantine zone"""

        full_path = self.get_quarantine_path(relative_path)

        makedirs(dirname(full_path), exist_ok=True)

        await file.seek(0)

        async with await open_file(full_path, "wb") as buffer:
            chunk_size = 1024 * 1024
            while chunk := await file.read(chunk_size):
                await buffer.write(chunk)

        return full_path
