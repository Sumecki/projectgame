import pytest

from app.core.domain.schemas.user import UserCreate
from app.core.services.user_service import UserService


class InMemoryUserRepository:
    def __init__(self):
        self.users = []

    def get_user_by_email(self, email: str):
        return next((user for user in self.users if user.email == email), None)
    
    def get_user_by_username(self, username: str):
        return next((user for user in self.users if user.username == username), None)
    
    def create_user(self, user):
        self.users.append(user)
        return user
    

def test_register_user_creates_user():
    repository = InMemoryUserRepository()
    service = UserService(repository)

    user_data = UserCreate(
        username="John",
        email="jdoe@google.com",
        password="SecretPassword!",
    )

    user = service.register_user(user_data)

    assert user.username == "John"
    assert user.email == "jdoe@google.com"