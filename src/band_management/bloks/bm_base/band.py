from anyblok import Declarations

from anyblok.column import String

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Band(Mixin.PrimaryColumn):
    name: str = String(label="Title", nullable=False, unique=True)

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
            musician=musician,
            band=band,
            is_admin=True,
        )
        musician.active_bands.append(band)
        return band
