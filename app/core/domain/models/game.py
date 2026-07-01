import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column()

    rawg_id: Mapped[int] = mapped_column(unique=True)

    description: Mapped[str | None] = mapped_column(nullable=True)
