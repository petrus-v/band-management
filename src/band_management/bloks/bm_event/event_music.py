from anyblok import Declarations
from anyblok.relationship import Many2One
from anyblok.column import Text, Integer

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class EventMusic(Mixin.PrimaryColumn):
    event: "Model.BandManagement.Event" = Many2One(
        model="Model.BandManagement.Event",
        foreign_key_options={"ondelete": "cascade"},
        nullable=False,
        one2many="musics",
    )
    music: "Model.BandManagement.Music" = Many2One(
        model="Model.BandManagement.Music",
        nullable=False,
        # one2many="events",
    )
    sequence: int = Integer(
        label="Postion of the music in the event",
    )
    comment: str = Text(label="Event music comment")
