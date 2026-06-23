from app.auth.security import hash_password, verify_password
from app.core.domain.models.user import User
from app.core.domain.schemas.user import UserCreate, UserLogin
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.repository.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, user_data: UserCreate) -> User:
        if self.user_repository.get_user_by_email(str(user_data.email)):
            raise UserAlreadyExistsError("Email already exists")
        if self.user_repository.get_user_by_username(user_data.username):
            raise UserAlreadyExistsError("Username already exists")

        user = User(
            username=user_data.username,
            email=str(user_data.email),
            hashed_password=hash_password(user_data.password),
        )
        return self.user_repository.create_user(user)

    def authenticate_user(self, login_data: UserLogin) -> User:
        user = self.user_repository.get_user_by_email(str(login_data.email))

        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(login_data.password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        return user

    def get_user_by_email(self, email: str) -> User | None:
        return self.user_repository.get_user_by_email(str(email))
