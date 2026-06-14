from app.auth.security import hash_password
from app.core.domain.models.user import User
from app.core.domain.schemas.user import UserCreate
from app.core.repository.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user_by_email(self, email: str) -> User | None:
        return self.user_repository.get_user_by_email(email)

    def register_user(self, user_data: UserCreate) -> User:
        if self.user_repository.get_user_by_email(user_data.email):
            raise ValueError("Email already exists")
        if self.user_repository.get_user_by_username(user_data.username):
            raise ValueError("Username already exists")

        user = User(
            username=user_data.username,
            email=str(user_data.email),
            hashed_password=hash_password(user_data.password),
        )
        return self.user_repository.create_user(user)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.user_repository.get_user_by_id(user_id)
