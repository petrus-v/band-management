import pytest
from pathlib import Path
from band_management.bloks.music_brainz.scripts.musicbrainz_importer import sync

from unittest import mock


@pytest.fixture
def recording_file():
    return Path(__file__).parent / "fixtures" / "recording"


def test_import(anyblok, recording_file):
    count_before = anyblok.BandManagement.Music.query().count()
    anyblok.MusicBrainz.synchronize(
        recording_file.open(mode="r"),
        commit=False,
        parse_limit=2,
        commit_buffer=3,
    )
    assert 2 == (anyblok.BandManagement.Music.query().count() - count_before)


def test_import_flushing_by_rollback(anyblok, recording_file):
    count_before = anyblok.BandManagement.Music.query().count()
    anyblok.MusicBrainz.synchronize(
        recording_file.open(mode="r"),
        commit=False,
        commit_buffer=2,
    )
    # there is 5 entries in the tests files
    # as buffer to 2 the 4 firsts are rollback
    # leaing only the last one present on the current
    # transaction
    assert 1 == (anyblok.BandManagement.Music.query().count() - count_before)


def test_import_flushing_by_commit(request, anyblok, recording_file):
    original_commit = anyblok.commit

    def restore_commit():
        anyblok.commit = original_commit

    request.addfinalizer(restore_commit)

    anyblok.commit = mock.MagicMock()
    count_before = anyblok.BandManagement.Music.query().count()
    anyblok.MusicBrainz.synchronize(
        recording_file.open(mode="r"),
        commit=True,
        commit_buffer=2,
    )
    # there is 5 entries in the tests files
    # as buffer to 2 commit is called 3 times
    assert anyblok.commit.call_count == 3
    assert 5 == (anyblok.BandManagement.Music.query().count() - count_before)


def test_import_import_twice_no_duplicate(anyblok, recording_file):
    count_before = anyblok.BandManagement.Music.query().count()
    anyblok.MusicBrainz.synchronize(
        recording_file.open(mode="r"),
        commit=False,
    )
    anyblok.MusicBrainz.synchronize(
        recording_file.open(mode="r"),
        commit=False,
    )
    assert 5 == (anyblok.BandManagement.Music.query().count() - count_before)


def test_parser_01(anyblok, recording_file):
    with (
        mock.patch(
            "sys.argv",
            [
                "import-prog",
                str(recording_file),
            ],
        ),
        mock.patch(
            "band_management.bloks.music_brainz.musicbrainz.MusicBrainz.synchronize"
        ) as sync_mock,
    ):
        sync(anyblok_registry=anyblok)
        sync_mock.assert_called_once()
        expected = dict(
            commit=True,
            parse_limit=None,
            commit_buffer=1000,
        )
        for key, expected_value in expected.items():
            assert sync_mock.call_args.kwargs[key] == expected_value


def test_parser_02(anyblok, recording_file):
    with (
        mock.patch(
            "sys.argv",
            [
                "import-prog",
                str(recording_file),
                "-n",
                "--limit",
                "20",
                "--insert-buffer",
                "10",
            ],
        ),
        mock.patch(
            "band_management.bloks.music_brainz.musicbrainz.MusicBrainz.synchronize"
        ) as sync_mock,
    ):
        sync(anyblok_registry=anyblok)
        sync_mock.assert_called_once()
        expected = dict(
            commit=False,
            parse_limit=20,
            commit_buffer=10,
        )
        for key, expected_value in expected.items():
            assert sync_mock.call_args.kwargs[key] == expected_value


def test_parser_03(anyblok, recording_file):
    with (
        mock.patch(
            "sys.argv",
            [
                "import-prog",
                str(recording_file),
                "-n",
                "--limit",
                "20",
                "--insert-buffer",
                "10",
            ],
        ),
        mock.patch(
            "band_management.bloks.music_brainz.musicbrainz.MusicBrainz.synchronize"
        ) as sync_mock,
    ):
        sync(anyblok_registry=False)
        sync_mock.assert_not_called()
