import logging
from typing import Annotated, Optional
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request
from .jinja import templates
from fastapi.responses import RedirectResponse
from anyblok.registry import Registry
from fastapi import Security
from datetime import timedelta
from fastapi.security import (
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import ValidationError

from band_management.bloks.http_auth_base.auth_api import SECRET_KEY, ALGORITHM
from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management.bloks.http_auth_base.auth_api import (
    create_access_token,
)

ACCESS_TOKEN_EXPIRE_MINUTES = 60


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


def index(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    ab_registry: "Registry" = Depends(get_registry),
):
    """Get the list of company"""
    with registry_transaction(ab_registry):
        return templates.TemplateResponse(
            name="index.html", request=request, context={}
        )


def login(
    request: Request,
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry):
        pass
    return templates.TemplateResponse(
        name="login.html", request=request, context={"error_message": None}
    )


def login_post(
    request: Request,
    anyblok_registry: Annotated["Registry", Depends(get_registry)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """Authentication end point"""
    with registry_transaction(anyblok_registry) as anyblok:
        user = anyblok.Auth.authenticate(form_data.username, form_data.password)
        if not user:
            return templates.TemplateResponse(
                name="login.html",
                status_code=401,
                request=request,
                context={"error_message": "Incorrect authentication"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=user.get_access_token_data(),
            expires_delta=access_token_expires,
        )
        response = RedirectResponse(
            "/home",
            status_code=202,
            headers={
                # "Content-Language": user.musician.lang,
                "HX-Redirect": "/home",
            },
        )
        response.set_cookie(
            "auth-token",
            access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=True,
            httponly=True,
            samesite="strict",
        )
        return response


def logout_post(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    anyblok_registry: Annotated["Registry", Depends(get_registry)],
):
    response = RedirectResponse(
        "/",
        status_code=200,
        headers={
            "HX-Redirect": "/",
        },
    )
    response.delete_cookie("auth-token")
    return response


def home(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="home.html",
            request=request,
            context={**_prepare_context(anyblok, request, token_data)},
        )


def toggle_musician_active_band(
    musician_uuid: str,
    band_uuid: str,
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        if musician_uuid != str(musician.uuid):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your are not allowed to update other user active bands",
            )

        musician.toggle_musician_active_band(band_uuid)
        return RedirectResponse(
            request.headers.get("HX-Current-URL", "/"),
            status_code=201,
            headers={
                # "HX-Redirect": "/bands",
                "HX-Refresh": "true",
            },
        )


def profile(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="profile.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
            },
        )


def credits(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        pass
    return templates.TemplateResponse(
        name="credits.html",
        request=request,
        context={**_prepare_context(anyblok, request, token_data)},
    )


def terms(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="terms.html",
            request=request,
            context={**_prepare_context(anyblok, request, token_data)},
        )


def register(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="register.html",
            request=request,
            context={**_prepare_context(anyblok, request, token_data)},
        )
