from pathlib import Path
import logging

from anyblok import configuration_post_load, load_init_function_from_entry_points

from anyblok.blok import BlokManager
from anyblok.config import Configuration, get_db_name, AnyBlokArgumentGroup
from anyblok.registry import RegistryManager

logger = logging.getLogger(__name__)


@Configuration.add("musicbrainz", label="Music Brainz")
def define_uvicorn_option(group: AnyBlokArgumentGroup) -> None:
    group.add_argument(
        "recording",
        help="JSON recording file",
        type=Path,
        # type=argparse.FileType("r"),
    )
    group.add_argument(
        "-n",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Dry run (no commit)",
    )
    group.add_argument(
        "--limit",
        dest="limit",
        type=int,
        help="Limit the number of record to parse",
    )
    group.add_argument(
        "--insert-buffer",
        dest="insert_buffer",
        type=int,
        default=1000,
        help="Commit SQL transaction every <insert-buffer> records inserted.",
    )


Configuration.add_application_properties(
    "musicbrainz-importer",
    ["musicbrainz"],
    prog="musicbrainz-importer",
    description=(
        "Import MusicBrainz's recording file "
        "from https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/"
    ),
)


def sync(anyblok_registry=None):
    load_init_function_from_entry_points()
    Configuration.load("musicbrainz-importer")
    configuration_post_load()
    if anyblok_registry is None:  # pragma: nocover
        BlokManager.load()
        db_name = get_db_name()
        anyblok_registry = RegistryManager.get(db_name)
    if anyblok_registry:
        # recording_file=Configuration.get("recording"),
        anyblok_registry.MusicBrainz.synchronize(
            recording_file=Configuration.get("recording").open(mode="r"),
            commit=not Configuration.get("dry_run"),
            parse_limit=Configuration.get("limit"),
            commit_buffer=Configuration.get("insert_buffer"),
        )
    else:
        logger.error("Couldn't start anyblok.")
