from os import makedirs
from os.path import abspath, join as path_join, commonpath
from fastapi import UploadFile
from anyio import open_file, Path as AsyncPath
from uuid import UUID

from app.core.config import settings


class StoreService:
    def __init__(self) -> None:
        self.storage_dir = abspath(settings.STORAGE_DIR)
        self.quarantine_dir = path_join(self.storage_dir, "quarantine")
        self.safe_dir = path_join(self.storage_dir, "safe")

        makedirs(self.quarantine_dir, exist_ok=True)
        makedirs(self.safe_dir, exist_ok=True)

    def get_quarantine_path(self, file_id: UUID):
        full_path = abspath(path_join(self.quarantine_dir, str(file_id)))

        if commonpath([self.quarantine_dir, full_path]) != self.quarantine_dir:
            raise ValueError("Security Alert: Path Traversal attack detected!")

        return full_path

    def get_safe_path(self, file_id: UUID):
        full_path = abspath(path_join(self.safe_dir, str(file_id)))

        if commonpath([self.safe_dir, full_path]) != self.safe_dir:
            raise ValueError("Security Alert: Path Traversal attack detected!")

        return full_path

    async def save_to_quarantine_zone(
        self, file: UploadFile, file_id: UUID, max_size: int = 10 * 1024 * 1024
    ):
        """Save uploaded file to quarantine zone"""

        full_path = self.get_quarantine_path(file_id)

        await AsyncPath(full_path).parent.mkdir(parents=True, exist_ok=True)

        await file.seek(0)

        total_bytes = 0
        async with await open_file(full_path, "wb") as buffer:
            chunk_size = 1024 * 1024
            while chunk := await file.read(chunk_size):
                total_bytes += len(chunk)
                if total_bytes > max_size:
                    raise ValueError(
                        "Security Alert: File exceeds maximum allowed size during transmission."
                    )
                await buffer.write(chunk)

    async def delete_from_quarantine(self, file_id: UUID):
        q_path = self.get_quarantine_path(file_id)
        async_q_path = AsyncPath(q_path)

        try:
            await async_q_path.unlink()
        except FileNotFoundError:
            pass
        except (IsADirectoryError, PermissionError):
            raise ValueError(
                "Security Alert: Attempted to delete a directory! Activity logged."
            )

    async def move_to_safe_zone(self, file_id: UUID):
        q_path = self.get_quarantine_path(file_id)
        s_path = self.get_safe_path(file_id)

        async_q_path = AsyncPath(q_path)
        async_s_path = AsyncPath(s_path)

        if await async_s_path.exists():
            raise FileExistsError(
                f"Conflict: File already exists in safe zone at {file_id}"
            )

        await async_s_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            await async_q_path.rename(s_path)
        except FileNotFoundError:
            raise FileNotFoundError("Security Alert: File not found in quarantine.")
        except IsADirectoryError:
            raise ValueError("Security Alert: Target is a directory, not a file.")

        return s_path


store_service = StoreService()
