import pytest
from anyblok.conftest import *  # noqa: F401,F403


@pytest.fixture()
def anyblok(rollback_registry):
    """Alias rollback registry"""
    return rollback_registry


@pytest.fixture(name="bm")
def band_management(anyblok):
    """Alias rollback registry"""
    return anyblok.BandManagement


@pytest.fixture(name="joe_user")
def joe_user(bm):
    joe_musician = (
        bm.Musician.query().filter(bm.Musician.email.ilike("joe@test.fr")).one()
    )
    return joe_musician.user
