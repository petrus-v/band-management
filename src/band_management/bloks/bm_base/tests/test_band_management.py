import pytest


from sqlalchemy.exc import IntegrityError


def test_band_management(bm):
    violin = bm.Instrument.insert(name="Violon")
    accordion = bm.Instrument.insert(name="Accordéon Sol/Do")
    bm.Instrument.insert(name="Accordéon La/Ré")
    bm.Instrument.insert(name="Trompette")

    pierre = bm.Musician.query().filter_by(name="Pierre Verkest").one()
    joe = bm.Musician.query().filter_by(email="joe@test.fr").one()
    doe = bm.Musician.query().filter_by(email="doe@test.fr").one()

    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()

    pierre_in_pahm = bm.Member.insert(musician=pierre, band=pamh_band)
    pierre_in_pahm.instruments.append(accordion)
    joe_in_pahm = bm.Member.insert(musician=joe, band=pamh_band)
    joe_in_pahm.instruments.append(violin)
    doe_in_pahm = bm.Member.insert(musician=doe, band=pamh_band)
    doe_in_pahm.instruments.append(accordion)

    music_zelda = bm.Music.insert(
        title="Zelda",
        dance="Valse",
        composer="Philippe Plard",
    )
    bm.Score.insert(
        name="Voice 1 - Zelda",
        score_source_writer="Manqu'pas d'airs",
        music=music_zelda,
    )
    bm.Score.insert(
        name="Voice 2 - Zelda",
        score_source_writer="Manqu'pas d'airs",
        music=music_zelda,
    )
    pamh_band.musics.append(music_zelda)


def test_create_duplicate_band_name_raise(anyblok, bm):
    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()
    with pytest.raises(IntegrityError, match="anyblok_uq_b_band__name"):
        bm.Band.insert(name=pamh_band.name)
        # anyblok.flush()


def test_band_musicians_count(anyblok, bm):
    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()
    assert pamh_band.musicians_count == 2


def test_band_musics_count(anyblok, bm):
    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()
    assert pamh_band.musics_count == 1
