import pytest
from unittest import mock
from fastapi import HTTPException
from ..fastapi_utils import get_authenticated_musician
from fastapi.security import SecurityScopes
from band_management.bloks.http_auth_base.auth_api import create_access_token
from band_management.bloks.http_auth_base.schemas.auth import TokenDataSchema
from datetime import timedelta
from uuid_extensions import uuid7
from freezegun import freeze_time
from band_management import config
from datetime import datetime, timezone


def test_invalid_token_ignored_public_page(anonymous):
    anonymous.cookies["auth-token"] = "invalid"
    anonymous.get("/terms")


def test_invalid_token_return_401(anonymous):
    anonymous.cookies["auth-token"] = "invalid"
    response = anonymous.get("/bands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing permissions"


def test_expired_token_return_401(anonymous, joe_user):
    expired_token_session = anonymous
    expired_token = create_access_token(
        data=joe_user.get_access_token_data(),
        expires_delta=timedelta(minutes=-1),
    )
    expired_token_session.cookies["auth-token"] = f"{expired_token}"
    response = anonymous.get("/bands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing permissions"


def test_valid_token_unknown_user_return_401(anonymous):
    unknown_user_session = anonymous
    unknown_user_token = create_access_token(
        data=TokenDataSchema(sub=str(uuid7()), scopes=["musician-auth"]),
        expires_delta=timedelta(minutes=10),
    )
    unknown_user_session.cookies["auth-token"] = f"{unknown_user_token}"
    response = unknown_user_session.get("/bands")
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
            mock.Mock(),
            SecurityScopes(["test"]),
            connected_musician.cookies["auth-token"],
        )


def test_anonymous_band_management_brand_page(anonymous):
    response = anonymous.get("/")
    assert response.status_code == 200, response.text


def test_anonymous_band_management_login_page(anonymous):
    response = anonymous.get("/login")
    assert response.status_code == 200, response.text


def test_anonymous_band_management_login(anonymous):
    assert not anonymous.cookies.get("auth-token")
    response = anonymous.post(
        "/login",
        data={"username": "joe", "password": "password"},
        follow_redirects=False,
    )
    assert response.headers["hx-redirect"] == "/home", response.text
    assert response.status_code == 202, response.text
    assert anonymous.cookies.get("auth-token")


def test_already_connected_band_management_index(connected_musician):
    token = connected_musician.cookies.get("auth-token")
    assert token
    response = connected_musician.get(
        "/",
        follow_redirects=False,
    )
    assert response.status_code == 200, response.text
    assert response.headers["hx-redirect"] == "/home", response.text


def test_already_connected_band_management_login(connected_musician):
    token = connected_musician.cookies.get("auth-token")
    assert token
    response = connected_musician.get(
        "/login",
        follow_redirects=False,
    )
    assert response.status_code == 200, response.text
    assert response.headers["hx-redirect"] == "/home", response.text
    assert not response.cookies.get("auth-token")


def test_already_connected_refresh_token(request, connected_musician):
    token = connected_musician.cookies.get("auth-token")
    with freeze_time(
        datetime.now(tz=timezone.utc)
        + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
            - config.ACCESS_TOKEN_RENEW_MINUTES / 2
        )
    ):
        response = connected_musician.get(
            "/home",
        )
    assert response.status_code == 200, response.text
    assert response.cookies.get("auth-token") != token


def test_anonymous_band_management_login_with_redirect(anonymous):
    assert not anonymous.cookies.get("auth-token")
    response = anonymous.post(
        "/login", data={"username": "joe", "password": "password"}
    )
    assert response.status_code == 202, response.text
    assert response.cookies.get("auth-token")
    assert response.headers["hx-redirect"] == "/home", response.text


def test_anonymous_band_management_login_wrong_login(anonymous):
    response = anonymous.post(
        "/login",
        data={"username": "joeWrong", "password": "password"},
        follow_redirects=False,
    )
    assert response.status_code == 401, response.text


def test_anonymous_band_management_login_credentials(anonymous):
    assert not anonymous.cookies.get("auth-token")
    response = anonymous.post(
        "/login",
        data={"username": "joeWrong", "password": "passwordWrong"},
        follow_redirects=False,
    )
    assert response.status_code == 401, response.text
    assert not response.cookies.get("auth-token")


def test_logout(connected_musician):
    assert connected_musician.cookies.get("auth-token")
    response = connected_musician.post(
        "/logout",
    )
    assert response.status_code == 200, response.text
    assert response.headers["hx-redirect"] == "/", response.text
    assert not response.cookies.get("auth-token")


def test_connected_musician_home(connected_musician):
    response = connected_musician.get("/home")
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
