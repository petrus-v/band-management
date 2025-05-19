def test_count_scores(zelda_music):
    assert zelda_music.scores_count == 2


def test_update_bands_remove_allowed(zelda_music, joe_musician, tradamuse_band):
    zelda_music.update_bands(joe_musician, [])
    assert len(zelda_music.bands) == 1
    assert zelda_music.bands == [tradamuse_band]


def test_update_bands_add_allowed(
    bm, elle_music, joe_musician, tradamuse_band, pamh_band, trib_band
):
    elle_music.update_bands(
        joe_musician,
        [str(tradamuse_band.uuid), str(pamh_band.uuid), str(trib_band.uuid)],
    )
    assert len(elle_music.bands) == 2
    assert set(elle_music.bands) == set([pamh_band, trib_band])


def test_query_any(bm, elle_music):
    query = bm.Music.query_any("elle")
    assert elle_music in query.all()


def test_is_played_by_true(bm, zelda_music, esperanza_music, pamh_band, trib_band):
    assert zelda_music.is_played_by(pamh_band) is True
    assert zelda_music.is_played_by(trib_band) is True
    assert esperanza_music.is_played_by(trib_band) is True


def test_is_played_by_false(bm, esperanza_music, pamh_band):
    assert esperanza_music.is_played_by(pamh_band) is False
