from anyblok import Declarations

from anyblok.relationship import Many2Many, Many2One
from anyblok.column import Integer, Selection, Text, Decimal, DateTime, String, Json

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model





@register(Model.BandManagement)
class MusicianPlayInBand(Mixin.PrimaryColumn):

    musician: "Model.BandManagement.Musician" = Many2One(
        model="Model.BandManagement.Musician",
        nullable=False,
        one2many="play",
    )
    band: "Model.BandManagement.Band" = Many2One(
        model="Model.BandManagement.Band",
        nullable=False,
        one2many="players",
    )
    instruments: list["Declarations.Model.BandManagement.Instrument"] = Many2Many(
        model=Declarations.Model.BandManagement.Instrument,
        join_table="bandmanagement_musician_play_in_band_instrument_rel",
        local_columns="uuid",
        m2m_local_columns="musician_play_in_band_uuid",
        m2m_remote_columns="instrument_uuid",
        remote_columns="uuid",
        many2many="musicians_in_band",
    )
