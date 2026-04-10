class ErrorMessages:
    ROLE_ACCESS_BLOCK = (
        "You do not belong to this department or have no assigned roles here."
    )
    MISSING_PERMISSIONS = "You do not have permission(s)."
    KNOWLEDGE_NOT_FOUND = "Knowledge not found."
    KNOWLEDGE_BLOCK = "Knowledge access denied."
    KNOWLEDGE_INVALID_MOVE = "Cannot move knowledge."

    DEPARTMENT_NOT_FOUND = "Department not found."

    ROLE_NOT_FOUND = "Role not found."
    ROLE_UPDATE_DENIED = "You cannot update this role."

    ACCESS_DENIED = "Access denied."

    MEMBER_ADD_ERROR = "Cannot add member."
    MEMBER_NOT_FOUND = "Member not found."
    MEMBER_ROLE_CONFLICT = "Member role conflict."

    USER_NOT_FOUND = "User not found."


class SystemMessages:
    DATABASE_SEED = (
        "System configuration error: Missing required permissions in database."
    )
