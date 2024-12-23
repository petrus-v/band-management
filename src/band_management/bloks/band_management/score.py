from anyblok import Declarations

from anyblok.relationship import Many2Many, Many2One
from anyblok.column import Integer, Selection, Text, Decimal, DateTime, String, Json

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Score(Mixin.PrimaryColumn):

    name: str = String(label="Name", nullable=False)
    score_source_writer: str = Text(label="Score/lyrics source & score writer")
    music: "Model.BandManagement.Music" = Many2One(
        model="Model.BandManagement.Music",
        nullable=False,
    )