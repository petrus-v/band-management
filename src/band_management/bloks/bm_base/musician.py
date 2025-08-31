from anyblok import Declarations

from anyblok.column import Email, String
from anyblok.relationship import Many2One, One2Many
from band_management import _t
from band_management.exceptions import PermissionDenied
from uuid_extensions import uuid7

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Musician(Mixin.PrimaryColumn):
    name: str = String(label="Name", nullable=False, unique=True)
    email: str = Email(label="Email", nullable=False, unique=True)
    lang: str = String(label="Language", nullable=False, default="en")

    active_band: "Declarations.Model.BandManagement.Band" = Many2One(
        model=Declarations.Model.BandManagement.Band,
        nullable=False,
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

    def set_active_band(self, band_uuid):
        band = self.anyblok.BandManagement.Band.query().get(band_uuid)
        return self._set_active_band(band)

    def _set_active_band(self, band: "Declarations.Model.BandManagement.Band"):
        if band not in self.my_bands:
            raise PermissionDenied(
                _t(
                    "Permission denied. You must be part of the band to be able to active it.",
                    lang=self.lang,
                )
            )

        if band != self.active_band:
            self.active_band = band

    def member_of(self, band):
        for member in self.members:
            if member.band == band:
                return member

    @classmethod
    def insert(cls, active_band=None, **kwargs):
        # overwritte anyblok insert to manage flush once active_band is
        # set to avoid integrity error on non null active_band_uuid field
        musician_uuid = kwargs.get("uuid")
        if not musician_uuid:
            musician_uuid = str(uuid7())
            kwargs["uuid"] = musician_uuid

        BM = cls.anyblok.BandManagement
        if not active_band:
            active_band = BM.Band.insert(
                name=_t("%s Solo", lang=kwargs.get("lang", "en"))
                % (kwargs.get("name", "My band"),)
            )
            musician_band_member = BM.Member(
                musician_uuid=musician_uuid,
                band=active_band,
                is_admin=True,
                invitation_state="accepted",
            )
        else:
            musician_band_member = BM.Member(
                musician_uuid=musician_uuid,
                band=active_band,
                is_admin=False,
                invitation_state="invited",
            )

        cls.anyblok.add(musician_band_member)
        return super().insert(active_band=active_band, **kwargs)
