import pytest


@pytest.fixture
def pverkest_musician(bm):
    pverkest_musician = (
        bm.Musician.query().filter(bm.Musician.email.ilike("pierre@verkest.fr")).one()
    )
    return pverkest_musician


@pytest.fixture
def joe_musician(bm):
    joe_musician = (
        bm.Musician.query().filter(bm.Musician.email.ilike("joe@test.fr")).one()
    )
    return joe_musician


@pytest.fixture
def doe_musician(bm):
    doe = bm.Musician.query().filter(bm.Musician.email.ilike("doe@test.fr")).one()
    return doe


@pytest.fixture
def joe_user(joe_musician):
    return joe_musician.user


@pytest.fixture
def pverkest_user(pverkest_musician):
    return pverkest_musician.user


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
