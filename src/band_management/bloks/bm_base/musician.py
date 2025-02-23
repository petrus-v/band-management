from anyblok import Declarations

from anyblok.column import String, Email
from anyblok.relationship import Many2Many
from band_management.exceptions import PermissionDenied, ValidationError


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
            self.active_bands.append(band)
        else:
            self.active_bands.remove(band)

        if len(self.active_bands) == 0:
            raise ValidationError(
                f"Musician {self.name} require at least one active band."
            )
