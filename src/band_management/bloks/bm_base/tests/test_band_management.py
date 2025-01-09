import pytest


from sqlalchemy.exc import IntegrityError


def test_band_management(bm):
    violin = bm.Instrument.insert(name="Violon")
    accordion = bm.Instrument.insert(name="Accordéon Sol/Do")
    bm.Instrument.insert(name="Accordéon La/Ré")
    bm.Instrument.insert(name="Trompette")

    pierre = bm.Musician.insert(name="Pierre")
    angele = bm.Musician.insert(name="Angele")
    mh = bm.Musician.insert(name="Marie-Hélène")

    pamh_band = bm.Band.query().filter(bm.Band.name.ilike("PAMH")).one()

    pierre_in_pahm = bm.Member.insert(musician=pierre, band=pamh_band)
    pierre_in_pahm.instruments.append(accordion)
    bm.Member.insert(musician=angele, band=pamh_band)
    pierre_in_pahm.instruments.append(violin)
    mh_in_pahm = bm.Member.insert(musician=mh, band=pamh_band)
    mh_in_pahm.instruments.append(accordion)

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
