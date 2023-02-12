from sqlalchemy.orm import Session

from src import crud, schemas
from src.core.config import settings
from src.db.base import Base
from src.db.session import engine


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)
