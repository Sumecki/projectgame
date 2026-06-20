from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.database import get_db
from app.core.domain.models.user import User
from app.core.domain.schemas.user import UserCreate, UserResponse
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

    return user_service(user_data)
