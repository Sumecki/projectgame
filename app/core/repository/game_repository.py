from uuid import UUID

from sqlalchemy.orm import Session

from app.core.domain.models.game import Game


class GameRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_game_by_rawg_id(self, rawg_id: int) -> Game | None:
        return self.session.query(Game).filter(Game.rawg_id == rawg_id).first()

    def get_game_by_id(self, game_id: UUID) -> Game | None:
        return self.session.query(Game).filter(Game.id == game_id).first()

    def create_game(self, game: Game) -> Game:
        self.session.add(game)
        self.session.commit()
        self.session.refresh(game)

        return game
