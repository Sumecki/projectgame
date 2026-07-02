from uuid import UUID, uuid4

from sqlalchemy import UUID as sqlUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        sqlUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )

    username: Mapped[str] = mapped_column(unique=True)

    email: Mapped[str] = mapped_column(unique=True)

    hashed_password: Mapped[str] = mapped_column()
