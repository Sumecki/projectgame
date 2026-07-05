from uuid import UUID

from sqlalchemy.orm import Session

from app.core.domain.models.favorite_game import FavoriteGame


class FavoriteGameRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_favorite_game_by_user_id_and_game_id(
        self,
        user_id: UUID,
        game_id: UUID,
    ) -> FavoriteGame | None:
        return (
            self.session.query(FavoriteGame)
            .filter(
                FavoriteGame.user_id == user_id,
                FavoriteGame.game_id == game_id,
            )
            .first()
        )

    def get_favorite_games_by_user_id(self, user_id: UUID) -> list[FavoriteGame]:
        return (
            self.session.query(FavoriteGame)
            .filter(FavoriteGame.user_id == user_id)
            .all()
        )

    def create_favorite_game(self, favorite_game: FavoriteGame) -> FavoriteGame:
        self.session.add(favorite_game)
        self.session.commit()
        self.session.refresh(favorite_game)

        return favorite_game

    def delete_favorite_game(self, favorite_game: FavoriteGame) -> None:
        self.session.delete(favorite_game)
        self.session.commit()
