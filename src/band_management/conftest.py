import pytest
from pathlib import Path
from band_management import config
from anyblok.conftest import *  # noqa: F401,F403

from fastapi import UploadFile


@pytest.fixture()
def score_attachment(tmp_path):
    score_path = tmp_path / "myscore.pdf"

    with score_path.open("w") as f:
        f.write("score data")
    return score_path


@pytest.fixture()
def uploaded_score_attachment(score_attachment):
    return UploadFile(score_attachment.open("rb"), filename=score_attachment.name)


@pytest.fixture(scope="function")
def anyblok(rollback_registry):
    """Alias rollback registry"""
    return rollback_registry


@pytest.fixture(name="bm")
def band_management(anyblok):
    """Alias rollback registry"""
    return anyblok.BandManagement


@pytest.fixture(name="storage_directory", scope="session", autouse=True)
def storage_directory(tmp_path_factory) -> Path:
    original_path = config.ORIGINAL_SCORE_PATH
    storage_path = tmp_path_factory.mktemp("data-storage")
    config.ORIGINAL_SCORE_PATH = storage_path
    try:
        yield storage_path
    except Exception:
        config.ORIGINAL_SCORE_PATH = original_path
        raise


@pytest.fixture(name="predictive_jwt_config", scope="session", autouse=True)
def predictive_jwt_config() -> Path:
    config.SECRET_KEY = "abc"
    config.ALGORITHM = "HS256"
    config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    config.ACCESS_TOKEN_RENEW_MINUTES = 2
    config.INVITATION_TOKEN_EXPIRE_DAYS = 5
    config.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 10
