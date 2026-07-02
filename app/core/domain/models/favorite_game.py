from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import UUID as sqlUUID
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base


class FavoriteGame(Base):
    __tablename__ = "favorite_games"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "game_id",
            name="uq_favorite_games_user_id_game_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        sqlUUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid4,
        init=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        sqlUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id: Mapped[UUID] = mapped_column(
        sqlUUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(UTC),
        init=False,
    )
