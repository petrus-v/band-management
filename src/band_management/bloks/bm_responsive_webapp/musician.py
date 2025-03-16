from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form, APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from .jinja import templates
from anyblok.registry import Registry
from fastapi import Security

from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management.bloks.bm_responsive_webapp.fastapi_utils import (
    get_authenticated_musician,
    _prepare_context,
    _get_musician_from_token,
    RenewTokenRoute,
)
from contextlib import contextmanager


from fastapi.responses import HTMLResponse


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
    modal_mode: bool = False,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        future_musician = BM.Musician(name=musician_name or "Musician name")
        band = None
        if band_uuid:
            band = BM.Band.query().get(band_uuid)
        # template = "musician-prepare.html"
        # if modal_mode:
        template = "musicians/prepare-modal.html"

        return templates.TemplateResponse(
            name=template,
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "invited_musician": future_musician,
                "modal_mode": modal_mode,
                "band": band,
            },
        )


@router.post(
    "/",
    response_class=HTMLResponse | RedirectResponse,
)
def add_musician(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    musician_name: Annotated[str, Form()],
    musician_email: Annotated[str, Form()],
    musician_lang: Annotated[str, Form()] = "en",
    band_uuid: Annotated[str, Form()] = "",
    modal_mode: Annotated[bool, Form()] = False,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        new_musician = BM.Musician.insert(
            name=musician_name,
            email=musician_email,
            lang=musician_lang,
        )
        return templates.TemplateResponse(
            name="musicians/musician-field-selection.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "invited_musician": new_musician,
                "band": BM.Band.query().get(band_uuid) if band_uuid else None,
            },
        )
