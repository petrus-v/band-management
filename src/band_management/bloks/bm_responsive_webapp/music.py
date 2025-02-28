from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form
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
from contextlib import contextmanager
from .jinja import templates
import sqlalchemy as sa


def musics(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="musics.html",
            request=request,
            context={**_prepare_context(anyblok, request, token_data)},
        )


def prepare_music(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        music = BM.Music(title="Default Music")
        [music.bands.append(b) for b in musician.active_bands]
        return templates.TemplateResponse(
            name="music-prepare.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "music": music,
            },
        )


def music(
    music_uuid: str,
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        music = BM.Music.query().get(music_uuid)
        return templates.TemplateResponse(
            name="music-update.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "music": music,
            },
        )


def add_music(
    request: Request,
    music_title: Annotated[str, Form()],
    music_composer: Annotated[str, Form()],
    music_author: Annotated[str, Form()],
    music_dance: Annotated[str, Form()],
    music_bands: Annotated[list[str] | None, Form()],
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        music = BM.Music.insert(
            title=music_title,
            composer=music_composer,
            author=music_author,
            dance=music_dance,
        )
        music.update_bands(musician, music_bands)
    return RedirectResponse(
        "/musics",
        status_code=201,
        headers={
            "HX-Redirect": "/musics",
        },
    )


def update_music(
    request: Request,
    music_uuid: str,
    music_title: Annotated[str, Form()],
    music_composer: Annotated[str, Form()],
    music_author: Annotated[str, Form()],
    music_dance: Annotated[str, Form()],
    music_bands: Annotated[list[str] | None, Form()],
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        music = BM.Music.query().get(music_uuid)
        music.title = music_title
        music.composer = music_composer
        music.author = music_author
        music.dance = music_dance
        music.update_bands(musician, music_bands)

    return RedirectResponse(
        "/musics",
        status_code=200,
        headers={
            "HX-Redirect": "/musics",
        },
    )


@contextmanager
def _search_musics(ab_registry, request, search, token_data):
    with registry_transaction(ab_registry) as anyblok:
        _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        musics_query = BM.Music.query()
        # .join(BM.Music.bands)
        musics_query = musics_query.filter(
            sa.or_(
                BM.Music.title.ilike(f"%{search}%"),
                BM.Music.composer.ilike(f"%{search}%"),
                BM.Music.author.ilike(f"%{search}%"),
            )
        )
        # musics_query = musics_query.filter(BM.Band.uuid.in_(musician.active_bands.uuid))

        musics_query = musics_query.order_by(
            BM.Music.title,
            BM.Music.composer,
            BM.Music.author,
        )
        yield anyblok, musics_query


def search_musics(
    request: Request,
    search: Annotated[str, Form()],
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with _search_musics(ab_registry, request, search, token_data) as (anyblok, musics):
        response = templates.TemplateResponse(
            name="musics/search-result.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "musics": musics.all(),
                "search": search,
            },
        )
        return response


def search_dropdown_musics(
    request: Request,
    search: Annotated[str, Form()],
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with _search_musics(ab_registry, request, search, token_data) as (anyblok, musics):
        response = templates.TemplateResponse(
            name="musics/search-dropdown-result.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "musics": musics.limit(7).all(),
                "search": search,
            },
        )
        return response
