from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    rawg_id: Mapped[int] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column()
