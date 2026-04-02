from enum import Enum


class PermissionName(str, Enum):
    EDIT = "Edit"
    VIEW = "View"
    DELETE = "Delete"
    MANAGE_USERS = "Manage_Users"
    ASSIGN_ROLES = "Assign_Roles"


class KnowledgeStatus(str, Enum):
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
