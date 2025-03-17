from anyblok import Declarations

from anyblok.column import Email, String
from anyblok.relationship import Many2Many, One2Many
from band_management.exceptions import PermissionDenied, ValidationError

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Musician(Mixin.PrimaryColumn):
    name: str = String(label="Name", nullable=False, unique=True)
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
    rejected_invitations = One2Many(
        model="Model.BandManagement.Member",
        remote_columns="musician_uuid",
        primaryjoin=(
            "and_(ModelBandManagementMusician.uuid == ModelBandManagementMember.musician_uuid,"
            "ModelBandManagementMember.invitation_state == 'rejected')"
        ),
        viewonly=True,
        # lazy="subquery",
    )

    @property
    def my_bands(self):
        return self.members.band

    def toggle_musician_active_band(self, band_uuid):
        band = self.anyblok.BandManagement.Band.query().get(band_uuid)

        if band not in self.my_bands:
            raise PermissionDenied(
                "Permission denied. You must be part of the band to be able to active it."
            )

        if band not in self.active_bands:
            if self.member_of(band).invitation_state == "rejected":
                raise ValidationError(
                    f"You ({self.name}) should accept the invitation before activate this band: {band.name}."
                )

            self.active_bands.append(band)
        else:
            self.active_bands.remove(band)

        if len(self.active_bands) == 0:
            raise ValidationError(
                f"Musician {self.name} require at least one active band."
            )

    def member_of(self, band):
        for member in self.members:
            if member.band == band:
                return member

    def create_solo(self):
        BM = self.anyblok.BandManagement
        return BM.Band.insert_by(self, name=f"{self.name} Solo")

    @classmethod
    def insert(cls, *args, create_solo_band: bool = True, **kwargs):
        musician = super().insert(*args, **kwargs)
        if create_solo_band:
            musician.create_solo()
        return musician
