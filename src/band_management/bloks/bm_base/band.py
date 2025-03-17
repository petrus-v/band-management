from anyblok import Declarations

from anyblok.column import String
from anyblok.relationship import One2Many
from band_management.exceptions import PermissionDenied, ValidationError

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Band(Mixin.PrimaryColumn):
    name: str = String(label="Title", nullable=False, unique=True)

    inactive_members = One2Many(
        model="Model.BandManagement.Member",
        remote_columns="band_uuid",
        primaryjoin=(
            "and_(ModelBandManagementBand.uuid == ModelBandManagementMember.band_uuid,"
            "ModelBandManagementMember.invitation_state == 'rejected')"
        ),
        viewonly=True,
        lazy="subquery",
    )

    @property
    def musics_count(self):
        return len(self.musics)

    @property
    def musicians_count(self):
        return len(self.members)

    @classmethod
    def insert_by(cls, musician, **kwargs):
        band = cls.insert(**kwargs)
        cls.anyblok.BandManagement.Member.insert(
            musician=musician, band=band, is_admin=True, invitation_state="accepted"
        )
        musician.active_bands.append(band)
        return band

    def update_by(self, admin_musician, **kwargs):
        if not admin_musician.member_of(self).is_admin:
            raise PermissionDenied(
                f"You, {admin_musician.name}, are not allowed to edit this band {self.name}. Ask an existing band administrator to become a band administrator."
            )
        self.update(**kwargs)

    def update_administrator_by(self, admin_musician, administrators: list[str]):
        """Update the administrator list


        administrators is a list of Member uuid
        """

        if not admin_musician.member_of(self).is_admin:
            raise PermissionDenied(
                f"You, {admin_musician.name}, are not allowed to edit administrators's band {self.name}. Ask an existing band administrator to become a band administrator."
            )

        for member in self.members:
            member.is_admin = str(member.uuid) in administrators

        if len([member for member in self.members if member.is_admin]) == 0:
            raise ValidationError(
                f"You should set at least one administrator to this band {self.name}"
            )

    def add_member_by(self, admin_musician, invited_member, is_admin=False):
        if not admin_musician.member_of(self).is_admin:
            raise PermissionDenied(
                f"You, {admin_musician.name}, are not allowed to invite new musician to this band {self.name}. Ask an existing band administrator to become a band administrator."
            )
        return self.anyblok.BandManagement.Member.insert(
            musician=invited_member, band=self, is_admin=is_admin
        )
