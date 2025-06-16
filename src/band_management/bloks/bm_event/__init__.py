from datetime import datetime
from pathlib import Path
from anyblok.blok import Blok
from band_management import __version__

VERSION = __version__


def import_declarations(reload=None):
    from . import event
    from . import event_music

    if reload is not None:
        reload(event)
        reload(event_music)


class BandManagementEvent(Blok):
    version = VERSION
    author = "Pierre Verkest"
    required = [
        "band-management-base",
        "band-management-report",
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
            self.anyblok.Report.JinjaTemplate.insert(
                code="event",
                directories=str((Path(__file__).parent / "documents").absolute()),
                template="event.html",
            )

        if latest and latest < "0.2.0":
            # do something while moving to version 0.2.0
            pass

    def update_demo(self, latest_version):
        """Called on install or update to set or update demo data"""

        if not latest_version:
            BM = self.anyblok.BandManagement
            pamh_band = BM.Band.query().filter_by(name="PAMH").one()
            music_zelda = BM.Music.query().filter_by(title="Zelda").one()
            music_envole = BM.Music.query().filter_by(title="L'envole").one()

            # Create event
            event = BM.Event.insert(
                name="A great event",
                band=pamh_band,
                place="Somewhere",
                date=datetime(2025, 5, 15),
                header="Event organized by Amnézic",
                footer="Pahm artists: Pierre, Angèle, ...",
                comment="This will be a great moment with our friends.",
            )
            BM.EventMusic.insert(
                event=event,
                music=music_zelda,
                sequence=10,
                comment="Introduced by MH. 2xAB - 1xCD",
            )
            BM.EventMusic.insert(
                event=event,
                music=music_envole,
                sequence=20,
                comment="Introduced by Angèle & M.",
            )

        if latest_version and latest_version < "0.2.0":
            # do something while moving to version 0.2.0
            pass
