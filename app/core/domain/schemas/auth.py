from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    access_token_expire: float


class TokenPayload(BaseModel):
    sub: str
    exp: float
