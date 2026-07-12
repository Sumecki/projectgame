from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db.database import get_db
from app.core.domain.models.game import Game
from app.core.domain.schemas.game import GameResponse, GameSearchResult
from app.core.repository.game_repository import GameRepository
from app.core.services.game_service import GameService
from app.core.services.rawg_client import RawgApiClient

game_router = APIRouter()


@game_router.get(
    "/search",
    response_model=list[GameSearchResult],
)
async def search_games(
    query: Annotated[str, Query(min_length=2)], db: Session = Depends(get_db)
) -> list[GameSearchResult]:
    game_repository = GameRepository(db)
    rawg_client = RawgApiClient()
    game_service = GameService(
        game_repository=game_repository,
        rawg_client=rawg_client,
    )
    return await game_service.search_games_from_rawg(query=query)


@game_router.get(
    "/rawg/{rawg_id}",
    response_model=GameResponse,
)
async def get_game_details(
    rawg_id: int,
    db: Session = Depends(get_db),
) -> Game:
    game_repository = GameRepository(db)
    rawg_client = RawgApiClient()
    game_service = GameService(
        game_repository=game_repository,
        rawg_client=rawg_client,
    )
    return await game_service.get_or_create_game_by_rawg_id(rawg_id)
