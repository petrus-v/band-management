from anyblok import Declarations

from anyblok.relationship import Many2Many, Many2One

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Member(Mixin.PrimaryColumn):
    musician: "Model.BandManagement.Musician" = Many2One(
        model="Model.BandManagement.Musician",
        nullable=False,
        one2many="members",
    )
    band: "Model.BandManagement.Band" = Many2One(
        model="Model.BandManagement.Band",
        nullable=False,
        one2many="members",
    )
    instruments: list["Declarations.Model.BandManagement.Instrument"] = Many2Many(
        model=Declarations.Model.BandManagement.Instrument,
        join_table="bandmanagement_member_instrument_rel",
        local_columns="uuid",
        m2m_local_columns="member_uuid",
        m2m_remote_columns="instrument_uuid",
        remote_columns="uuid",
        many2many="members",
    )
