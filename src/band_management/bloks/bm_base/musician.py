from anyblok import Declarations

from anyblok.column import String, Email
from anyblok.relationship import Many2Many, Many2One

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Musician(Mixin.PrimaryColumn):
    name: str = String(label="Name", nullable=False)
    email: str = Email(label="Email", nullable=False, unique=True)
    lang: str = String(label="Language", nullable=False, default="en")

    active_bands: list["Declarations.Model.BandManagement.Band"] = Many2Many(
        model=Declarations.Model.BandManagement.Band,
        join_table="bandmanagement_avtive_band_musician_rel",
        local_columns="uuid",
        m2m_local_columns="musician_uuid",
        m2m_remote_columns="band_uuid",
        remote_columns="uuid",
    )