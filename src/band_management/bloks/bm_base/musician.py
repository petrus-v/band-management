from anyblok import Declarations

from anyblok.column import Email, String
from anyblok.relationship import Many2Many, One2Many
from band_management import _t
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
    )

    @property
    def my_bands(self):
        return self.members.band

    def toggle_musician_active_band(self, band_uuid):
        band = self.anyblok.BandManagement.Band.query().get(band_uuid)

        if band not in self.my_bands:
            raise PermissionDenied(
                _t(
                    "Permission denied. You must be part of the band to be able to active it.",
                    lang=self.lang,
                )
            )

        if band not in self.active_bands:
            if self.member_of(band).invitation_state == "rejected":
                raise ValidationError(
                    _t(
                        "You, %s, should accept the invitation before activate "
                        "this band: %s.",
                        lang=self.lang,
                    )
                    % (
                        self.name,
                        band.name,
                    )
                )
            self.active_bands.append(band)
        else:
            self.active_bands.remove(band)

        if len(self.active_bands) == 0:
            raise ValidationError(
                _t("You, %s, require at least one active band.", lang=self.lang)
                % self.name
            )

    def member_of(self, band):
        for member in self.members:
            if member.band == band:
                return member

    def create_solo(self):
        BM = self.anyblok.BandManagement
        return BM.Band.insert_by(
            self, name=_t("%s Solo", lang=self.lang) % (self.name,)
        )

    @classmethod
    def insert(cls, *args, create_solo_band: bool = True, **kwargs):
        musician = super().insert(*args, **kwargs)
        if create_solo_band:
            musician.create_solo()
        return musician
