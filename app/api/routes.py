from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.auth import create_access_token, get_current_user
from app.core.db.database import get_db
from app.core.domain.models.user import User
from app.core.domain.schemas.auth import Token
from app.core.domain.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.repository.user_repository import UserRepository
from app.core.services.user_service import UserService

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"health": "ok"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)

    return user_service.register_user(user_data)


@router.post("/login", response_model=Token)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)

    user = user_service.authenticate_user(login_data)
    access_token, access_token_expire = create_access_token(user.email)

    return Token(
        access_token=access_token,
        access_token_expire=access_token_expire,
    )


@router.get(
    "/users/me",
    response_model=UserResponse,
)
def get_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
