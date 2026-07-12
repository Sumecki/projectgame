from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db.database import get_db
from app.core.domain.schemas.game import GameResponse, GameSearchResult
from app.core.repository.game_repository import GameRepository
from app.core.services.game_service import GameService
from app.core.services.rawg_client import RawgApiClient

game_router = APIRouter()


def get_game_service(
    db: Annotated[Session, Depends(get_db)],
) -> GameService:
    game_repository = GameRepository(db)
    rawg_client = RawgApiClient()

    return GameService(
        game_repository=game_repository,
        rawg_client=rawg_client,
    )


@game_router.get(
    "/search",
    response_model=list[GameSearchResult],
)
async def search_games(
    query: Annotated[str, Query(min_length=2)],
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> list[GameSearchResult]:
    return await game_service.search_games_from_rawg(query=query)


@game_router.get(
    "/rawg/{rawg_id}",
    response_model=GameResponse,
)
async def get_game_details(
    rawg_id: int,
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameResponse:
    return game_service.get_or_create_game_by_rawg_id(rawg_id)
