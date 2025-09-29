import pytest
from ..auth_api import create_access_token, get_current_user
from band_management import config
from band_management.bloks.http_auth_base.schemas.auth import (
    TokenDataSchema,
    UserSchema,
)
from band_management.exceptions import PermissionDenied
from jose import jwt
from fastapi.security import SecurityScopes
from datetime import timedelta, datetime, timezone


def test_auth_user(joe_user, webserver):
    response = webserver.post(
        "/token", data={"username": "joe", "password": "password"}
    )
    assert response.status_code == 200, response.text
    payload = jwt.decode(
        response.json()["access_token"],
        config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
    )
    token_data = TokenDataSchema(**payload)
    assert token_data.scopes == ["musician-auth"]
    assert token_data.sub == str(joe_user.uuid)


def test_auth_user_without_scope(no_scope_user, webserver):
    response = webserver.post(
        "/token", data={"username": "un-scope", "password": "user"}
    )
    assert response.status_code == 200
    payload = jwt.decode(
        response.json()["access_token"],
        config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
    )
    token_data = TokenDataSchema(**payload)
    assert token_data.scopes == []
    assert token_data.sub == str(no_scope_user.uuid)


def test_auth_unknown_user(webserver):
    response = webserver.post(
        "/token",
        data={"username": "abc", "password": "def"},
    )
    assert response.status_code == 401
    assert "Incorrect authentication" in response.text


def test_user_me(joe_rest_api_client, joe_user):
    response = joe_rest_api_client.get(
        "/api/user/me",
    )
    user = UserSchema(**response.json())
    assert user.musician.name == "Joe"
    assert user.uuid == joe_user.uuid


def test_user_me_with_expired_token(webserver, joe_user):
    token = create_access_token(
        data=joe_user.get_access_token_data(),
        expires_delta=timedelta(minutes=-1),
    )
    webserver.headers["Authorization"] = f"Bearer {token}"

    response = webserver.get(
        "/api/user/me",
    )
    assert response.status_code == 401
    assert "Could not validate credentials." in response.text


def test_create_access_token_default_timedelta(joe_user):
    token = create_access_token(
        data=joe_user.get_access_token_data(),
    )
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    token_data = TokenDataSchema(**payload)
    assert (
        token_data.exp
        >= (datetime.now(tz=timezone.utc) + timedelta(minutes=14)).timestamp()
    )


@pytest.mark.asyncio
async def test_valid_token_without_sub_raises(joe_user):
    user_data = joe_user.get_access_token_data()
    user_data.sub = ""
    token = create_access_token(
        data=user_data,
        expires_delta=timedelta(minutes=5),
    )
    with pytest.raises(PermissionDenied, match="Could not validate credentials") as ex:
        await get_current_user(
            SecurityScopes(),
            token,
        )
    assert ex.value.headers["WWW-Authenticate"] == "Bearer"


def test_access_denied_no_scope_user(webserver_no_scope_user):
    response = webserver_no_scope_user.get(
        "/api/user/me",
    )
    assert response.status_code == 401
    assert "Not enough permissions." in response.text
    assert response.headers["WWW-Authenticate"] == 'Bearer scope="musician-auth"'
