import logging
from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form, Query
from .jinja import templates
from fastapi.responses import RedirectResponse
from anyblok.registry import Registry
from fastapi import Security
from datetime import timedelta
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from band_management import _t
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
    parse_jwt_token,
    check_csrf,
)
from band_management import config


logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["main"],
    responses={404: {"description": _t("Not found :cry:")}},
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
            status_code=302,
            headers={
                # "Content-Language": user.musician.lang,
                "HX-Redirect": "/home",
            },
        )
        return response
    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={
            **_prepare_context(None, request, token_data),
        },
    )


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
            status_code=302,
            headers={
                # "Content-Language": user.musician.lang,
                "HX-Redirect": "/home",
            },
        )
        return response
    return templates.TemplateResponse(
        name="login.html",
        request=request,
        context={**_prepare_context(None, request, token_data), "error_message": None},
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
                context={
                    **_prepare_context(None, request, None),
                    "error_message": _t("Incorrect authentication"),
                },
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
        musician = _get_musician_from_token(anyblok, token_data)
        languages = {
            "fr": _t("French", lang=musician.lang),
            "en": _t("English", lang=musician.lang),
        }
        return templates.TemplateResponse(
            name="profile.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "languages": languages,
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
    if token_data:
        response = RedirectResponse(
            "/home",
            status_code=302,
            headers={
                "HX-Redirect": "/home",
            },
        )
        return response
    with registry_transaction(ab_registry) as anyblok:
        user_context = _prepare_context(anyblok, request, token_data)
        languages = {
            "fr": _t("French", lang=user_context["lang"]),
            "en": _t("English", lang=user_context["lang"]),
        }
        return templates.TemplateResponse(
            name="register.html",
            request=request,
            context={
                **user_context,
                "invited_musician": anyblok.BandManagement.Musician(
                    lang=user_context["lang"]
                ),
                "languages": languages,
            },
        )


@router.get(
    "/user/reset-password",
)
def reset_password_page(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    invitation_token: Annotated[str, Query()],
    ab_registry: "Registry" = Depends(get_registry),
):
    """Used to reset own password or create user account when invited"""
    with registry_transaction(ab_registry) as anyblok:
        data = parse_jwt_token(invitation_token)
        user = anyblok.Auth.User.query().get(data.sub)
        if not user:
            return RedirectResponse(
                request.base_url,
                status_code=401,
                headers={
                    "HX-Redirect": "/",
                },
            )

        return templates.TemplateResponse(
            name="reset-password.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "invited_musician": user.musician,
                "invitation_token": invitation_token,
            },
        )


@router.post(
    "/user/reset-password",
)
def reset_password(
    request: Request,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    csrf: check_csrf,
    invitation_token: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_confirmation: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        data = parse_jwt_token(invitation_token)
        Auth = anyblok.Auth
        invited_user = Auth.User.query().get(data.sub)
        if password != password_confirmation:
            return templates.TemplateResponse(
                name="reset-password.html",
                status_code=400,
                request=request,
                context={
                    **_prepare_context(anyblok, request, token_data),
                    "invited_musician": invited_user.musician,
                    "invitation_token": invitation_token,
                    "error_message": _t(
                        "Password mismatched !", lang=invited_user.musician.lang
                    ),
                },
            )

        for cred in (
            Auth.CredentialStore.query()
            .filter_by(user=invited_user, label="main")
            .all()
        ):
            cred.delete()
        Auth.CredentialStore.insert(
            label="main",
            key=invited_user.musician.email,
            secret=password,
            user=invited_user,
        )
        invited_user.invitation_token = None
        invited_user.invitation_token_expiration_date = None
        response = RedirectResponse(
            "/login",
            status_code=200,
            headers={
                # "Content-Language": user.musician.lang,
                "HX-Redirect": "/login",
            },
        )
        return response
