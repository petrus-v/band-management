from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form
from .jinja import templates
from fastapi.responses import RedirectResponse
from anyblok.registry import Registry
from fastapi import Security

from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management.bloks.bm_responsive_webapp.main import (
    get_authenticated_musician,
    _prepare_context,
    _get_musician_from_token,
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


def band(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    band_uuid: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        return templates.TemplateResponse(
            name="band-update.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "band": band,
            },
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
        BM = anyblok.BandManagement
        BM.Band.insert(name=band_name)
    return RedirectResponse(
        "/bands",
        status_code=201,
        headers={
            "HX-Redirect": "/bands",
        },
    )


def update_band(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    band_uuid: str,
    band_name: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        band.name = band_name
    return RedirectResponse(
        "/bands",
        status_code=200,
        headers={
            "HX-Redirect": "/bands",
        },
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
