# app/services/user_service.py
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.exceptions import UserNotFoundError

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def update_user_profile(self, user_id: int, user_update: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate_user(self, user_id: int) -> User:
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
