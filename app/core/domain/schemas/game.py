import uuid

from pydantic import BaseModel, ConfigDict


class GameResponse(BaseModel):
    id: uuid.UUID
    rawg_id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
