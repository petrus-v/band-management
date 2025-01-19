import pytest
from anyblok_fastapi.conftest import webserver  # noqa: F401


@pytest.fixture(name="anonymous")
def anonymous_user_http_client(webserver):  # noqa: F811
    return webserver


@pytest.fixture(name="band_leader")
def band_leader_user_http_client(webserver):  # noqa: F811
    return webserver
