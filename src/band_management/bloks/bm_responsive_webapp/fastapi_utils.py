import logging
from typing import Annotated, Optional
from fastapi import Depends, Request
from fastapi.security import (
    SecurityScopes,
)
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import ValidationError

from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)

from band_management.config import SECRET_KEY, ALGORITHM


logger = logging.getLogger(__name__)


class CookieAuth:
    async def __call__(self, request: Request) -> Optional[str]:
        return request.cookies.get("auth-token")


async def get_authenticated_musician(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(CookieAuth())]
) -> Optional[TokenDataSchema]:
    token_data = None

    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_data = TokenDataSchema(**payload)
        except (JWTError, ValidationError) as err:
            logger.warning("Ignoring error %r", err)

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    for scope in security_scopes.scopes:
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return token_data


def _get_musician_from_token(anyblok, token_data):
    musician = None
    if token_data:
        user = anyblok.Auth.User.query().get(token_data.sub)
        if user:
            musician = user.musician
        if not musician:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
            )
    return musician


def _prepare_context(anyblok, request, token_data):
    musician = _get_musician_from_token(anyblok, token_data)
    return {
        "is_authenticated": True if musician else False,
        "musician": musician,
    }
