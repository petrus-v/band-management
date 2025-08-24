from pathlib import PurePath
from anyblok import Declarations

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
