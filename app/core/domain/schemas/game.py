from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GameResponse(BaseModel):
    id: UUID
    rawg_id: int
    name: str
    description: str | None = None
    genres: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class GameSearchResult(BaseModel):
    rawg_id: int
    name: str
    released: str | None = None
