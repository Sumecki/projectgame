from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from app.core.db.database import get_db
from app.core.domain.models.game import Game
from app.core.domain.models.user import User
from app.core.domain.schemas.game import (
    GameResponse,
    GameSearchResult,
    GeneratedGameDescriptionResponse,
)
from app.core.repository.game_repository import GameRepository
from app.core.services.bedrock_description_service import BedrockDescriptionService
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


@game_router.post(
    "/{game_id}/b-movie-description",
    response_model=GeneratedGameDescriptionResponse,
)
def generate_b_movie_description(
    game_id: UUID,
    _current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    bedrock_service: BedrockDescriptionService = Depends(BedrockDescriptionService),
) -> GeneratedGameDescriptionResponse:
    game = game_service.get_game_by_game_id(game_id)

    generated_description = bedrock_service.rewrite_description_as_b_movie_plot(
        game_name=game.name,
        game_description=game.description,
    )

    return GeneratedGameDescriptionResponse(
        game_id=game.id,
        game_name=game.name,
        generated_description=generated_description,
    )
