import logging
from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request
from .jinja import templates
from fastapi.responses import RedirectResponse
from anyblok.registry import Registry
from fastapi import Security
from datetime import timedelta
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from fastapi import HTTPException, status

from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management.bloks.http_auth_base.auth_api import (
    create_access_token,
)
from fastapi import APIRouter

from .fastapi_utils import (
    get_authenticated_musician,
    _get_musician_from_token,
    _prepare_context,
    RenewTokenRoute,
)
from band_management import config


logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["main"],
    responses={404: {"description": "Not found :cry:"}},
    route_class=RenewTokenRoute,
)


@router.get(
    "/",
)
def index(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
):
    """Get the list of company"""
    if token_data:
        response = RedirectResponse(
            "/home",
            status_code=200,
            headers={
                # "Content-Language": user.musician.lang,
                "HX-Redirect": "/home",
            },
        )
        return response
    return templates.TemplateResponse(name="index.html", request=request, context={})


@router.get(
    "/login",
)
def login(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=[])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    if token_data:
        response = RedirectResponse(
            "/home",
            status_code=200,
            headers={
                # "Content-Language": user.musician.lang,
                "HX-Redirect": "/home",
            },
        )
        return response
    return templates.TemplateResponse(
        name="login.html", request=request, context={"error_message": None}
    )


@router.post(
    "/login",
)
def login_post(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    anyblok_registry: Annotated["Registry", Depends(get_registry)],
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
            create_access_token(
                data=user.get_access_token_data(),
                expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
            ),
            max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=True,
            httponly=True,
            samesite="strict",
        )
        return response


@router.post(
    "/logout",
)
def logout(
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


@router.get(
    "/home",
)
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


@router.put(
    "/musician/{musician_uuid}/toggle-active-band/{band_uuid}",
)
def toggle_musician_active_band(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    musician_uuid: str,
    band_uuid: str,
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
                # "HX-Redirect": "/bands/",
                "HX-Refresh": "true",
            },
        )


@router.get(
    "/profile",
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


@router.get(
    "/credits",
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


@router.get(
    "/terms",
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


@router.get(
    "/register",
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
