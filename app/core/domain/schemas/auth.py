from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    access_token_expire: float


class TokenPayload(BaseModel):
    sub: str
    exp: float
