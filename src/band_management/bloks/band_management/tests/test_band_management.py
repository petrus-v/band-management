
def test_band_management(bm):

    violin = bm.Instrument.insert(name="Violon")
    accordion = bm.Instrument.insert(name="Accordéon Sol/Do")
    accordion_ad = bm.Instrument.insert(name="Accordéon La/Ré")
    trumpet = bm.Instrument.insert(name="Trompette")

    pierre = bm.Musician.insert(name="Pierre")
    angele = bm.Musician.insert(name="Angele")
    mh = bm.Musician.insert(name="Marie-Hélène")

    pamh_band = bm.Band.insert(name="PAMH")
    
    pierre_in_pahm = bm.Member.insert(musician=pierre, band=pamh_band)
    pierre_in_pahm.instruments.append(accordion)
    angele_in_pahm = bm.Member.insert(musician=angele, band=pamh_band)
    pierre_in_pahm.instruments.append(violin)
    mh_in_pahm = bm.Member.insert(musician=mh, band=pamh_band)
    mh_in_pahm.instruments.append(accordion)

    music_zelda = bm.Music.insert(
        title="Zelda",
        dance="Valse",
        composer="Philippe Plard",
    )
    score_voice_1 = bm.Score.insert(
        name="Voice 1 - Zelda",
        score_source_writer="Manqu'pas d'airs",
        music=music_zelda,
    )
    score_voice_2 = bm.Score.insert(
        name="Voice 2 - Zelda",
        score_source_writer="Manqu'pas d'airs",
        music=music_zelda,
    )
    pamh_band.musics.append(music_zelda)
