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
