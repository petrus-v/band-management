import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, TYPE_CHECKING, Optional
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from pydantic import ValidationError
from band_management.bloks.http_auth_base.schemas.auth import (
    TokenSchema,
    TokenDataSchema,
    UserSchema,
)
from band_management import config
from fastapi import APIRouter

if TYPE_CHECKING:
    from anyblok.registy import Registry as AnyblokRegistry

logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)


router_auth = APIRouter(
    tags=["api"],
    responses={404: {"description": "Not found"}},
)
api_user = APIRouter(
    prefix="/api/user",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


def create_access_token(data: TokenDataSchema, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    data.exp = int(expire.timestamp())
    encoded_jwt = jwt.encode(
        data.model_dump(mode="json"), config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> Optional[TokenDataSchema]:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        token_data = TokenDataSchema(**payload)
        if not token_data.sub:
            raise credentials_exception
    except (JWTError, ValidationError) as err:
        logger.warning("Ignoring error %r", err)
        raise credentials_exception

    # TODO: considering how we are trusting jwt token and if we want to revoke
    # token or changed scope before token expired

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return token_data


async def get_authenticated_user(
    token_data: Annotated[
        TokenDataSchema, Security(get_current_user, scopes=["musician-auth"])
    ],
) -> TokenDataSchema:
    return token_data


@router_auth.post(
    "/token",
    response_model=TokenSchema,
)
async def login_for_access_token(
    anyblok_registry: Annotated["AnyblokRegistry", Depends(get_registry)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenSchema:
    """Authentication end point"""
    with registry_transaction(anyblok_registry) as anyblok:
        user = anyblok.Auth.authenticate(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect authentication")
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=user.get_access_token_data(),
            expires_delta=access_token_expires,
        )
        return TokenSchema(access_token=access_token, token_type="bearer")


@api_user.get(
    "/me",
    response_model=UserSchema,
)
async def read_users_me(
    anyblok_registry: Annotated["AnyblokRegistry", Depends(get_registry)],
    token_data: Annotated[TokenDataSchema, Depends(get_authenticated_user)],
) -> UserSchema:
    with registry_transaction(anyblok_registry) as anyblok:
        return anyblok.Auth.User.query().get(token_data.sub)
