from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from app.core.db.database import get_db
from app.core.domain.models.favorite_game import FavoriteGame
from app.core.domain.models.user import User
from app.core.domain.schemas.favorite_game import (
    FavoriteGameResponse,
    MostPopularGameResponse,
)
from app.core.repository.favorite_game_repository import FavoriteGameRepository
from app.core.repository.game_repository import GameRepository
from app.core.services.favorite_game_service import FavoriteGameService

favorite_game_router = APIRouter(
    prefix="/favorite-games",
    tags=["favorite-games"],
)


def get_favorite_game_service(db: Session = Depends(get_db)) -> FavoriteGameService:
    return FavoriteGameService(
        favorite_game_repository=FavoriteGameRepository(db),
        game_repository=GameRepository(db),
    )


@favorite_game_router.get(
    "/most-popular",
    response_model=MostPopularGameResponse,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "No favorite games exist",
        },
    },
)
def get_most_popular_game(
    favorite_game_service: FavoriteGameService = Depends(get_favorite_game_service),
) -> MostPopularGameResponse | Response:
    result = favorite_game_service.get_most_popular_game()

    if result is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return result


@favorite_game_router.post(
    "/{game_id}",
    response_model=FavoriteGameResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_favorite_game(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    favorite_game_service: FavoriteGameService = Depends(get_favorite_game_service),
) -> FavoriteGame:
    return favorite_game_service.add_favorite_game(
        user_id=current_user.id,
        game_id=game_id,
    )


@favorite_game_router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_favorite_game(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    favorite_game_service: FavoriteGameService = Depends(get_favorite_game_service),
) -> None:
    favorite_game_service.remove_favorite_game(user_id=current_user.id, game_id=game_id)


@favorite_game_router.get(
    "",
    response_model=list[FavoriteGameResponse],
)
def get_favorite_games(
    current_user: User = Depends(get_current_user),
    favorite_game_service: FavoriteGameService = Depends(get_favorite_game_service),
) -> list[FavoriteGame]:
    return favorite_game_service.get_user_favorite_games(user_id=current_user.id)
