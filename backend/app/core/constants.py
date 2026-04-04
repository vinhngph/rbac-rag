from enum import Enum


class PermissionName(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class KnowledgeStatus(str, Enum):
    SCANNING = "scanning"
    SAFE = "safe"

    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"

    COMPLETED = "completed"
    FAILED = "failed"


class FileType(str, Enum):
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"


MAGIC_BYTES_RULES = {
    FileType.PDF: b"%PDF-",
    FileType.PNG: b"\x89PNG\r\n\x1a\n",
    FileType.JPG: b"\xff\xd8\xff",
    FileType.JPEG: b"\xff\xd8\xff",
}
