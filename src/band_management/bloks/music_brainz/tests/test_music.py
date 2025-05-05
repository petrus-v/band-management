from uuid import uuid4


def test_query_any(bm):
    musicbrainz_artists = str(uuid4())
    bm.Music.insert(
        title="Musicbrainz test",
        musicbrainz_title="Musicbrainz test",
        musicbrainz_artists=musicbrainz_artists,
        musicbrainz_uuid=uuid4(),
    )
    query = bm.Music.query_any(musicbrainz_artists)
    assert len(query.all()) == 1


def test_query_any_ensure_or(bm):
    musicbrainz_artists = str(uuid4())
    bm.Music.insert(
        title="Musicbrainz test",
        musicbrainz_title="Musicbrainz test",
        musicbrainz_artists=musicbrainz_artists,
        musicbrainz_uuid=uuid4(),
    )
    bm.Music.insert(
        title=musicbrainz_artists[:10],
    )
    query = bm.Music.query_any(musicbrainz_artists[:10])
    assert len(query.all()) == 2
