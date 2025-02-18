from anyblok.blok import Blok
from band_management import __version__
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.routing import APIRoute, Mount
from fastapi.staticfiles import StaticFiles
from pathlib import Path

VERSION = __version__


def import_declarations(reload=None):
    # from . import mixins

    if reload is not None:
        # reload(mixins)
        pass


class BandManagementResponsiveWebApp(Blok):
    version = VERSION
    author = "Pierre Verkest"
    required = [
        "band-management-base",
        "http-auth-base",
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
    def fastapi_routes(cls, routes: dict) -> None:
        from . import main

        routes.update(
            {
                "PUT/musician/{musician_uuid}/toggle-active-band/{band_uuid}": APIRoute(
                    "/musician/{musician_uuid}/toggle-active-band/{band_uuid}",
                    main.toggle_musician_active_band,
                    methods=["PUT"],
                    response_class=HTMLResponse,
                ),
                "GET/": APIRoute(
                    "/",
                    main.index,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "GET/login": APIRoute(
                    "/login",
                    main.login,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "POST/login": APIRoute(
                    "/login",
                    main.login_post,
                    methods=["POST"],
                    response_class=RedirectResponse,
                ),
                "POST/logout": APIRoute(
                    "/logout",
                    main.logout_post,
                    methods=["POST"],
                    response_class=RedirectResponse,
                ),
                "GET/register": APIRoute(
                    "/register",
                    main.register,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "GET/home": APIRoute(
                    "/home",
                    main.home,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "GET/bands": APIRoute(
                    "/bands",
                    main.bands,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "POST/bands": APIRoute(
                    "/bands",
                    main.search_bands,
                    methods=["POST"],
                    response_class=HTMLResponse,
                ),
                "MOUNT/band/": Mount(
                    "/band",
                    routes=[
                        APIRoute(
                            "/",
                            main.add_band,
                            methods=["POST"],
                            response_class=HTMLResponse,
                        ),
                        APIRoute(
                            "/prepare",
                            main.prepare_band,
                            methods=["GET"],
                            response_class=HTMLResponse,
                        ),
                        APIRoute(
                            "/{band_uuid}",
                            main.band,
                            methods=["GET"],
                            response_class=HTMLResponse,
                        ),
                        APIRoute(
                            "/{band_uuid}",
                            main.update_band,
                            methods=["PUT"],
                            response_class=HTMLResponse,
                        ),
                    ],
                ),
                "GET/musics": APIRoute(
                    "/musics",
                    main.musics,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "GET/scores": APIRoute(
                    "/scores",
                    main.scores,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "POST/scores": APIRoute(
                    "/scores",
                    main.search_scores,
                    methods=["POST"],
                    response_class=HTMLResponse,
                ),
                "MOUNT/score/": Mount(
                    "/score",
                    routes=[
                        APIRoute(
                            "/",
                            main.add_scores,
                            methods=["POST"],
                            response_class=HTMLResponse,
                        ),
                        APIRoute(
                            "/prepare",
                            main.prepare_score,
                            methods=["GET"],
                            response_class=HTMLResponse,
                        ),
                        APIRoute(
                            "/{score_uuid}",
                            main.score,
                            methods=["GET"],
                            response_class=HTMLResponse,
                        ),
                        APIRoute(
                            "/{score_uuid}/media",
                            main.score_media,
                            methods=["GET"],
                            response_class=FileResponse,
                        ),
                        APIRoute(
                            "/{score_uuid}",
                            main.update_score,
                            methods=["PUT"],
                            response_class=HTMLResponse,
                        ),
                    ],
                ),
                "GET/profile": APIRoute(
                    "/profile",
                    main.profile,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "GET/credits": APIRoute(
                    "/credits",
                    main.credits,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "GET/terms": APIRoute(
                    "/terms",
                    main.terms,
                    methods=["GET"],
                    response_class=HTMLResponse,
                ),
                "GET/static": Mount(
                    "/static",
                    app=StaticFiles(directory=Path(__file__).parent / "static"),
                    name="static",
                ),
            }
        )
