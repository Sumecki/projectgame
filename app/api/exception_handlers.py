from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    BedrockGenerationError,
    FavoriteGameDuplicateError,
    FavoriteGameNotFoundError,
    GameAlreadyExistsError,
    GameDescriptionNotAvailableError,
    GameNotFoundError,
    InvalidCredentialsError,
    InvalidRawgResponseError,
    TokenValidationError,
    UserAlreadyExistsError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(
        _request: Request,
        exc: UserAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        _request: Request,
        exc: InvalidCredentialsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(TokenValidationError)
    async def token_validation_handler(
        _request: Request,
        exc: TokenValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(GameNotFoundError)
    async def game_not_found_handler(
        _request: Request,
        exc: GameNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidRawgResponseError)
    async def invalid_rawg_response_handler(
        _request: Request,
        exc: InvalidRawgResponseError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(FavoriteGameDuplicateError)
    async def favorite_game_duplicate_handler(
        _request: Request,
        exc: FavoriteGameDuplicateError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(FavoriteGameNotFoundError)
    async def favorite_game_not_found_handler(
        _request: Request,
        exc: FavoriteGameNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(GameAlreadyExistsError)
    async def game_already_exists_handler(
        _request: Request,
        exc: GameAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(exc),
                "game_id": str(exc.game_id),
            },
        )

    @app.exception_handler(GameDescriptionNotAvailableError)
    async def game_description_not_available_handler(
        _request: Request,
        exc: GameDescriptionNotAvailableError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(BedrockGenerationError)
    async def bedrock_generation_error_handler(
        _request: Request,
        exc: BedrockGenerationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )
