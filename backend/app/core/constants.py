from enum import Enum


class PermissionName(str, Enum):
    EDIT = "Edit"
    VIEW = "View"
    DELETE = "Delete"
    MANAGE_USERS = "Manage_Users"
    ASSIGN_ROLES = "Assign_Roles"
