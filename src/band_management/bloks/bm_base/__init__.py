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
            BM = self.anyblok.BandManagement
            pamh_band = BM.Band.insert(name="PAMH")
            trib_band = BM.Band.insert(name="Tribardeurs")
            tradamuse_band = BM.Band.insert(name="Trad'amuse")

            musician_pv = BM.Musician.insert(
                name="Pierre Verkest",
                email="pierre@verkest.fr",
                lang="fr",
                create_solo_band=False,
            )
            musician_joe = BM.Musician.insert(
                name="Joe",
                email="joe@test.fr",
                lang="en",
                create_solo_band=False,
            )
            musician_doe = BM.Musician.insert(
                create_solo_band=False, name="Doe", email="doe@test.fr"
            )

            voice = BM.Instrument.insert(name="Voice")
            BM.Instrument.insert(name="Voice Tenor")
            BM.Instrument.insert(name="Voice Soprano")
            BM.Instrument.insert(name="Voice Alto")
            gc_accordion = BM.Instrument.insert(name="Accordion G/C")
            BM.Instrument.insert(name="Accordion L/D")
            chromatic_accordion = BM.Instrument.insert(
                name="Chromatic button accordion"
            )
            BM.Instrument.insert(name="Chromatic piano accordion")
            BM.Instrument.insert(name="Bayan")

            violin = BM.Instrument.insert(name="Violon")
            classical_guitare = BM.Instrument.insert(name="Classical Guitar")
            BM.Instrument.insert(name="Acoustic Guitar")
            BM.Instrument.insert(name="Ukulele")
            banjos = BM.Instrument.insert(name="Banjos")

            pierre_in_pahm = BM.Member.insert(
                is_admin=True,
                musician=musician_pv,
                band=pamh_band,
                invitation_state="accepted",
            )
            musician_pv.active_bands.append(pamh_band)
            pierre_in_pahm.instruments.append(gc_accordion)
            joe_in_pahm = BM.Member.insert(
                musician=musician_joe, band=pamh_band, invitation_state="accepted"
            )
            joe_in_pahm.instruments.append(violin)

            pierre_in_trib = BM.Member.insert(
                is_admin=True,
                musician=musician_pv,
                band=trib_band,
            )
            musician_pv.active_bands.append(trib_band)
            pierre_in_trib.instruments.append(gc_accordion)
            pierre_in_trib.instruments.append(voice)
            joe_in_trib = BM.Member.insert(musician=musician_joe, band=trib_band)
            joe_in_trib.instruments.append(violin)

            doe_in_trib = BM.Member.insert(musician=musician_doe, band=trib_band)
            doe_in_trib.instruments.append(banjos)
            doe_in_trib.instruments.append(classical_guitare)
            doe_in_trib.instruments.append(chromatic_accordion)

            BM.Member.insert(is_admin=True, musician=musician_doe, band=tradamuse_band)

            # Score not link yet to music
            BM.Score.insert(
                name="Polka pomme",
                imported_by=musician_joe,
            )
            BM.Score.insert(
                name="Au coin du feux",
                imported_by=musician_doe,
            )

            # Score link to music but no band

            music_jet_lama = BM.Music.insert(
                title="Le Jet du Lama",
                dance="Chapelloise",
                composer="Philippe Plard",
            )
            BM.Score.insert(
                name="Voice 1 - G/C accordéon",
                imported_by=musician_joe,
                music=music_jet_lama,
            )

            music_elle = BM.Music.insert(
                title="Elle",
                dance="Valse 5 temps",
                composer="Rémi Geffroy",
            )
            BM.Score.insert(
                name="voice 1 - G/C accordéon",
                imported_by=musician_doe,
                music=music_elle,
            )

            # Scores linked to musics/bands
            music_envole = BM.Music.insert(
                title="L'envole",
                dance="Valse",
                composer="Pierre Verkest",
            )
            BM.Score.insert(
                name="Voice 1",
                source_writer_credits="Marie-Hélène",
                imported_by=musician_joe,
                music=music_envole,
            )

            music_zelda = BM.Music.insert(
                title="Zelda",
                dance="Mixer",
                composer="Philippe Plard",
            )
            BM.Score.insert(
                name="Voice 1 - Zelda",
                source_writer_credits="Manqu'pas d'airs",
                imported_by=musician_joe,
                music=music_zelda,
            )
            BM.Score.insert(
                name="Voice 2 - Zelda",
                source_writer_credits="Manqu'pas d'airs",
                imported_by=musician_pv,
                music=music_zelda,
            )
            music_esperanza = BM.Music.insert(
                title="Esperanza",
                dance="Scottish",
                composer="Marc Perrone",
            )
            BM.Score.insert(
                name="Voice 1",
                source_writer_credits="Manqu'pas d'airs",
                imported_by=musician_pv,
                music=music_esperanza,
            )
            pamh_band.musics.append(music_zelda)
            pamh_band.musics.append(music_envole)
            tradamuse_band.musics.append(music_zelda)
            trib_band.musics.append(music_esperanza)
            trib_band.musics.append(music_zelda)

        if latest_version and latest_version < "0.2.0":
            # do something while moving to version 0.2.0
            pass
