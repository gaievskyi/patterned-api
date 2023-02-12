from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from src.core.security import get_password_hash, verify_password
from .base import CRUD
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUD[User, UserCreate, UserUpdate]):

    def get_by_email(self, session: Session, *, email: str) -> Optional[User]:
        return session.query(User).filter(User.email == email).first()

    def create(self, session: Session, *, payload: UserCreate) -> User:
        model = User(
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            full_name=payload.full_name,
            is_superuser=payload.is_superuser,
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    def update(
        self, session: Session, *, model: User, payload: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(payload, dict):
            update_data = payload
        else:
            update_data = payload.dict(exclude_unset=True)

        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(session, model=model, payload=update_data)

    def authenticate(self, session: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(session, email=email)

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
