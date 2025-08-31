def test_score_name_from_filename(bm):
    assert (
        bm.Score.name_from_filename("valse-des-petits-CHEVAUX_de-Bois.pdf")
        == "Valse des petits chevaux de bois"
    )


def test_query_for_musician(bm, joe_pamh_current_active_band):
    scores = bm.Score.query_for_musician(joe_pamh_current_active_band).all()
    # 1 score imported (polka pomme)
    # 1 score with music no bands (jet du lama)
    # 3 PAMH as 2 music with 3 scores: 1 envole + 2 zelda
    assert len(scores) == 5
    assert [(s.music.title if s.music else "", s.name) for s in scores] == [
        ("", "Polka pomme"),
        ("Le Jet du Lama", "Voice 1 - G/C accordéon"),
        ("L'envole", "Voice 1"),
        (
            "Zelda",
            "Voice 1 - Zelda",
        ),
        ("Zelda", "Voice 2 - Zelda"),
    ]


def test_query_for_musician_without_draft_scores(bm, joe_pamh_current_active_band):
    scores = bm.Score.query_for_musician(
        joe_pamh_current_active_band, with_draft_score=False
    ).all()
    # 3 PAMH as 2 music with 3 scores: 1 envole + 2 zelda
    assert len(scores) == 3
    assert [(s.music.title if s.music else "", s.name) for s in scores] == [
        ("L'envole", "Voice 1"),
        (
            "Zelda",
            "Voice 1 - Zelda",
        ),
        ("Zelda", "Voice 2 - Zelda"),
    ]


def test_query_for_musician_trib_active(bm, joe_musician, trib_band):
    joe_musician.set_active_band(trib_band.uuid)
    scores_query = bm.Score.query_for_musician(joe_musician, query=bm.Score.query())
    scores = scores_query.all()
    assert len(scores) == 5
    # 1 score imported (polka pomme)
    # 1 score with music no bands (jet du lama)
    # 3 tradamuse as 2 music with 3 scores: 1 esperanza + 2 zelda
    assert [(s.music.title if s.music else "", s.name) for s in scores] == [
        ("", "Polka pomme"),
        ("Esperanza", "Voice 1"),
        ("Le Jet du Lama", "Voice 1 - G/C accordéon"),
        (
            "Zelda",
            "Voice 1 - Zelda",
        ),
        ("Zelda", "Voice 2 - Zelda"),
    ]


def test_score_update_by(bm, joe_pamh_current_active_band, pamh_band, esperanza_music):
    assert pamh_band not in esperanza_music.bands
    esperanza_voice_3 = bm.Score.insert(
        name="voice 3", imported_by=joe_pamh_current_active_band
    )
    esperanza_voice_3.update_by(
        joe_pamh_current_active_band,
        name="Esperanza - Voice 3",
        source_writer_credits="Test",
        music_uuid=esperanza_music.uuid,
    )
    assert esperanza_voice_3.music == esperanza_music
    assert pamh_band in esperanza_music.bands
    assert esperanza_voice_3.name == "Esperanza - Voice 3"
    assert esperanza_voice_3.source_writer_credits == "Test"
    other_music = bm.Music.insert(
        title="Other",
    )
    esperanza_voice_3.update_by(
        joe_pamh_current_active_band,
        name="",
        source_writer_credits="",
        music_uuid=other_music.uuid,
    )
    assert esperanza_voice_3.music == other_music
    assert pamh_band in esperanza_music.bands
    assert pamh_band in other_music.bands
    assert esperanza_voice_3.name == "Esperanza - Voice 3"
    assert esperanza_voice_3.source_writer_credits is None

    esperanza_voice_3.update_by(
        joe_pamh_current_active_band, name="", source_writer_credits="", music_uuid=""
    )
    assert esperanza_voice_3.music is None
