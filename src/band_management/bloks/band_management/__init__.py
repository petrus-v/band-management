from anyblok.blok import Blok
from band_management import __version__

VERSION = __version__


def import_declarations(reload=None):
    from . import mixins
    from . import band_management
    from . import time_signature
    from . import tone
    from . import instrument
    from . import band
    from . import musician
    from . import musician_play_in_band
    from . import music
    from . import score
    
    if reload is not None:
        reload(mixins)
        reload(band_management)
        reload(time_signature)
        reload(tone)
        reload(instrument)
        reload(band)
        reload(musician)
        reload(musician_play_in_band)
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
            self.anyblok.BandManagement.TimeSignature.insert(name="2/2")
            self.anyblok.BandManagement.TimeSignature.insert(name="4/4")
            self.anyblok.BandManagement.TimeSignature.insert(name="3/4")
            self.anyblok.BandManagement.TimeSignature.insert(name="6/8")
            self.anyblok.BandManagement.TimeSignature.insert(name="Mixed 6/8 & 2/4")
            
            # Major
            self.anyblok.BandManagement.Tone.insert(name="C")
            self.anyblok.BandManagement.Tone.insert(name="C#")
            self.anyblok.BandManagement.Tone.insert(name="D")
            self.anyblok.BandManagement.Tone.insert(name="E♭")
            self.anyblok.BandManagement.Tone.insert(name="E")
            self.anyblok.BandManagement.Tone.insert(name="F")
            self.anyblok.BandManagement.Tone.insert(name="F#")
            self.anyblok.BandManagement.Tone.insert(name="G")
            self.anyblok.BandManagement.Tone.insert(name="G#")
            self.anyblok.BandManagement.Tone.insert(name="A")
            self.anyblok.BandManagement.Tone.insert(name="B♭")
            self.anyblok.BandManagement.Tone.insert(name="B")

            # Minor
            self.anyblok.BandManagement.Tone.insert(name="Cm")
            self.anyblok.BandManagement.Tone.insert(name="C#m")
            self.anyblok.BandManagement.Tone.insert(name="Dm")
            self.anyblok.BandManagement.Tone.insert(name="E♭m")
            self.anyblok.BandManagement.Tone.insert(name="Em")
            self.anyblok.BandManagement.Tone.insert(name="Fm")
            self.anyblok.BandManagement.Tone.insert(name="F#m")
            self.anyblok.BandManagement.Tone.insert(name="Gm")
            self.anyblok.BandManagement.Tone.insert(name="G#m")
            self.anyblok.BandManagement.Tone.insert(name="Am")
            self.anyblok.BandManagement.Tone.insert(name="B♭m")
            self.anyblok.BandManagement.Tone.insert(name="Bm")

            # Mixed
            self.anyblok.BandManagement.Tone.insert(name="G / C")
            self.anyblok.BandManagement.Tone.insert(name="A / D")

        if latest and latest < "0.2.0":
            # do something while moving to version 0.2.0
            pass
