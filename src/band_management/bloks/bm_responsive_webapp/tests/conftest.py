import pytest
from datetime import timedelta
from band_management.bloks.http_auth_base.auth_api import create_access_token

from anyblok_fastapi.conftest import webserver  # noqa: F401


@pytest.fixture(name="anonymous")
def anonymous_user_http_client(webserver):  # noqa: F811
    return webserver


@pytest.fixture(name="joe_http_client")
def webserver_joe_user(webserver, joe_user):  # noqa: F811
    token = create_access_token(
        data=joe_user.get_access_token_data(),
        expires_delta=timedelta(minutes=10),
    )
    webserver.cookies["auth-token"] = f"{token}"
    return webserver


@pytest.fixture(name="connected_musician")
def band_leader_user_http_client(joe_http_client):  # noqa: F811
    return joe_http_client
