import pytest
from anyblok.conftest import *  # noqa: F401,F403
from anyblok_fastapi.conftest import webserver  # noqa: F401
from ..auth_api import create_access_token
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 3


@pytest.fixture(name="Auth")
def auth_registry(rollback_registry):
    """Alias rollback registry"""
    return rollback_registry.Auth


@pytest.fixture(name="joe_rest_api_client")
def webserver_joe_user(webserver, joe_user):  # noqa: F811
    token = create_access_token(
        data=joe_user.get_access_token_data(),
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    webserver.headers["Authorization"] = f"Bearer {token}"
    return webserver


@pytest.fixture(name="no_scope_user")
def unauthorized_user(bm, Auth):
    joe_musician = (
        bm.Musician.query().filter(bm.Musician.email.ilike("doe@test.fr")).one()
    )
    user = Auth.User.insert(musician=joe_musician)
    Auth.CredentialStore.insert(
        label="Test user without scopes",
        user=user,
        key="un-scope",
        secret="user",
    )
    return user


@pytest.fixture()
def webserver_no_scope_user(webserver, no_scope_user):  # noqa: F811
    token = create_access_token(
        data=no_scope_user.get_access_token_data(),
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    webserver.headers["Authorization"] = f"Bearer {token}"
    return webserver


@pytest.fixture(autouse=True)
def skip_if_installed(request, rollback_registry):
    if request.node.get_closest_marker("skip_if_installed"):
        if bloks_name := request.node.get_closest_marker("skip_if_installed").args:
            Blok = rollback_registry.System.Blok

            query = Blok.query()
            query = query.filter(Blok.name.in_(bloks_name))
            query = query.filter(Blok.state.in_(["installed", "toinstall", "toupdate"]))
            installed_bloks = query.all().name
            if installed_bloks:
                pytest.skip("skipping because: {} is installed".format(installed_bloks))
