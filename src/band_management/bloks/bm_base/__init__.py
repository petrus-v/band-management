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


class BandManagementBase(Blok):
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

    def update_demo(self, latest_version):
        """Called on install or update to set or update demo data"""

        if not latest_version:
            bm = self.anyblok.BandManagement
            bm.Band.insert(name="PAMH")
            bm.Band.insert(name="Tribarteurs")
            bm.Band.insert(name="Manque pas d'air")
            bm.Band.insert(name="Trad'amuse")

        if latest_version and latest_version < "0.2.0":
            # do something while moving to version 0.2.0
            pass
