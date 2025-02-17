import pytest
from uuid_extensions import uuid7
from datetime import timedelta
from band_management.bloks.http_auth_base.auth_api import create_access_token
from pathlib import Path
from band_management import config
from anyblok_fastapi.conftest import webserver  # noqa: F401


@pytest.fixture(name="anonymous", scope="function")
def anonymous_user_http_client(webserver):  # noqa: F811
    if webserver.cookies.get("auth-token") is not None:
        webserver.cookies.pop("auth-token")

    yield webserver

    if webserver.cookies.get("auth-token") is not None:
        webserver.cookies.pop("auth-token")


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


@pytest.fixture(name="storage_directory", scope="session", autouse=True)
def storage_directory(tmp_path_factory) -> Path:
    original_path = config.ORIGINAL_SCORE_PATH
    storage_path = tmp_path_factory.mktemp("data-storage")
    config.ORIGINAL_SCORE_PATH = storage_path
    yield storage_path
    config.ORIGINAL_SCORE_PATH = original_path


@pytest.fixture
def fake_score_file(tmp_path):
    score = tmp_path / "zelda-voice-3.pdf"
    score.write_text("test", encoding="utf-8")
    return score


@pytest.fixture
def imported_score(bm, joe_user, storage_directory):
    score_uuid = uuid7()
    reference = str(score_uuid)
    relative_path = f"{reference[:2]}/{reference[2:]}"
    score = bm.Score.insert(
        uuid=score_uuid,
        name="Zelda - Voice 1",
        imported_by=joe_user.musician,
        storage_file_metadata={
            "mime_type": "application/pdf",
            "original_filename": "zelda-voice-1.pdf",
            "relative_path": relative_path,
            "size": 4,
        },
    )
    score_path = storage_directory / relative_path
    score_path.parent.mkdir(parents=True, exist_ok=True)
    with open(score_path, "w") as score_fp:
        score_fp.write("test Zelda voice 1")
    return score
