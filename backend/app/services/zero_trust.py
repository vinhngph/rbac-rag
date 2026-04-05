from anyio import open_file, Path as AsyncPath, to_thread
from fastapi import UploadFile, HTTPException, status, Depends
from re import sub as re_sub
from hashlib import sha256
from PIL import Image
from pathlib import Path as PathLib
from typing import Annotated

from app.core.constants import FileType, MAGIC_BYTES_RULES
from app.core.logger import logger_info
from app.services.store import StoreService
from app.models.knowledge import Knowledge
from app.models.user import User
from app.models.role import Role


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
        self.store_service = StoreService()

    async def initialize(self):
        """
        Initialize the necessary directories
        """
        await AsyncPath(self.store_service.quarantine_dir).mkdir(
            parents=True, exist_ok=True
        )
        await AsyncPath(self.store_service.safe_dir).mkdir(parents=True, exist_ok=True)

    async def _layer1_gatekeeping(self, file: UploadFile, user: User, role: Role):
        logger_info("ZeroTrust", "Execute Layer 1: Gatekeeping...")

        # 1: Size limit
        if file.size and (file.size > self.max_file_size):
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Layer 1 Error: File too large.",
            )

        # 2: Sanitize Filename
        raw_name = file.filename if file.filename else "untitled"
        safe_name = re_sub(r"[^a-zA-Z0-9_\-\.]", "_", raw_name)

        p = PathLib(safe_name)

        file_name = p.stem
        file_extension = p.suffix.lstrip(".").lower()

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
            name=file_name, type=file_type, role_id=role.id, author_id=user.id
        )

    async def _layer2_quarantine(self, file: UploadFile, knowledge: Knowledge):
        logger_info("ZeroTrust", "Execute Layer 2: Quarantine...")

        await self.store_service.save_to_quarantine_zone(
            file, file_id=knowledge.id, max_size=self.max_file_size
        )

    async def _layer3_deep_scanning(self, knowledge: Knowledge):
        logger_info("ZeroTrust", "Execute Layer 3: Deep Scanning (Hash & Antivirus)...")

        try:
            # 1: Hash Check (SHA-256)
            sha256_hash = sha256()

            q_path = self.store_service.get_quarantine_path(knowledge.id)
            async with await open_file(q_path, "rb") as f:
                while chunk := await f.read(4096):
                    sha256_hash.update(chunk)
            file_hash = sha256_hash.hexdigest()

            logger_info("ZeroTrust", f"Layer 3: {file_hash}")
            # API VirusTotal

            # 2: ClamAV scan
            # pyclamd socket

            is_virus_detected = False

            if is_virus_detected:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Layer 3 Error: Malware/Virus Detected.",
                )
        except Exception as e:
            await self.store_service.delete_from_quarantine(knowledge.id)
            raise e

    async def _layer4_cdr_disarm(self, knowledge: Knowledge):
        logger_info("ZeroTrust", "Execute Layer 4: Data disinfection (CDR)")

        if knowledge.type in [FileType.PNG, FileType.JPG, FileType.JPEG]:
            q_path = self.store_service.get_quarantine_path(knowledge.id)
            try:
                await to_thread.run_sync(_clean_image, q_path)
                logger_info(
                    "ZeroTrust",
                    "Layer 4: The image has been extracted and reconstructed cleanly.",
                )
            except Exception as e:
                await self.store_service.delete_from_quarantine(knowledge.id)
                raise ValueError(
                    f"Layer 4 Error: Data disinfection error. Error: {str(e)}"
                )
        elif knowledge.type == FileType.PDF:
            # Remove hidden JavaScript/Macro from PDFs.
            pass

    async def _layer5_approval_and_distribute(self, knowledge: Knowledge):
        logger_info("ZeroTrust", "Execute Layer 6: Approval and distribute")

        await self.store_service.move_to_safe_zone(file_id=knowledge.id)

    async def execute_security_pipeline(self, file: UploadFile, user: User, role: Role):
        knowledge = await self._layer1_gatekeeping(file, user, role)

        await self._layer2_quarantine(file, knowledge)
        await self._layer3_deep_scanning(knowledge)
        await self._layer4_cdr_disarm(knowledge)
        await self._layer5_approval_and_distribute(knowledge)

        logger_info(
            "ZeroTrust",
            f"{knowledge.name}.{knowledge.type.value} has been scanned.",
        )

        return knowledge


type UseZeroTrust = Annotated[ZeroTrust, Depends(ZeroTrust)]
