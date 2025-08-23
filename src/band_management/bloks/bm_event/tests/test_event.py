import pytest
from unittest import mock
from uuid_extensions import uuid7


@pytest.fixture
def new_music(bm, pamh_band):
    music_test = bm.Music.insert(
        title="Test",
        dance="Scottish",
        composer="Test",
    )
    pamh_band.musics.append(music_test)
    return music_test


@pytest.fixture
def music_without_band(bm):
    music_test = bm.Music.insert(
        uuid=uuid7(),
        title="Test without band",
        dance="Mazurka",
        composer="Test",
    )
    return music_test


def test_print_document(event):
    pdf = event.print("fr")
    assert pdf is not None
    # with open("test.pdf", "wb") as f:
    #     f.write(pdf)


def test_print_for(event, pverkest_musician):
    with mock.patch("band_management.bloks.bm_event.event.Event.print") as mo:
        event.print_for(pverkest_musician)

    mo.assert_called_once_with(pverkest_musician.lang)


def test_update_event_musics_add_new_music(bm, event, new_music):
    assert len(event.musics) == 2
    event_music_1 = event.musics[0]
    event_music_2 = event.musics[1]
    new_uuid = uuid7()
    event.update_event_musics(
        [str(event_music_2.uuid), str(new_uuid), str(event_music_1.uuid)],
        [
            str(event_music_2.music.uuid),
            str(new_music.uuid),
            str(event_music_1.music.uuid),
        ],
        [
            "comment music 2",
            "comment new music",
            "comment music 1",
        ],
    )

    expected = {
        event_music_1.music.uuid: {
            "uuid": str(event_music_2.uuid),
            "position": 3,
            "comment": "comment music 1",
        },
        event_music_2.music.uuid: {
            "uuid": str(new_uuid),
            "position": 1,
            "comment": "comment music 2",
        },
        new_music.uuid: {
            "uuid": str(event_music_1.uuid),
            "position": 2,
            "comment": "comment new music",
        },
    }

    assert len(event.musics) == 3
    for event in sorted(event.musics, key=lambda evt: evt.sequence):
        assert event.sequence == expected[event.music.uuid]["position"]
        assert event.comment == expected[event.music.uuid]["comment"]


def test_update_event_musics_add_new_music_and_remove(bm, event, new_music):
    assert len(event.musics) == 2
    event.musics[0]
    event_music_2 = event.musics[1]
    event.update_event_musics(
        [
            str(event_music_2.uuid),
            str(uuid7()),
        ],
        [
            str(event_music_2.music.uuid),
            str(new_music.uuid),
        ],
        [
            "comment music 2",
            "comment new music",
        ],
    )

    expected = {
        event_music_2.music.uuid: {
            "position": 1,
            "comment": "comment music 2",
        },
        new_music.uuid: {
            "position": 2,
            "comment": "comment new music",
        },
    }

    assert len(event.musics) == 2

    for event in sorted(event.musics, key=lambda evt: evt.sequence):
        assert event.sequence == expected[event.music.uuid]["position"]
        assert event.comment == expected[event.music.uuid]["comment"]


def test_update_event_unknown_music(bm, event, new_music):
    new_uuid = uuid7()
    unknown_music = uuid7()
    with pytest.raises(ValueError, match=f"Music reference {unknown_music} not found"):
        event.update_event_musics(
            [str(new_uuid), str(new_music.uuid)],
            [
                str(unknown_music),
                str(new_music.uuid),
            ],
            [
                "Unknown music",
                "comment new music",
            ],
        )


def test_update_event_non_band_related_music(bm, event, new_music, music_without_band):
    new_uuid = uuid7()
    with pytest.raises(
        ValueError,
        match=f"This music {music_without_band.title} is not played by the current band {event.band.name}",
    ):
        event.update_event_musics(
            [str(new_uuid), str(new_music.uuid)],
            [
                str(music_without_band.uuid),
                str(new_music.uuid),
            ],
            [
                "Unknown music",
                "comment new music",
            ],
        )


def test_event_copy(bm, event):
    new_event = event.copy()
    assert new_event.uuid != event.uuid
    assert len(new_event.musics) == len(event.musics)
    assert [event_music.uuid for event_music in new_event.musics] != [
        event_music.uuid for event_music in event.musics
    ]
    assert [event_music.music_uuid for event_music in new_event.musics] == [
        event_music.music_uuid for event_music in event.musics
    ]
    assert new_event.uri_code != event.uri_code


def test_delete_event(bm, event):
    event_music_0_uuid = str(event.musics[0].uuid)
    event.delete()
    assert bm.EventMusic.query().get(event_music_0_uuid) is None
