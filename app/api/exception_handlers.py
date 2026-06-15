from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError


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
