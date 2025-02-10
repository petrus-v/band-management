from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from pydantic_extra_types.language_code import LanguageAlpha2
from band_management.bloks.http_auth_base.schemas.base import BMBaseModel, RefSchema


class MusicianSchema(BMBaseModel):
    name: str
    lang: LanguageAlpha2
    email: EmailStr


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    sub: str | UUID | None = None
    exp: int | None = None
    scopes: list[str] = Field(default_factory=lambda: [])


class UserSchema(BMBaseModel):
    musician: RefSchema | MusicianSchema | None = None
