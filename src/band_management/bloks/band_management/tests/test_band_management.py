
def test_band_management(bm):
    tone_gc = bm.Tone.query().filter(bm.Tone.name == "G / C").one()
    tone_ad = bm.Tone.query().filter(bm.Tone.name == "A / D").one()

    ts_68 = bm.TimeSignature.query().filter(bm.TimeSignature.name == "6/8").one()

    violin = bm.Instrument.insert(name="Violon")
    accordion = bm.Instrument.insert(name="Accordéon Sol/Do", tone=tone_gc)
    accordion_ad = bm.Instrument.insert(name="Accordéon La/Ré", tone=tone_ad)
    trumpet = bm.Instrument.insert(name="Trompette")

    pierre = bm.Musician.insert(name="Pierre")
    pierre.instruments.append(accordion)
    pierre.instruments.append(trumpet)


    angele = bm.Musician.insert(name="Angele")
    pierre.instruments.append(violin)


    mh = bm.Musician.insert(name="Marie-Hélène")
    mh.instruments.append(accordion)
    mh.instruments.append(accordion_ad)

    pamh_band = bm.Band.insert(name="PAMH")
    
    pierre_in_pahm = bm.MusicianPlayInBand.insert(musician=pierre, band=pamh_band)
    pierre_in_pahm.instruments.append(accordion)
    angele_in_pahm = bm.MusicianPlayInBand.insert(musician=angele, band=pamh_band)
    pierre_in_pahm.instruments.append(violin)
    mh_in_pahm = bm.MusicianPlayInBand.insert(musician=mh, band=pamh_band)
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
        time_signature=ts_68,
    )
    score_voice_2 = bm.Score.insert(
        name="Voice 2 - Zelda",
        score_source_writer="Manqu'pas d'airs",
        music=music_zelda,
        time_signature=ts_68,
    )
    pamh_band.musics.append(music_zelda)
