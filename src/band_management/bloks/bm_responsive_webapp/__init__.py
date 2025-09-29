from anyblok.blok import Blok
from band_management import __version__
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from band_management.exceptions import PermissionDenied
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from .jinja import templates
from fastapi.responses import JSONResponse

from band_management.bloks.bm_responsive_webapp.fastapi_utils import (
    _prepare_context,
)

from fastapi import status, HTTPException
from band_management import _t


VERSION = __version__


def import_declarations(reload=None):
    from . import auth
    from . import band_management

    if reload is not None:
        reload(auth)
        reload(band_management)

    auth.import_declarations(reload=reload)
    band_management.import_declarations(reload=reload)


class BandManagementResponsiveWebApp(Blok):
    version = VERSION
    author = "Pierre Verkest"
    required = [
        "band-management-base",
        "band-management-event",
        "http-auth-base",
        "music-brainz",
    ]

    @classmethod
    def import_declaration_module(cls):
        import_declarations()

    @classmethod
    def reload_declaration_module(cls, reload):
        import_declarations(reload=reload)

    def update(self, latest):
        if not latest:
            # setup fresh database
            pass

        if latest and latest < "0.2.0":
            # do something while moving to version 0.2.0
            pass

    @classmethod
    def prepare_fastapi(cls, app: FastAPI) -> None:
        cls._register_fastapi_route(app)
        cls._register_fastapi_exceptions(app)

    @classmethod
    def _register_fastapi_route(cls, app: FastAPI) -> None:
        from . import band
        from . import main
        from . import member
        from . import music
        from . import musician
        from . import score
        from . import event

        app.mount(
            "/static",
            StaticFiles(directory=Path(__file__).parent / "static"),
            name="static",
        )

        app.include_router(band.bands_router)
        app.include_router(band.router)
        app.include_router(main.router)
        app.include_router(member.router)
        app.include_router(music.musics_router)
        app.include_router(music.router)
        app.include_router(musician.musicians_router)
        app.include_router(musician.router)
        app.include_router(score.scores_router)
        app.include_router(score.router)
        app.include_router(event.events_router)
        app.include_router(event.router)

    @classmethod
    def _register_fastapi_exceptions(cls, app: FastAPI) -> None:
        @app.exception_handler(404)
        async def not_found_exception_handler(
            request: Request,
            exc: HTTPException,
        ):
            if request.headers.get("HX-Request"):
                # htmx ajax request
                return JSONResponse(
                    status_code=exc.status_code, content={"message": str(exc)}
                )
            else:
                return templates.TemplateResponse(
                    name="error.html",
                    status_code=404,
                    request=request,
                    context={
                        **_prepare_context(None, request, None),
                        "error_message": _t("Page not found %(current_url)s")
                        % {
                            "current_url": request.headers.get(
                                "HX-Current-URL", request.url.path
                            ),
                        },
                    },
                )

        @app.exception_handler(Exception)
        async def errors_handler(
            request: Request,
            exc: Exception,
        ):
            if request.headers.get("HX-Request"):
                # htmx ajax request
                return JSONResponse(status_code=500, content={"message": str(exc)})
            return templates.TemplateResponse(
                name="error.html",
                status_code=200,
                request=request,
                context={
                    **_prepare_context(None, request, None),
                    "error_message": str(exc),
                },
            )

        @app.exception_handler(PermissionDenied)
        async def permission_denied_handler(
            request: Request,
            exc: PermissionDenied,
        ):
            if exc.redirect == "/login":
                exc.redirect = f"{exc.redirect}?next_path={request.url.path}"
            if request.headers.get("HX-Request"):
                # htmx ajax request
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"message": str(exc)},
                )
                if exc.redirect:
                    response.status_code = status.HTTP_307_TEMPORARY_REDIRECT
                    response.headers.update(
                        {
                            "HX-Redirect": exc.redirect,
                        }
                    )
            else:
                if exc.redirect:
                    response = RedirectResponse(
                        exc.redirect,
                        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                        headers={
                            "HX-Redirect": exc.redirect,
                        },
                    )
                else:
                    response = templates.TemplateResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        name="error.html",
                        request=request,
                        context={
                            **_prepare_context(None, request, None),
                            "error_message": str(exc),
                        },
                    )
            response.headers.update(exc.headers)

            return response
