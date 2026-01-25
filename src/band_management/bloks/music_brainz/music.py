from anyblok import Declarations
from anyblok.column import String, UUID, Text

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Music:
    musicbrainz_title: str = String(size=256, index=True)
    musicbrainz_artists: str = Text(label="Musicbrainz's artist", index=True)
    musicbrainz_uuid: UUID = UUID(
        label="Musicbrainz's reference", index=True, unique=True, nullable=True
    )

    @classmethod
    def query_any(cls, search: str, **kwargs):
        musics_query = super().query_any(search, **kwargs)
        for where_clause in musics_query.sql_statement._where_criteria:
            if where_clause.description == "or-search-clause":
                where_clause.clauses += (cls.musicbrainz_artists.ilike(f"%{search}%"),)
        return musics_query
