from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.database import get_db
from app.core.domain.models.game import Game
from app.core.domain.schemas.game import GameResponse, GameSearchResult
from app.core.repository.game_repository import GameRepository
from app.core.services.game_service import GameService
from app.core.services.rawg_client import RawgApiClient

game_router = APIRouter(prefix="/games", tags=["games"])


def get_game_service(db: Session = Depends(get_db)) -> GameService:
    return GameService(
        game_repository=GameRepository(db),
        rawg_client=RawgApiClient(),
    )


@game_router.get(
    "/search",
    response_model=list[GameSearchResult],
)
async def search_games(
    query: Annotated[str, Query(min_length=2)],
    game_service: GameService = Depends(get_game_service),
) -> list[GameSearchResult]:
    return await game_service.search_games_from_rawg(query=query)


@game_router.get(
    "/rawg/{rawg_id}",
    response_model=GameResponse,
)
def get_game_details(
    rawg_id: int,
    game_service: GameService = Depends(get_game_service),
) -> Game:
    return game_service.get_game_by_rawg_id(rawg_id)


@game_router.post(
    "/rawg/{rawg_id}",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_game_from_rawg(
    rawg_id: int,
    game_service: GameService = Depends(get_game_service),
) -> Game:
    return await game_service.create_game_from_rawg(rawg_id)
