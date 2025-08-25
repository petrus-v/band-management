import pytest
from band_management.bloks.http_auth_base.auth_api import create_access_token
from band_management.bloks.http_auth_base.schemas.auth import TokenDataSchema
from datetime import timedelta
from uuid_extensions import uuid7


def test_connected_musician_get_scores(connected_musician):
    response = connected_musician.get("/scores")
    assert response.status_code == 200, response.text


def test_connected_musician_search_scores(bm, connected_musician):
    response = connected_musician.post("/scores", data={"search": "ze"})
    assert response.status_code == 200, response.text


def test_connected_musician_empty_search_scores(bm, connected_musician):
    response = connected_musician.post("/scores", data={"search": ""})
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_connected_musician_post_score(
    storage_directory, fake_score_file, bm, connected_musician
):
    with open(fake_score_file, "rb") as f:
        response = connected_musician.post(
            "/score/",
            data={},
            files=[
                ("score_files", ("zelda-voice-3.pdf", f, "plop")),
            ],
        )
    assert response.status_code == 201, response.text

    score = bm.Score.query().filter(bm.Score.name.like("Zelda voice 3")).one()
    reference = str(score.uuid)
    relative_path = f"{reference[:2]}/{reference[2:]}"
    assert (storage_directory / relative_path).exists()
    assert (storage_directory / relative_path).is_file()
    assert score.name == "Zelda voice 3"
    assert score.storage_file_metadata == {
        "mime_type": "plop",
        "original_filename": "zelda-voice-3.pdf",
        "relative_path": relative_path,
        "size": 4,
    }


@pytest.mark.asyncio
async def test_connected_musician_post_score_guess_mime_type(
    storage_directory, fake_score_file, bm, connected_musician
):
    with open(fake_score_file, "rb") as f:
        response = connected_musician.post(
            "/score/",
            data={},
            files=[
                ("score_files", ("zelda-voice-3.pdf", f, "")),
            ],
        )
    assert response.status_code == 201, response.text

    score = bm.Score.query().filter(bm.Score.name.like("Zelda voice 3")).one()
    reference = str(score.uuid)
    relative_path = f"{reference[:2]}/{reference[2:]}"
    assert (storage_directory / relative_path).exists()
    assert (storage_directory / relative_path).is_file()
    assert score.name == "Zelda voice 3"
    assert score.storage_file_metadata == {
        "mime_type": "application/pdf",
        "original_filename": "zelda-voice-3.pdf",
        "relative_path": relative_path,
        "size": 4,
    }
    assert response.headers["hx-redirect"] == f"/score/{reference}", response.text


@pytest.mark.asyncio
async def test_connected_musician_post_multiple_files(
    storage_directory, fake_score_file, bm, connected_musician
):
    with open(fake_score_file, "rb") as f:
        response = connected_musician.post(
            "/score/",
            data={},
            files=[
                ("score_files", ("Au-coin-du-feux-voice-1.pdf", f, "plop")),
                ("score_files", ("Au-coin-du-feux-voice-2.pdf", f, "plop")),
            ],
        )
    assert response.status_code == 201, response.text

    score_voice1 = (
        bm.Score.query().filter(bm.Score.name.like("Au coin du feux voice 1")).one()
    )
    score_voice2 = (
        bm.Score.query().filter(bm.Score.name.like("Au coin du feux voice 2")).one()
    )
    reference = str(score_voice1.uuid)
    relative_path = f"{reference[:2]}/{reference[2:]}"
    assert (storage_directory / relative_path).exists()
    assert (storage_directory / relative_path).is_file()
    reference = str(score_voice2.uuid)
    relative_path = f"{reference[:2]}/{reference[2:]}"
    assert (storage_directory / relative_path).exists()
    assert (storage_directory / relative_path).is_file()

    assert response.headers["hx-redirect"] == "/scores/", response.text


@pytest.mark.asyncio
async def test_get_score_media_no_user_found_raises(anonymous, imported_score):
    token = create_access_token(
        data=TokenDataSchema(sub=str(uuid7()), scopes=["musician-auth"]),
        expires_delta=timedelta(minutes=10),
    )
    anonymous.cookies["auth-token"] = f"{token}"
    response = anonymous.get(f"/score/{imported_score.uuid}/media")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not enough permissions"


@pytest.mark.asyncio
async def test_get_score_media_anonymous_raises(anonymous, imported_score):
    response = anonymous.get(f"/score/{imported_score.uuid}/media")
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_get_score_media(imported_score, connected_musician):
    response = connected_musician.get(f"/score/{imported_score.uuid}/media")
    assert response.status_code == 200, response.text


def test_connected_musician_prepare_score(bm, connected_musician):
    response = connected_musician.get("/score/prepare")
    assert response.status_code == 200, response.text


def test_connected_musician_get_score(bm, connected_musician, joe_musician):
    score = bm.Score.insert(name="test", imported_by=joe_musician)
    response = connected_musician.get(f"/score/{score.uuid}")
    assert response.status_code == 200, response.text


def test_connected_musician_update_score(bm, connected_musician, joe_user, zelda_music):
    score = bm.Score.insert(name="test", imported_by=joe_user.musician)
    score.refresh()
    response = connected_musician.put(
        f"/score/{score.uuid}",
        data={
            "score_name": "other",
            "source_writer_credits": "writer credit",
            "score_music": str(zelda_music.uuid),
        },
    )
    assert response.status_code == 200, response.text
    score.refresh()
    assert score.name == "other"
    assert score.source_writer_credits == "writer credit"
    assert score.music == zelda_music


def test_connected_musician_update_unknown_score(
    bm, connected_musician, joe_user, zelda_music
):
    score = bm.Score.insert(name="test", imported_by=joe_user.musician)
    score.refresh()
    response = connected_musician.put(
        f"/score/{uuid7()}",
        data={
            "score_name": "other",
            "source_writer_credits": "writer credit",
            "score_music": str(zelda_music.uuid),
        },
    )
    assert response.status_code == 404, response.text


def test_connected_musician_update_score_without_music(
    bm, connected_musician, joe_user, zelda_music
):
    score = bm.Score.insert(
        name="test", imported_by=joe_user.musician, music=zelda_music
    )
    score.refresh()
    response = connected_musician.put(
        f"/score/{score.uuid}",
        data={
            "score_name": "other",
            "source_writer_credits": "writer credit",
            "score_music": "",
        },
    )
    assert response.status_code == 200, response.text
    score.refresh()
    assert score.name == "other"
    assert score.source_writer_credits == "writer credit"
    assert score.music is None


@pytest.mark.asyncio
async def test_delete_score(bm, connected_musician, imported_score):
    response = connected_musician.delete(f"/score/{imported_score.uuid}")
    assert response.status_code == 204, response.text
