from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from src import crud, models, schemas
from src.api import deps
from src.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    session: Session = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(session, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    session: Session = Depends(deps.get_session),
    user_payload: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new user.
    """
    user = crud.user.get_by_email(session, email=user_payload.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = crud.user.create(session, obj_in=user_payload)

    if settings.EMAILS_ENABLED and user_payload.email:
        pass  # send_new_account_email(...)

    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    session: Session = Depends(deps.get_session),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_payload = schemas.UserUpdate(**current_user_data)

    if password is not None:
        user_payload.password = password
    if full_name is not None:
        user_payload.full_name = full_name
    if email is not None:
        user_payload.email = email

    user = crud.user.update(
        session, session_obj=current_user, obj_in=user_payload)

    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    session: Session = Depends(deps.get_session),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
def create_user_open(
    *,
    session: Session = Depends(deps.get_session),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create a new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )

    user = crud.user.get_by_email(session, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )

    user_payload = schemas.UserCreate(
        password=password, email=email, full_name=full_name)
    user = crud.user.create(session, obj_in=user_payload)

    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    session: Session = Depends(deps.get_session),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(session, id=user_id)

    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )

    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    session: Session = Depends(deps.get_session),
    user_id: int,
    user_payload: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(session, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    user = crud.user.update(session, session_obj=user, obj_in=user_payload)
    return user
