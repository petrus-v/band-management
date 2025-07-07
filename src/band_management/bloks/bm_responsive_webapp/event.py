from typing import Annotated
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends, Request, Form
from fastapi.responses import RedirectResponse
from anyblok.registry import Registry
from fastapi import Security
from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
)
from band_management import _t
from band_management.tools import slugify
from band_management.bloks.bm_responsive_webapp.paging import paging_query
from band_management.bloks.bm_responsive_webapp.fastapi_utils import (
    get_authenticated_musician,
    _prepare_context,
    _get_musician_from_token,
    RenewTokenRoute,
)
from contextlib import contextmanager
from .jinja import templates, NextAction
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from io import BytesIO


events_router = APIRouter(
    prefix="/events",
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)
router = APIRouter(
    prefix="/event",
    responses={404: {"description": "Not found"}},
    route_class=RenewTokenRoute,
)


@events_router.get(
    "/",
)
def events(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        return templates.TemplateResponse(
            name="events.html",
            request=request,
            context={**_prepare_context(anyblok, request, token_data)},
        )


@contextmanager
def _search_events(ab_registry, request, search, token_data):
    with registry_transaction(ab_registry) as anyblok:
        _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        events_query = BM.Event.query().filter(
            BM.Event.name.ilike(f"%{search}%"),
        )
        events_query = events_query.order_by(
            BM.Event.date.desc(),
        )
        yield anyblok, events_query


@events_router.post(
    "/",
)
def search_events(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    search: Annotated[str, Form()],
    page: Annotated[int, Form()] = 0,
    ab_registry: "Registry" = Depends(get_registry),
):
    with _search_events(ab_registry, request, search, token_data) as (anyblok, events):
        displayed_events, next_page, last_element = paging_query(events, page)
        response = templates.TemplateResponse(
            name="events/search-result.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "events": displayed_events,
                "next_page": next_page,
                "last_element": last_element,
                "search": search,
            },
        )
        return response


@router.get(
    "/prepare",
)
def prepare_event(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    event_name: str = "",
    next_action: NextAction = NextAction.EDIT_FORM_VIEW,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        event = BM.Event(
            name=event_name or _t("New event", lang=musician.lang),
            band=musician.active_bands[0] if musician.active_bands else None,
            date=datetime.now(),
        )
        template = "event-prepare.html"
        future_action = NextAction.BACK_TO_LIST
        return templates.TemplateResponse(
            name=template,
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "event": event,
                "future_action": future_action,
            },
        )


@router.get(
    "/{event_uuid_or_uri_code}",
)
def event(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    event_uuid_or_uri_code: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        BM = anyblok.BandManagement
        event = BM.Event.query()
        if len(event_uuid_or_uri_code) > 10:
            event = event.get(event_uuid_or_uri_code)
        else:
            event = event.filter_by(uri_code=event_uuid_or_uri_code).one()
        return templates.TemplateResponse(
            name="event-update.html",
            request=request,
            context={
                **_prepare_context(anyblok, request, token_data),
                "event": event,
            },
        )


@router.get(
    "/{event_uuid_or_uri_code}/print",
)
def print_event(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    event_uuid_or_uri_code: str,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        musician = _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        event = BM.Event.query()
        if len(event_uuid_or_uri_code) > 10:
            event = event.get(event_uuid_or_uri_code)
        else:
            event = event.filter_by(uri_code=event_uuid_or_uri_code).one()
        if not event:
            raise ValueError("Event not found %s" % event_uuid_or_uri_code)
        filename = slugify(f"{event.date.strftime('%Y%m%d')}-{event.name}")
        pdf = event.print_for(musician)

    return StreamingResponse(
        BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/",
    response_class=HTMLResponse | RedirectResponse,
)
def add_music(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    name: Annotated[str, Form()],
    event_date: Annotated[datetime, Form()],
    band_uuid: Annotated[str, Form()],
    place: Annotated[str, Form()],
    comment: Annotated[str, Form()],
    header: Annotated[str, Form()],
    footer: Annotated[str, Form()],
    event_music_uuids: Annotated[list[str], Form()] = None,
    event_music_music_uuids: Annotated[list[str], Form()] = None,
    event_music_comments: Annotated[list[str], Form()] = None,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        event = BM.Event.insert(
            name=name,
            date=event_date,
            band_uuid=band_uuid,
            place=place,
            comment=comment,
            header=header,
            footer=footer,
        )
        event.update_event_musics(
            event_music_uuids or [],
            event_music_music_uuids or [],
            event_music_comments or [],
        )

    return RedirectResponse(
        "/events",
        status_code=201,
        headers={
            "HX-Redirect": "/events/",
        },
    )


@router.put(
    "/{event_uuid}",
)
def update_music(
    request: Request,
    token_data: Annotated[
        TokenDataSchema, Security(get_authenticated_musician, scopes=["musician-auth"])
    ],
    event_uuid: str,
    name: Annotated[str, Form()],
    event_date: Annotated[datetime, Form()],
    band_uuid: Annotated[str, Form()],
    place: Annotated[str, Form()],
    comment: Annotated[str, Form()],
    header: Annotated[str, Form()],
    footer: Annotated[str, Form()],
    event_music_uuids: Annotated[list[str], Form()] = None,
    event_music_music_uuids: Annotated[list[str], Form()] = None,
    event_music_comments: Annotated[list[str], Form()] = None,
    ab_registry: "Registry" = Depends(get_registry),
):
    with registry_transaction(ab_registry) as anyblok:
        _get_musician_from_token(anyblok, token_data)
        BM = anyblok.BandManagement
        event = BM.Event.query().get(event_uuid)
        event.name = name
        event.date = event_date
        event.band_uuid = band_uuid
        event.place = place
        event.comment = comment
        event.header = header
        event.footer = footer
        event.update_event_musics(
            event_music_uuids or [],
            event_music_music_uuids or [],
            event_music_comments or [],
        )

    return RedirectResponse(
        "/events",
        status_code=200,
        headers={
            "HX-Redirect": "/events/",
        },
    )
