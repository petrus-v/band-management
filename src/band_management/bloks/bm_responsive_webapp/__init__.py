from anyblok.blok import Blok
from band_management import __version__
from fastapi import FastAPI
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
    def prepare_fastapi(cls, app: FastAPI) -> None:
        from . import main
        from . import band
        from . import score
        from . import music

        app.mount(
            "/static",
            StaticFiles(directory=Path(__file__).parent / "static"),
            name="static",
        )

        app.include_router(main.router)
        app.include_router(band.bands_router)
        app.include_router(band.router)
        app.include_router(music.musics_router)
        app.include_router(music.router)
        app.include_router(score.scores_router)
        app.include_router(score.router)
