from anyblok.blok import Blok
from band_management import __version__

VERSION = __version__


def import_declarations(reload=None):
    from . import music
    from . import musicbrainz

    if reload is not None:
        reload(music)
        reload(musicbrainz)


class MusicBrainz(Blok):
    """MusicBrainz data integration"""

    version = VERSION
    author = "Pierre Verkest"
    required = [
        "band-management-base",
    ]

    @classmethod
    def import_declaration_module(cls):
        import_declarations()

    @classmethod
    def reload_declaration_module(cls, reload):
        import_declarations(reload=reload)

    def update(self, latest):
        if not latest:
            # setup data on new version
            pass

        if latest and latest < "0.2.0":
            # do something while moving to version 0.2.0
            pass
