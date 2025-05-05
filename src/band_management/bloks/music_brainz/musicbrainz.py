import json
import logging

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
            cls.anyblok.BandManagement.Music.insert(
                title=brainz_music["title"][:256],
                musicbrainz_title=brainz_music["title"][:256],
                musicbrainz_artists="".join(
                    [
                        artist["name"] + artist["joinphrase"]
                        for artist in brainz_music["artist-credit"]
                    ]
                ),
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
