import logging
from typing import Callable, Annotated, Optional

from fastapi import Request, Response, Form
from fastapi.routing import APIRoute

from fastapi import Depends
from fastapi.security import (
    SecurityScopes,
)
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import ValidationError
from band_management import _t, get_translations
from band_management.exceptions import ValidationError as BMValidationError
from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)

from band_management.bloks.http_auth_base.auth_api import (
    create_access_token,
)
from band_management import config


logger = logging.getLogger(__name__)


class CookieAuth:
    async def __call__(self, request: Request) -> Optional[str]:
        return request.cookies.get("auth-token")


def parse_jwt_token(token: str) -> TokenDataSchema:
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    return TokenDataSchema(**payload)


def csrf_token(
    minutes: int,
):
    return create_access_token(
        TokenDataSchema(sub="csrf"), expires_delta=timedelta(minutes=minutes)
    )


async def assert_valid_csrf_token(
    csrf_token: Annotated[str, Form()],
):
    token_data = parse_jwt_token(csrf_token)
    if token_data.sub != "csrf":
        raise BMValidationError(_t("Not a valid csrf token !"))
    return True


check_csrf = Annotated[bool, Depends(assert_valid_csrf_token)]


async def get_authenticated_musician(
    request: Request,
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(CookieAuth())],
) -> Optional[TokenDataSchema]:
    token_data = None

    if token:
        try:
            token_data = parse_jwt_token(token)
            token_expiry = datetime.fromtimestamp(token_data.exp, tz=timezone.utc)
            if datetime.now(tz=timezone.utc) >= (
                token_expiry - timedelta(minutes=config.ACCESS_TOKEN_RENEW_MINUTES)
            ):
                request.state.refreshed_auth_token = create_access_token(
                    data=token_data,
                    expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
                )
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
                detail=_t("Missing permissions"),
                headers={"WWW-Authenticate": authenticate_value},
            )

        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_t("Missing permissions"),
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
                detail=_t("Not enough permissions"),
            )
    return musician


def get_lang_from_headers(request: Request) -> str:
    accept_language = request.headers.get("accept-language", "en")  # Langue par défaut
    return accept_language.split(",")[0].split("-")[
        0
    ]  # Prend la première langue indiquée


def _prepare_context(anyblok, request, token_data):
    if anyblok is not None:
        musician = _get_musician_from_token(anyblok, token_data)
    else:
        musician = None

    if musician:
        lang = musician.lang
    else:
        lang = get_lang_from_headers(request)

    if lang not in config.AVAILABLE_LANGS:
        lang = config.DEFAULT_LANG
    translate = get_translations(lang)
    return {
        "is_authenticated": True if musician else False,
        "lang": lang,
        "musician": musician,
        "gettext": translate,  # support for {% trans %} using jinja2.ext.i18n
        "_t": translate,  # support for {{ _t() }} in templates
    }


class RenewTokenRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            if hasattr(request.state, "refreshed_auth_token"):
                response.set_cookie(
                    "auth-token",
                    request.state.refreshed_auth_token,
                    max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    secure=True,
                    httponly=True,
                    samesite="strict",
                )
            return response

        return custom_route_handler
