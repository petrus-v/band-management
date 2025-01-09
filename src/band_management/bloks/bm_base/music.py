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
    author: str = String(label="Lyrics author(s)")
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
