from anyblok import Declarations

from anyblok.column import String

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Instrument(Mixin.PrimaryColumn):
    name: str = String(label="Name", nullable=False)
