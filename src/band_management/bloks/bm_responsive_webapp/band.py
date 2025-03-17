import datetime

from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form, APIRouter
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

bands_router = APIRouter(
    prefix="/bands",
    tags=["band"],
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)
router = APIRouter(
    prefix="/band",
    tags=["band"],
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)


@bands_router.get(
    "/",
)
def bands(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="bands.html",
            request=request,
            context={**_prepare_context(anyblok, request, token_data)},
        )


@bands_router.post(
    "/",
)
def search_bands(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    search: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        bands_query = BM.Band.query()
        bands_query = bands_query.filter(BM.Band.name.ilike(f"%{search}%"))
        bands_query = bands_query.filter(BM.Band.uuid.in_(musician.active_bands.uuid))
        bands = bands_query.all()
        response = templates.TemplateResponse(
            name="bands/search-result.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "bands": bands,
                "search": search,
            },
        )
        return response


@router.get(
    "/prepare",
)
def prepare_band(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        band = BM.Band(name="Default Band")
        return templates.TemplateResponse(
            name="band-prepare.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "band": band,
            },
        )


@router.get(
    "/{band_uuid}",
)
def band(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    band_uuid: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        member = musician.member_of(band)
        if member and member.is_admin:
            return templates.TemplateResponse(
                name="band-update.html",
                request=request,
                context={
                    **_prepare_context(anyblok, request, token_data),
                    "band": band,
                },
            )
        return RedirectResponse(
            "/bands",
            status_code=401,
            headers={
                "HX-Redirect": "/bands/",
            },
        )


@router.get(
    "/{band_uuid}/invite",
)
def invite_band_member_page(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    band_uuid: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        member = musician.member_of(band)
        if member and member.is_admin:
            return templates.TemplateResponse(
                name="band-invite.html",
                request=request,
                context={
                    **_prepare_context(anyblok, request, token_data),
                    "band": band,
                    "now": datetime.datetime.now(tz=datetime.timezone.utc),
                },
            )
        return RedirectResponse(
            "/bands",
            status_code=401,
            headers={
                "HX-Redirect": "/bands/",
            },
        )


@router.post(
    "/{band_uuid}/invite",
)
def invite_band_member(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    band_uuid: str,
    musician_uuid: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        current_musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        current_musician.member_of(band)
        invited_musician = BM.Musician.query().get(musician_uuid)
        BM.Member.create_invitation_by(
            band=band,
            invited_musician=invited_musician,
            invited_by=current_musician,
        )
        return templates.TemplateResponse(
            name="band-invite.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "band": band,
                "now": datetime.datetime.now(tz=datetime.timezone.utc),
            },
        )


@router.post(
    "/",
)
def add_band(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    band_name: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        BM.Band.insert_by(musician, name=band_name)
    return RedirectResponse(
        "/bands",
        status_code=201,
        headers={
            "HX-Redirect": "/bands/",
        },
    )


@router.put(
    "/{band_uuid}",
)
def update_band(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    band_uuid: str,
    band_name: Annotated[str, Form()],
    administrators: Annotated[list[str], Form()] = [],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        band.update_by(musician, name=band_name)
        band.update_administrator_by(musician, administrators)
    return RedirectResponse(
        "/bands",
        status_code=200,
        headers={
            "HX-Redirect": "/bands/",
        },
    )
