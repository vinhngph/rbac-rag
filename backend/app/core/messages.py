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

    ACCESS_DENIED = "Access denied."

    MEMBER_ADD_ERROR = "Cannot add member."


class SystemMessages:
    DATABASE_SEED = (
        "System configuration error: Missing required permissions in database."
    )
