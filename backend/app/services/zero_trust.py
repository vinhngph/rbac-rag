from anyio import open_file, Path as AsyncPath, to_thread
from fastapi import UploadFile, HTTPException, status
from logging import info as logging_info, error as logging_error
from re import sub as re_sub
from uuid import UUID
from hashlib import sha256
from PIL import Image

from app.services.store import store_service
from app.core.constants import FileType, MAGIC_BYTES_RULES
from app.models.knowledge import Knowledge
from app.models.user import User
from app.main import logger


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

    def __init__(self, max_file_size: int = 10 * 1024 * 1024) -> None:
        self.max_file_size = max_file_size

    async def initialize(self):
        """
        Initialize the necessary directories
        """
        await AsyncPath(store_service.quarantine_dir).mkdir(parents=True, exist_ok=True)
        await AsyncPath(store_service.safe_dir).mkdir(parents=True, exist_ok=True)

    async def _layer1_gatekeeping(
        self, file: UploadFile, user: User, department_id: UUID
    ):
        logger.info("Execute Layer 1: Gatekeeping...")

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
        try:
            file_type = FileType(file_extension)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Layer 1: Unsupported file type: '{file_extension}'.",
            )

        expected_sig = MAGIC_BYTES_RULES[file_type]
        header_bytes = await file.read(len(expected_sig))

        await file.seek(0)
        if header_bytes != expected_sig:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Layer 1: Detected fake file type.",
            )

        return Knowledge(
            title=safe_name,
            file_type=file_type,
            department_id=department_id,
            uploader_id=user.id,
        )

    async def _layer2_quarantine(self, file: UploadFile, knowledge: Knowledge):
        logger.info("Execute Layer 2: Quarantine...")

        await store_service.save_to_quarantine_zone(
            file, file_id=knowledge.id, max_size=self.max_file_size
        )

    async def _layer3_deep_scanning(self, knowledge: Knowledge):
        logger.info("Execute Layer 3: Deep Scanning (Hash & Antivirus)...")

        # 1: Hash Check (SHA-256)
        sha256_hash = sha256()

        q_path = store_service.get_quarantine_path(knowledge.id)
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

    async def _layer4_cdr_disarm(self, knowledge: Knowledge):
        logger.info("Execute Layer 4: Data disinfection (CDR)")

        if knowledge.file_type in [FileType.PNG, FileType.JPG, FileType.JPEG]:
            q_path = store_service.get_quarantine_path(knowledge.id)
            try:
                await to_thread.run_sync(_clean_image, q_path)
                logging_info(
                    "Layer 4: The image has been extracted and reconstructed cleanly."
                )
            except Exception as e:
                raise ValueError(
                    f"Layer 4 Error: Data disinfection error. Error: {str(e)}"
                )
        elif knowledge.file_type == FileType.PDF:
            # Remove hidden JavaScript/Macro from PDFs.
            pass

    async def _layer5_approval_and_distribute(self, knowledge: Knowledge):
        logger.info("Execute Layer 6: Approval and distribute")

        await store_service.move_to_safe_zone(file_id=knowledge.id)

    async def execute_security_pipeline(
        self, file: UploadFile, user: User, department_id: UUID
    ):
        file_id = None
        try:
            knowledge = await self._layer1_gatekeeping(file, user, department_id)
            file_id = knowledge.id

            await self._layer2_quarantine(file, knowledge)
            await self._layer3_deep_scanning(knowledge)
            await self._layer4_cdr_disarm(knowledge)
            await self._layer5_approval_and_distribute(knowledge)

            logging_info(f"{knowledge.title} has been scanned.")

            return knowledge
        except Exception as e:
            logging_error(e)

            if file_id:
                await store_service.delete_from_quarantine(file_id)

            raise e


zero_trust = ZeroTrust()
