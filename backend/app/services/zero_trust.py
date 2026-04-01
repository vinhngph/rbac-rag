from anyio import open_file, Path as AsyncPath, to_thread
from fastapi import UploadFile, HTTPException, status
from logging import info as logging_info, error as logging_error
from re import sub as re_sub
from uuid import uuid4, UUID
from hashlib import sha256
from PIL import Image
from pydantic import BaseModel

from app.services.store import store_service
from app.core.types import NonEmptyString


class FileMetadata(BaseModel):
    id: UUID
    name: NonEmptyString
    extension: str


def _clean_image(img_path: str):
    with Image.open(img_path) as img:
        mode = img.mode
        size = img.size
        img_format = img.format
        img_clean = Image.new(mode, size)
        img_clean.paste(img)
    img_clean.save(img_path, format=img_format)


class ZeroTrust:
    """
    The multi-layered defense system (Defense in Depth) applies the Zero Trust philosophy to file uploads.
    """

    def __init__(self) -> None:
        self.max_file_size = 10 * 1024 * 1024  # 10 MB
        self.allowed_magic_bytes = {
            "pdf": b"%PDF-",
            "png": b"\x89PNG\r\n\x1a\n",
            "jpg": b"\xff\xd8\xff",
            "jpeg": b"\xff\xd8\xff",
        }
        self.store = store_service

    async def initialize(self):
        """
        Initialize the necessary directories
        """
        await AsyncPath(self.store.quarantine_dir).mkdir(parents=True, exist_ok=True)
        await AsyncPath(self.store.safe_dir).mkdir(parents=True, exist_ok=True)

    async def _layer1_gatekeeping(self, file: UploadFile) -> FileMetadata:
        logging_info("Execute Layer 1: Gatekeeping...")

        # 1: Size limit
        if file.size and (file.size > self.max_file_size):
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Layer 1 Error: File too large.",
            )

        # 2: Sanitize Filename
        raw_name = file.filename if file.filename else "untitled"
        safe_name = re_sub(r"[^a-zA-Z0-9_\-\.]", "_", raw_name)
        file_extension = safe_name.split(".")[-1].lower() if "." in safe_name else ""

        # 3: True File Type
        if file_extension not in self.allowed_magic_bytes:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Layer 1: Unsupported file type.",
            )
        expected_sig = self.allowed_magic_bytes[file_extension]
        header_bytes = await file.read(len(expected_sig))
        await file.seek(0)

        if header_bytes != expected_sig:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Layer 1: Detected fake file type.",
            )

        return FileMetadata(id=uuid4(), name=safe_name, extension=file_extension)

    async def _layer2_quarantine(self, file: UploadFile, file_metadata: FileMetadata):
        logging_info("Execute Layer 2: Quarantine...")

        await store_service.save_to_quarantine_zone(
            file, file_id=file_metadata.id, max_size=self.max_file_size
        )

    async def _layer3_deep_scanning(self, file_metadata: FileMetadata):
        logging_info("Execute Layer 3: Deep Scanning (Hash & Antivirus)...")

        # 1: Hash Check (SHA-256)
        sha256_hash = sha256()

        q_path = self.store.get_quarantine_path(file_metadata.id)
        async with await open_file(q_path, "rb") as f:
            while chunk := await f.read(4096):
                sha256_hash.update(chunk)
        file_hash = sha256_hash.hexdigest()

        logging_info(f"File hash: {file_hash}")
        # API VirusTotal

        # 2: ClamAV scan
        # pyclamd socket

        is_virus_detected = False

        if is_virus_detected:
            raise Exception("Layer 3 Error: Malware/Virus Detected.")

    async def _layer4_cdr_disarm(self, file_metadata: FileMetadata):
        logging_info("Execute Layer 4: Data disinfection (CDR)")

        if file_metadata.extension in ["jpg", "jpeg", "png"]:
            q_path = self.store.get_quarantine_path(file_metadata.id)
            try:
                await to_thread.run_sync(_clean_image, q_path)
                logging_info(
                    "Layer 4: The image has been extracted and reconstructed cleanly."
                )
            except Exception as e:
                raise ValueError(
                    f"Layer 4 Error: Data disinfection error. Error: {str(e)}"
                )
        elif file_metadata.extension == "pdf":
            # Remove hidden JavaScript/Macro from PDFs.
            pass

    async def _layer5_approval_and_distribute(
        self, file_metadata: FileMetadata
    ) -> dict[str, str | dict[str, str]]:
        logging_info("Execute Layer 6: Approval and distribute")

        await self.store.move_to_safe_zone(file_id=file_metadata.id)

        safe_headers = {
            "Content-Disposition": f'attachment; filename="{file_metadata.name}"',
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none';",
        }

        return {
            "status": "safe",
            "safe_path": self.store.get_safe_path(file_id=file_metadata.id),
            "filename": file_metadata.name,
            "security_headers": safe_headers,
        }

    async def execute_security_pipeline(
        self, file: UploadFile
    ) -> dict[str, str | dict[str, str]]:
        file_id = None
        try:
            file_metadata = await self._layer1_gatekeeping(file)
            file_id = file_metadata.id

            await self._layer2_quarantine(file, file_metadata)
            await self._layer3_deep_scanning(file_metadata)
            await self._layer4_cdr_disarm(file_metadata)

            rs = await self._layer5_approval_and_distribute(file_metadata)

            logging_info(f"{file_metadata.name} has been scanned.")

            return rs
        except Exception as e:
            logging_error(e)

            if file_id:
                await self.store.delete_from_quarantine(file_id)

            raise e


zero_trust = ZeroTrust()
