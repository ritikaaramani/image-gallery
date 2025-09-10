from app.modules.users.schemas import User as UserSchema

def can_change_settings(user: UserSchema) -> bool:
    return user.is_admin
