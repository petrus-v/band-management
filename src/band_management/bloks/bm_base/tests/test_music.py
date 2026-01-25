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


def test_query_any(bm, elle_music, pamh_band, trib_band):
    # 1. basic search
    query = bm.Music.query_any("elle")
    assert elle_music in query.all()

    # 2. search with band filter
    # zelda is in pamh_band, elle is NOT in pamh_band (usually)
    # let's make sure
    if pamh_band in elle_music.bands:
        elle_music.bands.remove(pamh_band)

    query = bm.Music.query_any("elle", band=pamh_band)
    assert elle_music not in query.all()

    # 3. search with band_exclude filter
    query = bm.Music.query_any("elle", band_exclude=pamh_band)
    assert elle_music in query.all()


def test_is_played_by_true(bm, zelda_music, esperanza_music, pamh_band, trib_band):
    assert zelda_music.is_played_by(pamh_band) is True
    assert zelda_music.is_played_by(trib_band) is True
    assert esperanza_music.is_played_by(trib_band) is True


def test_is_played_by_false(bm, esperanza_music, pamh_band):
    assert esperanza_music.is_played_by(pamh_band) is False


def test_ensure_musician_active_band_already_present(
    zelda_music, joe_musician, tradamuse_band
):
    assert tradamuse_band in zelda_music.bands
    joe_musician.active_band = tradamuse_band
    zelda_music.ensure_musician_active_band(joe_musician)
    assert tradamuse_band in zelda_music.bands


def test_ensure_musician_active_band_not_present(elle_music, joe_musician, pamh_band):
    # joe is member of pamh
    joe_musician.active_band = pamh_band
    if pamh_band in elle_music.bands:
        elle_music.bands.remove(pamh_band)

    assert pamh_band not in elle_music.bands
    elle_music.ensure_musician_active_band(joe_musician)
    assert pamh_band in elle_music.bands
