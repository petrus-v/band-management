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


def test_toggle_musician_active_band(connected_musician, joe_user, pamh_band):
    response = connected_musician.put(
        f"/musician/{joe_user.musician_uuid}/toggle-active-band/{pamh_band.uuid}"
    )
    assert response.status_code == 201, response.text
    assert response.headers["HX-Refresh"] == "true"


def test_toggle_musician_active_band_permission_denied(
    connected_musician, doe_musician, pamh_band
):
    response = connected_musician.put(
        f"/musician/{doe_musician.uuid}/toggle-active-band/{pamh_band.uuid}"
    )
    assert response.status_code == 401, response.text
