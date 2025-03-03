import pytest


from sqlalchemy.exc import IntegrityError


def test_create_duplicate_band_name_raise(bm):
    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()
    with pytest.raises(IntegrityError, match="anyblok_uq_b_band__name"):
        bm.Band.insert(name=pamh_band.name)


def test_band_musicians_count(bm):
    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()
    assert pamh_band.musicians_count == 2


def test_band_musics_count(bm):
    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()
    assert pamh_band.musics_count == 2
