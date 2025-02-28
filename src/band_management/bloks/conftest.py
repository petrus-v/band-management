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


@pytest.fixture(name="joe_musician")
def joe_musician(bm):
    joe_musician = (
        bm.Musician.query().filter(bm.Musician.email.ilike("joe@test.fr")).one()
    )
    return joe_musician


@pytest.fixture(name="doe_musician")
def doe_musician(bm):
    doe = bm.Musician.query().filter(bm.Musician.email.ilike("doe@test.fr")).one()
    return doe


@pytest.fixture(name="joe_user")
def joe_user(joe_musician):
    return joe_musician.user


@pytest.fixture()
def pamh_band(bm):
    return bm.Band.query().filter_by(name="PAMH").one()


@pytest.fixture()
def trib_band(bm):
    return bm.Band.query().filter_by(name="Tribardeurs").one()


@pytest.fixture()
def tradamuse_band(bm):
    return bm.Band.query().filter_by(name="Trad'amuse").one()


@pytest.fixture
def zelda_music(bm):
    return bm.Music.query().filter_by(title="Zelda").one()


@pytest.fixture
def elle_music(bm):
    return bm.Music.query().filter_by(title="Elle").one()


@pytest.fixture
def esperanza_music(bm):
    return bm.Music.query().filter_by(title="Esperanza").one()
