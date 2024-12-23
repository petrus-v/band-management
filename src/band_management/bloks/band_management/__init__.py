from anyblok.blok import Blok
from band_management import __version__

VERSION = __version__


def import_declarations(reload=None):
    from . import mixins
    from . import band_management
    from . import instrument
    from . import band
    from . import musician
    from . import member
    from . import music
    from . import score
    
    if reload is not None:
        reload(mixins)
        reload(band_management)
        reload(instrument)
        reload(band)
        reload(musician)
        reload(member)
        reload(score)
        reload(music)


class BandManagement(Blok):
    version = VERSION
    author = "Pierre Verkest"
    required = [
        "anyblok-core",
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
