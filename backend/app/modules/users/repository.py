from sqlalchemy.orm import Session
from app.db.repository import BaseRepository
from app.modules.users.models import User, Role, Permission, UserRole, RolePermission

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)

class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: Session):
        super().__init__(Permission, db)
