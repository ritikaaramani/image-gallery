from enum import Enum
from app.modules.users.schemas import User as UserSchema

# Define roles
class Role(str, Enum):
    admin = "admin"
    editor = "editor"
    visitor = "visitor"

# Define permissions
class Permission(str, Enum):
    upload = "upload"
    edit = "edit"
    delete = "delete"
    publish = "publish"
    moderate_comments = "moderate_comments"

# Role-to-permission mapping
ROLE_PERMISSIONS = {
    Role.admin: {Permission.upload, Permission.edit, Permission.delete, Permission.publish, Permission.moderate_comments},
    Role.editor: {Permission.upload, Permission.edit, Permission.publish},
    Role.visitor: set()  # just viewing
}

# Check if user has a permission
def has_permission(user: UserSchema, permission: Permission) -> bool:
    if user.is_admin:
        return True
    return permission in ROLE_PERMISSIONS.get(user.role, set())
