from uuid import UUID, uuid4

from sqlalchemy import UUID as sqlUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(
        sqlUUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid4,
        init=False,
    )
    name: Mapped[str] = mapped_column()

    rawg_id: Mapped[int] = mapped_column(unique=True)

    description: Mapped[str | None] = mapped_column(nullable=True)
