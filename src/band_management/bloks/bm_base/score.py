from anyblok import Declarations

from anyblok.relationship import Many2One
from anyblok.column import Text, String

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
