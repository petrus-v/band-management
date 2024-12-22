from anyblok import Declarations

from anyblok.relationship import Many2Many, Many2One
from anyblok.column import Integer, Selection, Text, Decimal, DateTime, String, Json

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Instrument(Mixin.PrimaryColumn):

    name: str = String(label="Name", nullable=False)
    tone: "Model.BandManagement.Tone" = Many2One(
        model="Model.BandManagement.Tone",
        label="Instrument Tone, ie: a Trumpet is commonly in B♭ tone.",
    )