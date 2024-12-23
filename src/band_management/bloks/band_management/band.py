from anyblok import Declarations

from anyblok.column import String

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Band(Mixin.PrimaryColumn):
    name: str = String(label="Title", nullable=False)
