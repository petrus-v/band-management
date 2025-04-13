import datetime
import logging

from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form, APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from .jinja import templates, NextAction
from anyblok.registry import Registry
from fastapi import Security

from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management import _t
from band_management import config
from band_management.bloks.bm_responsive_webapp.fastapi_utils import (
    get_authenticated_musician,
    _prepare_context,
    _get_musician_from_token,
    RenewTokenRoute,
    check_csrf,
)
from contextlib import contextmanager


from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

musicians_router = APIRouter(
    prefix="/musicians",
    tags=["musician"],
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)
router = APIRouter(
    prefix="/musician",
    tags=["musician"],
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)


@router.put(
    "/{musician_uuid}/toggle-active-band/{band_uuid}",
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
                detail=_t(
                    "Your are not allowed to update other user active bands",
                    lang=musician.lang,
                ),
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


@contextmanager
def _search_musicians(ab_registry, request, search, band_uuid, token_data):
    with registry_transaction(ab_registry) as anyblok:
        _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        musician_query = BM.Musician.query()
        if search:
            musician_query = musician_query.filter(
                BM.Musician.name.ilike(f"%{search}%"),
            )
        if band_uuid:
            # TODO: figureout why subquery not properly
            # works is it related to uuid7 ?? or query format?
            band = BM.Band.query().get(band_uuid)
            musician_query = musician_query.filter(
                ~BM.Musician.uuid.in_(
                    [str(m.uuid) for m in band.members.musician]
                    # BM.Member.query(BM.Member.musician_uuid).filter(
                    #     BM.Member.band_uuid==band_uuid
                    # )
                )
            )
        musician_query = musician_query.order_by(
            BM.Musician.name,
        )
        yield anyblok, musician_query


@musicians_router.post(
    "/dropdown",
)
def search_dropdown_musicians(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    search: Annotated[str, Form()],
    band_uuid: Annotated[str, Form()] = None,
    ab_registry: "Registry" = Depends(get_registry),
):
    with _search_musicians(
        ab_registry,
        request,
        search,
        band_uuid,
        token_data,
    ) as (anyblok, musicians):
        BM = anyblok.BandManagement
        band = None
        if band_uuid:
            band = BM.Band.query().get(band_uuid)
        response = templates.TemplateResponse(
            name="musicians/musician-field-selection-items.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "musicians": musicians.limit(7).all(),
                "search": search,
                "band": band,
            },
        )
        return response


@router.get(
    "/prepare",
)
def prepare_musician(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    musician_name: str = "",
    band_uuid: str | None = None,
    next_action: NextAction = NextAction.EDIT_MODAL_FROM_VIEW,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        future_musician = BM.Musician(
            name=musician_name or "Musician name", lang=musician.lang
        )
        band = None
        if band_uuid:
            band = BM.Band.query().get(band_uuid)

        # template = "musician-prepare.html"
        # if next_action == NextAction.EDIT_MODAL_FROM_VIEW:
        template = "musicians/prepare-modal.html"

        languages = {
            "fr": _t("French", lang=musician.lang),
            "en": _t("English", lang=musician.lang),
        }
        return templates.TemplateResponse(
            name=template,
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "invited_musician": future_musician,
                "band": band,
                "languages": languages,
            },
        )


@router.post(
    "/",
    response_class=HTMLResponse | RedirectResponse,
)
def add_musician(
    request: Request,
    csrf: check_csrf,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    musician_name: Annotated[str, Form()],
    musician_email: Annotated[str, Form()],
    musician_lang: Annotated[str, Form()] = "en",
    band_uuid: Annotated[str, Form()] = "",
    next_action: Annotated[NextAction, Form()] = NextAction.UPDATE_FIELD_SELECTION,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        # _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        if next_action == NextAction.UPDATE_FIELD_SELECTION:
            expiration_delta = datetime.timedelta(
                days=config.INVITATION_TOKEN_EXPIRE_DAYS
            )
        else:
            expiration_delta = datetime.timedelta(
                minutes=config.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES
            )
        new_musician = BM.Musician.insert(
            name=musician_name,
            email=musician_email,
            lang=musician_lang,
            invitation_token_delta=expiration_delta,
        )
        if next_action == NextAction.UPDATE_FIELD_SELECTION:
            return templates.TemplateResponse(
                name="musicians/musician-field-selection.html",
                request=request,
                context={
                    **_prepare_context(anyblok, request, token_data),
                    "invited_musician": new_musician,
                    "band": BM.Band.query().get(band_uuid) if band_uuid else None,
                },
            )
        return templates.TemplateResponse(
            name="register-confirmation.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "invited_musician": new_musician,
                "band": BM.Band.query().get(band_uuid) if band_uuid else None,
                "invitation_url": str(
                    request.base_url.replace(
                        path="user/reset-password"
                    ).replace_query_params(
                        invitation_token=new_musician.user.invitation_token
                    )
                ),
            },
        )


@router.put(
    "/{musician_uuid}",
    response_class=HTMLResponse | RedirectResponse,
)
def update_musician_profile(
    request: Request,
    csrf: check_csrf,
    token_data: Annotated[TokenDataSchema, Security(get_authenticated_musician)],
    musician_uuid: str,
    musician_name: Annotated[str, Form()],
    musician_lang: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        if musician_uuid != str(musician.uuid):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_t(
                    "Your are not allowed to update other musician profiles",
                    lang=musician.lang,
                ),
            )

        musician.update(
            name=musician_name,
            lang=musician_lang
            if musician_lang in config.AVAILABLE_LANGS
            else config.DEFAULT_LANG,
        )
        response = RedirectResponse(
            "/home",
            status_code=200,
            headers={
                "HX-Redirect": "/home",
            },
        )
        return response
