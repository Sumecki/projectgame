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
    pass
