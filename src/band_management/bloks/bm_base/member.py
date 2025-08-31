from anyblok import Declarations

from anyblok.relationship import Many2Many, Many2One
from anyblok.column import Boolean, Selection
from anyblok.schema import (
    UniqueConstraint,
)
from band_management import _t
from band_management.exceptions import PermissionDenied

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Member(Mixin.PrimaryColumn):
    INVITATION_STATE = [
        ("invited", "Invited"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    musician: "Model.BandManagement.Musician" = Many2One(
        model="Model.BandManagement.Musician",
        nullable=False,
        one2many=(
            "members",
            dict(
                primaryjoin=(
                    "and_(ModelBandManagementMusician.uuid == ModelBandManagementMember.musician_uuid,"
                    "ModelBandManagementMember.invitation_state != 'rejected')"
                ),
                lazy="subquery",
            ),
        ),
    )
    band: "Model.BandManagement.Band" = Many2One(
        model="Model.BandManagement.Band",
        nullable=False,
        one2many=(
            "members",
            dict(
                primaryjoin=(
                    "and_(ModelBandManagementBand.uuid == ModelBandManagementMember.band_uuid,"
                    "ModelBandManagementMember.invitation_state != 'rejected')"
                ),
                lazy="subquery",
            ),
        ),
    )
    is_admin = Boolean(label="Band admin", default=False)

    instruments: list["Declarations.Model.BandManagement.Instrument"] = Many2Many(
        model=Declarations.Model.BandManagement.Instrument,
        join_table="bandmanagement_member_instrument_rel",
        local_columns="uuid",
        m2m_local_columns="member_uuid",
        m2m_remote_columns="instrument_uuid",
        remote_columns="uuid",
        many2many="members",
    )
    invitation_state = Selection(
        selections=INVITATION_STATE,
        default="invited",
        index=True,
    )
    invited_by: "Model.BandManagement.Musician" = Many2One(
        model="Model.BandManagement.Musician",
        nullable=True,
    )

    @classmethod
    def define_table_args(cls):
        table_args = super().define_table_args()
        return table_args + (
            UniqueConstraint(
                cls.musician_uuid, cls.band_uuid, name="unique_musician_per_band"
            ),
        )

    # @classmethod
    # def query(cls, *args, filter_rejected=True, **kwargs):
    #     query = super().query(*args, **kwargs)
    #     if filter_rejected:
    #         query = query.filter(cls.invitation_state != "rejected")
    #     return query

    @classmethod
    def create_invitation_by(cls, band, invited_musician, invited_by=None):
        if invited_by:
            member = invited_by.member_of(band)
            if not (member.is_admin and member.invitation_state == "accepted"):
                raise PermissionDenied(
                    _t(
                        "You must have an accepted invitation with admin access "
                        "to this band %(band_name)s before invite new musicians.",
                        lang=invited_by.lang,
                    )
                    % {"band_name": band.name}
                )

        member = cls.insert(band=band, musician=invited_musician, invited_by=invited_by)
        return member

    def accept_invitation(self):
        self.invitation_state = "accepted"

    def reject_invitation(self):
        self.invitation_state = "rejected"
        self.anyblok.flush()
        self.musician.refresh()
        if self.musician.active_band == self.band:
            if len(self.musician.my_bands) == 0:
                raise ValueError(
                    _t(
                        "You must be part of at least one band, create an other one if you want to leave the current one"
                    )
                )
            self.musician.set_active_band(str(self.musician.my_bands[0].uuid))
