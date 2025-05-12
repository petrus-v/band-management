import json
import logging
import textwrap

from anyblok import Declarations

register = Declarations.register
Model = Declarations.Model


logger = logging.getLogger(__name__)


@register(Model)
class MusicBrainz:
    @classmethod
    def synchronize(
        cls,
        recording_file,
        commit=False,
        parse_limit=None,
        commit_buffer=1000,
    ):
        parsed = 0
        inserted = 0
        while recording := recording_file.readline():
            parsed += 1
            if parse_limit and parsed > parse_limit:
                logger.warning(
                    "Stop importing because we get the parsed limit %d >= %d",
                    parsed,
                    parse_limit,
                )
                break
            brainz_music = json.loads(recording)
            exists = (
                cls.anyblok.BandManagement.Music.query()
                .filter_by(musicbrainz_uuid=brainz_music["id"])
                .one_or_none()
            )
            if exists:
                continue

            composers = []
            authors = []
            artists = []
            for relation in brainz_music.get("relations", []):
                if relation.get("target-type") != "artist":
                    continue
                if not (artist_name := relation.get("artist", {}).get("name")):
                    continue
                if relation.get("type") in ["composer", "librettist"]:
                    composers.append(artist_name)
                if relation.get("type") == "orchestrator":
                    artists.append(artist_name)
                if relation.get("type") in ["lyricist", "writer"]:
                    authors.append(artist_name)

            cls.anyblok.BandManagement.Music.insert(
                title=textwrap.shorten(
                    brainz_music["title"], width=256, placeholder="..."
                ),
                composer=textwrap.shorten(
                    ", ".join(composers), width=256, placeholder="..."
                ),
                author=textwrap.shorten(
                    ", ".join(authors), width=256, placeholder="..."
                ),
                musicbrainz_title=textwrap.shorten(
                    brainz_music["title"], width=256, placeholder="..."
                ),
                musicbrainz_artists=", ".join(artists),
                musicbrainz_uuid=brainz_music["id"],
            )
            inserted += 1
            if inserted % commit_buffer == 0:
                logger.warning(
                    "%s %d records over %d music parsed",
                    "Commit" if commit else "Rollback",
                    inserted,
                    parsed,
                )
                if commit:
                    cls.anyblok.commit()
                else:
                    cls.anyblok.rollback()

        if commit:
            cls.anyblok.commit()
