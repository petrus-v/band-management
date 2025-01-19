from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form
from fastapi.templating import Jinja2Templates
from pathlib import Path
from anyblok import Declarations
from anyblok.registry import Registry

# from market_place.bloks.http_auth_base.auth_api import get_current_user

register = Declarations.register
Model = Declarations.Model

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def index(
    request: Request,
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    """Get the list of company"""
    with registry_transaction(ab_registry):
        pass
    return templates.TemplateResponse(name="index.html", request=request, context={})


def login(
    request: Request,
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry):
        pass
    return templates.TemplateResponse(name="login.html", request=request, context={})


def home(
    request: Request,
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry):
        pass
    return templates.TemplateResponse(name="home.html", request=request, context={})


def bands(
    request: Request,
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry):
        pass
    return templates.TemplateResponse(name="bands.html", request=request, context={})


def prepare_band(
    request: Request,
    ab_registry: "Registry" = Depends(get_registry),
):
    # import pdb; pdb.set_trace()
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        band = BM.Band(name="Default Band")
        return templates.TemplateResponse(
            name="band-prepare.html", request=request, context={"band": band}
        )


def band(
    band_uuid: str,
    request: Request,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        return templates.TemplateResponse(
            name="band-update.html", request=request, context={"band": band}
        )


def add_band(
    request: Request,
    band_name: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        band = BM.Band.insert(name=band_name)
        anyblok.flush()
        return templates.TemplateResponse(
            name="band-update.html", request=request, context={"band": band}
        )


def update_band(
    request: Request,
    band_uuid: str,
    band_name: Annotated[str, Form()],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        band = BM.Band.query().get(band_uuid)
        band.name = band_name
        return templates.TemplateResponse(
            name="band-update.html", request=request, context={"band": band}
        )


def search_bands(
    request: Request,
    search: Annotated[str, Form()],
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        bands = BM.Band.query().filter(BM.Band.name.ilike(f"%{search}%")).all()
        return templates.TemplateResponse(
            name="bands/search-result.html",
            request=request,
            context={"bands": bands},
        )


def musics(
    request: Request,
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry):
        pass
    return templates.TemplateResponse(name="musics.html", request=request, context={})


def profile(
    request: Request,
    # token_data: Annotated[TokenDataSchema, Security(get_current_user, scopes=["mp-admin"])],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry):
        pass
    return templates.TemplateResponse(name="profile.html", request=request, context={})
