from pathlib import PurePath
from anyblok import Declarations

from anyblok.relationship import Many2One
from anyblok.column import Text, Json


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
