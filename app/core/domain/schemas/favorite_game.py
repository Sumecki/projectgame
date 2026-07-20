from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.domain.schemas.game import GameResponse


class FavoriteGameResponse(BaseModel):
    id: UUID
    user_id: UUID
    game_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MostPopularGameResponse(BaseModel):
    game: GameResponse
    favorites_count: int
