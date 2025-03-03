from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from anyblok.registry import Registry
from fastapi import Security
from band_management.storage import storage_factory

from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management.bloks.bm_responsive_webapp.fastapi_utils import (
    get_authenticated_musician,
    _prepare_context,
    _get_musician_from_token,
    RenewTokenRoute,
)
from .jinja import templates

from fastapi import APIRouter

scores_router = APIRouter(
    prefix="/scores",
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)
router = APIRouter(
    prefix="/score",
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)


@scores_router.get(
    "/",
)
def scores(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="scores.html",
            request=request,
            context={**_prepare_context(anyblok, request, token_data)},
        )


@scores_router.post(
    "/",
)
def search_scores(
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
        score_query = BM.Score.query_for_musician(musician)

        if search:
            score_query = score_query.filter(BM.Score.name.ilike(f"%{search}%"))

        scores = score_query.all()

        response = templates.TemplateResponse(
            name="scores/search-result.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "scores": scores,
                "search": search,
            },
        )
        return response


@router.get(
    "/prepare",
)
def prepare_score(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        score = BM.Score(name="Default Score")
        return templates.TemplateResponse(
            name="score-prepare.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "score": score,
            },
        )


@router.get(
    "/{score_uuid}",
)
def score(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    score_uuid: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        score = BM.Score.query().get(score_uuid)
        return templates.TemplateResponse(
            name="score-update.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "score": score,
            },
        )


@router.get(
    "/{score_uuid}/media",
    response_class=FileResponse,
)
async def score_media(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    score_uuid: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        score = BM.Score.query().get(score_uuid)
        _get_musician_from_token(anyblok, token_data)
        # TODO: make sure musician is allowed to read this score
        StorageClass = storage_factory()
        medium = StorageClass(
            reference=score.uuid, storage_metadata=score.storage_file_metadata
        )
        return FileResponse(medium.path, media_type=medium.storage_metadata.mime_type)


@router.post(
    "/",
)
async def add_scores(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    score_files: Annotated[
        list[UploadFile], File(description="Multipple Score file to upload")
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    for score_file in score_files:
        StorageClass = storage_factory()
        score = StorageClass()
        await score.save(score_file)
        with registry_transaction(ab_registry) as anyblok:
            musician = _get_musician_from_token(anyblok, token_data)
            BM = anyblok.BandManagement
            BM.Score.insert(
                uuid=score.reference,
                name=BM.Score.name_from_filename(
                    score.storage_metadata.original_filename
                ),
                imported_by=musician,
                storage_file_metadata=score.file_metadata,
            )

    if len(score_files) == 1:
        return RedirectResponse(
            f"/score/{score.reference}",
            status_code=201,
            headers={
                "HX-Redirect": f"/score/{score.reference}",
            },
        )
    else:
        return RedirectResponse(
            "/scores/",
            status_code=201,
            headers={
                "HX-Redirect": "/scores/",
            },
        )


@router.put(
    "/{score_uuid}",
)
def update_score(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    score_uuid: str,
    score_name: Annotated[str, Form()],
    score_music: Annotated[str | None, Form()] = None,
    source_writer_credits: Annotated[str | None, Form()] = None,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        score = BM.Score.query().get(score_uuid)
        if score:
            score.update_by(
                musician,
                name=score_name,
                source_writer_credits=source_writer_credits,
                music_uuid=score_music,
            )
            status_code = 200
        else:
            status_code = 404
        return RedirectResponse(
            "/scores",
            status_code=status_code,
            headers={
                "HX-Redirect": "/scores/",
            },
        )
