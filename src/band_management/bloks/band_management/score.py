from anyblok import Declarations

from anyblok.relationship import Many2Many, Many2One
from anyblok.column import Integer, Selection, Text, Decimal, DateTime, String, Json

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Score(Mixin.PrimaryColumn):

    name: str = String(label="Name", nullable=False)
    tempo: int = Integer(label="Tempo/beat")
    score_source_writer: str = Text(label="Score/lyrics source & score writer")
    music: "Model.BandManagement.Music" = Many2One(
        model="Model.BandManagement.Music",
        nullable=False,
    )
    time_signature: "Model.BandManagement.TimeSignature" = Many2One(
        model="Model.BandManagement.TimeSignature",
    )
    tone: "Model.BandManagement.Tone" = Many2One(
        model="Model.BandManagement.Tone",
    )
    instruments: list["Model.BandManagement.Instrument"] = Many2Many(
        model=Model.BandManagement.Instrument,
        join_table="bandmanagement_score_instrument_rel",
        local_columns="uuid",
        m2m_local_columns="score_uuid",
        m2m_remote_columns="instrument_uuid",
        remote_columns="uuid",
        many2many="scores",
    )
