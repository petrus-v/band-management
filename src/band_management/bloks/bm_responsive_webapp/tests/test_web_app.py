import pytest
from fastapi import HTTPException
from ..main import get_authenticated_musician
from fastapi.security import SecurityScopes
from band_management.bloks.http_auth_base.auth_api import create_access_token
from band_management.bloks.http_auth_base.schemas.auth import TokenDataSchema
from datetime import timedelta
from uuid_extensions import uuid7


def test_invalid_token_ignored_public_page(anonymous):
    anonymous.cookies["auth-token"] = "invalid"
    anonymous.get("/terms")


def test_invalid_token_return_401(anonymous):
    anonymous.cookies["auth-token"] = "invalid"
    response = anonymous.get("/bands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing permissions"


def test_expired_token_return_401(anonymous, joe_user):
    token = create_access_token(
        data=joe_user.get_access_token_data(),
        expires_delta=timedelta(minutes=-1),
    )
    expired_token = anonymous
    expired_token.cookies["auth-token"] = f"{token}"
    response = anonymous.get("/bands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing permissions"


def test_valid_token_unknow_user_return_401(anonymous):
    token = create_access_token(
        data=TokenDataSchema(sub=str(uuid7()), scopes=["musician-auth"]),
        expires_delta=timedelta(minutes=10),
    )
    anonymous.cookies["auth-token"] = f"{token}"
    response = anonymous.get("/bands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not enough permissions"


def test_notken_return_401(anonymous):
    response = anonymous.get("/bands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing permissions"


@pytest.mark.asyncio
async def test_get_authenticated_musician(connected_musician):
    with pytest.raises(HTTPException, match="Missing permissions"):
        await get_authenticated_musician(
            SecurityScopes(["test"]), connected_musician.cookies["auth-token"]
        )


def test_anonymous_band_management_brand_page(anonymous):
    response = anonymous.get("/")
    assert response.status_code == 200, response.text


def test_anonymous_band_management_login_page(anonymous):
    response = anonymous.get("/login")
    assert response.status_code == 200, response.text


def test_anonymous_band_management_login(anonymous):
    response = anonymous.post(
        "/login",
        data={"username": "joe", "password": "password"},
        follow_redirects=False,
    )
    assert response.status_code == 202, response.text


def test_anonymous_band_management_login_with_redirect(anonymous):
    response = anonymous.post(
        "/login", data={"username": "joe", "password": "password"}
    )
    assert response.status_code == 202, response.text
    assert response.headers["hx-redirect"] == "/home", response.text


def test_anonymous_band_management_login_wrong_login(anonymous):
    response = anonymous.post(
        "/login",
        data={"username": "joeWrong", "password": "password"},
        follow_redirects=False,
    )
    assert response.status_code == 401, response.text


def test_anonymous_band_management_login_credentials(anonymous):
    response = anonymous.post(
        "/login",
        data={"username": "joeWrong", "password": "passwordWrong"},
        follow_redirects=False,
    )
    assert response.status_code == 401, response.text


def test_logout(connected_musician):
    response = connected_musician.post(
        "/logout",
    )
    assert response.status_code == 200, response.text
    assert response.headers["hx-redirect"] == "/", response.text
    assert not response.cookies.get("auth-token")


def test_connected_musician_home(connected_musician):
    response = connected_musician.get("/home")
    assert response.status_code == 200, response.text


def test_connected_musician_get_bands(connected_musician):
    response = connected_musician.get("/bands")
    assert response.status_code == 200, response.text


def test_connected_musician_search_bands(bm, connected_musician):
    response = connected_musician.post("/bands", data={"search": "PA"})
    assert response.status_code == 200, response.text


def test_connected_musician_post_band(bm, connected_musician):
    response = connected_musician.post("/band/", data={"band_name": "Band name"})
    assert response.status_code == 201, response.text

    band = bm.Band.query().filter(bm.Band.name.like("Band name")).one()
    assert band.name == "Band name"


def test_connected_musician_prepare_band(bm, connected_musician):
    response = connected_musician.get("/band/prepare")
    assert response.status_code == 200, response.text


def test_connected_musician_get_band(bm, connected_musician):
    band = bm.Band.query().filter(bm.Band.name.like("PAMH")).one()
    response = connected_musician.get(f"/band/{band.uuid}")
    assert response.status_code == 200, response.text


def test_connected_musician_update_band(bm, connected_musician):
    band = bm.Band.query().filter(bm.Band.name.like("PAMH")).one()
    response = connected_musician.put(f"/band/{band.uuid}", data={"band_name": "other"})
    assert response.status_code == 200, response.text
    band.refresh()
    assert band.name == "other"


def test_connected_musician_get_scores(connected_musician):
    response = connected_musician.get("/scores")
    assert response.status_code == 200, response.text


def test_connected_musician_search_scores(bm, connected_musician):
    response = connected_musician.post("/scores", data={"search": "ze"})
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_connected_musician_post_score(
    storage_directory, fake_score_file, bm, connected_musician
):
    with open(fake_score_file, "rb") as f:
        response = connected_musician.post(
            "/score/",
            data={},
            files={"score_file": ("zelda-voice-3.pdf", f, "plop")},
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
            files={"score_file": ("zelda-voice-3.pdf", f, "")},
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


def test_connected_musician_get_score(bm, connected_musician):
    score = bm.Band.insert(name="test")
    response = connected_musician.get(f"/score/{score.uuid}")
    assert response.status_code == 200, response.text


def test_connected_musician_update_score(bm, connected_musician, joe_user):
    score = bm.Score.insert(name="test", imported_by=joe_user.musician)
    score.refresh()
    response = connected_musician.put(
        f"/score/{score.uuid}",
        data={"score_name": "other", "source_writer_credits": ""},
    )
    assert response.status_code == 200, response.text
    score.refresh()
    assert score.name == "other"


def test_connected_musician_get_musics(connected_musician):
    response = connected_musician.get("/musics")
    assert response.status_code == 200, response.text


def test_connected_musician_get_profile(connected_musician):
    response = connected_musician.get("/profile")
    assert response.status_code == 200, response.text


def test_band_register(anonymous):
    response = anonymous.get("/register")
    assert response.status_code == 200, response.text


def test_band_terms(anonymous):
    response = anonymous.get("/terms")
    assert response.status_code == 200, response.text


def test_band_credits(anonymous):
    response = anonymous.get("/credits")
    assert response.status_code == 200, response.text
