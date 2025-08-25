from pathlib import PurePath
from anyblok import Declarations
from band_management import _t
from band_management.exceptions import ValidationError, PermissionDenied
from band_management.storage import storage_factory
from anyblok.relationship import Many2One
from anyblok.column import Text, Json
import sqlalchemy as sa


register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Score(Mixin.PrimaryColumn):
    name: str = Text(label="Name", nullable=False)
    source_writer_credits: str = Text(label="Score/lyrics source & score writer")

    storage_file_metadata: str = Json(
        label="Storage File metadata",
        nullable=True,
    )
    music: "Model.BandManagement.Music" = Many2One(
        model="Model.BandManagement.Music",
        nullable=True,
        one2many="scores",
    )
    imported_by: "Model.BandManagement.Musician" = Many2One(
        model="Model.BandManagement.Musician",
        nullable=False,
        one2many="my_scores",
    )

    @property
    def is_deletable(self):
        if self.music:
            return False
        return True

    @classmethod
    def name_from_filename(cls, filename: str) -> str:
        """Normalize score name from file name"""
        return PurePath(filename).stem.replace("-", " ").replace("_", " ").capitalize()

    @classmethod
    def query_for_musician(cls, musician, query=None, with_draft_score=True):
        BM = cls.anyblok.BandManagement
        if not query:
            query = cls.query()

        query = query.join(BM.Score.music, isouter=with_draft_score)
        query = query.join(BM.Music.bands, isouter=with_draft_score)
        query = query.filter(
            sa.or_(
                BM.Band.uuid == musician.active_band.uuid,
                sa.and_(
                    BM.Band.uuid.is_(None),
                    BM.Score.imported_by == musician,
                ),
            )
        )
        query = query.distinct(
            BM.Score.uuid,
            BM.Score.name,
            BM.Music.title,
        )
        query = query.order_by(
            sa.nulls_first(BM.Music.title),
            BM.Score.name,
        )

        return query

    @classmethod
    def get_by(cls, ref, musician):
        """Score must be imported by the musician or
        the related music must be present in the musician
        active band"""
        score = cls.query().get(ref)
        if not score:
            return
        if score.imported_by == musician or (
            score.music and score.music.is_played_by(musician.active_band)
        ):
            return score
        raise PermissionDenied(
            _t(
                "You are not allowed to access to this score not link to your current band %(band_name)s",
                lang=musician.lang,
            )
            % {"band_name": musician.active_band.name}
        )

    @classmethod
    async def delete_by(cls, ref, musician):
        """Score can be removed only by the one who import
        it"""
        score = cls.query().get(ref)
        if not score.is_deletable:
            raise ValidationError(
                _t("Only scores unlink to its music can be removed", lang=musician.lang)
            )
        if score.imported_by != musician:
            raise PermissionDenied(
                _t(
                    "You are not allowed to delete this score. Only the one who imported it can remove it.",
                    lang=musician.lang,
                )
            )
        return await score.delete()

    def update_by(
        self,
        musician,
        name=None,
        source_writer_credits=None,
        music_uuid: str = None,
    ):
        BM = self.anyblok.BandManagement
        if name:
            self.name = name

        self.source_writer_credits = source_writer_credits or None

        music = None
        if music_uuid:
            music = BM.Music.query().filter_by(uuid=music_uuid).one_or_none()
        if music and self.music != music:
            music.ensure_musician_active_band(musician)
        self.music = music

    async def delete(self):
        StorageClass = storage_factory()
        medium = StorageClass(
            reference=self.uuid, storage_metadata=self.storage_file_metadata
        )
        await medium.remove()
        return super().delete()
