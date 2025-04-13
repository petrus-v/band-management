from anyblok import Declarations

from anyblok.relationship import Many2Many
from anyblok.column import String

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Music(Mixin.PrimaryColumn):
    title: str = String(label="Title", nullable=False)
    composer: str = String(label="Music composer(s)")
    author: str = String(label="Lyricist(s)")
    dance: str = String(label="Dance name")

    bands: list["Declarations.Model.BandManagement.Band"] = Many2Many(
        model=Declarations.Model.BandManagement.Band,
        join_table="bandmanagement_band_music_rel",
        local_columns="uuid",
        m2m_local_columns="music_uuid",
        m2m_remote_columns="band_uuid",
        remote_columns="uuid",
        many2many="musics",
    )

    @property
    def scores_count(self):
        return len(self.scores)

    def update_bands(self, musician, expected_band_uuids):
        current_bands = set()
        expected_bands = set()

        for band in musician.members.band:
            if band in self.bands:
                current_bands |= {band}
            if str(band.uuid) in expected_band_uuids:
                expected_bands |= {band}

        [self.bands.append(band) for band in expected_bands - current_bands]
        [self.bands.remove(band) for band in current_bands - expected_bands]

    def ensure_musician_active_bands(self, musician):
        [
            self.bands.append(band)
            for band in set(musician.active_bands) - set(self.bands)
        ]
