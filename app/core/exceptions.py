from uuid import UUID


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class TokenValidationError(Exception):
    pass


class GameNotFoundError(Exception):
    pass


class InvalidRawgResponseError(Exception):
    pass


class FavoriteGameDuplicateError(Exception):
    pass


class FavoriteGameNotFoundError(Exception):
    pass


class GameAlreadyExistsError(Exception):
    def __init__(self, game_id: UUID) -> None:
        self.game_id = game_id
        super().__init__("Game already exists")


class GameDescriptionNotAvailableError(Exception):
    pass


class BedrockGenerationError(Exception):
    pass
