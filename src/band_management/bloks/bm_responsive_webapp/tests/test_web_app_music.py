def test_connected_musician_get_musics(connected_musician):
    response = connected_musician.get("/musics")
    assert response.status_code == 200, response.text


def test_connected_musician_search_musics(bm, connected_musician):
    response = connected_musician.post("/musics", data={"search": "ze"})
    assert response.status_code == 200, response.text


def test_connected_musician_search_musics_dropdown(bm, connected_musician):
    response = connected_musician.post("/dropdown-musics", data={"search": "ze"})
    assert response.status_code == 200, response.text


def test_connected_musician_post_music(
    bm,
    connected_musician,
    pamh_band,
):
    response = connected_musician.post(
        "/music/",
        data={
            "music_title": "Music name",
            "music_composer": "A composer",
            "music_author": "An author",
            "music_dance": "Valse",
            "music_bands": [
                "hidden",
                str(pamh_band.uuid),
            ],
        },
    )
    assert response.status_code == 201, response.text

    music = bm.Music.query().filter(bm.Music.title.like("Music name")).one()
    assert music.title == "Music name"
    assert music.composer == "A composer"
    assert music.author == "An author"
    assert music.dance == "Valse"
    assert music.bands == [pamh_band]


def test_connected_musician_prepare_music(bm, connected_musician):
    response = connected_musician.get("/music/prepare")
    assert response.status_code == 200, response.text


def test_connected_musician_get_music(bm, connected_musician):
    music = bm.Music.query().filter(bm.Music.title.like("Zelda")).one()
    response = connected_musician.get(f"/music/{music.uuid}")
    assert response.status_code == 200, response.text


def test_connected_musician_update_music(bm, connected_musician, pamh_band):
    music = bm.Music.query().filter(bm.Music.title.like("Zelda")).one()
    response = connected_musician.put(
        f"/music/{music.uuid}",
        data={
            "music_title": "Music name",
            "music_composer": "A composer",
            "music_author": "An author",
            "music_dance": "Valse",
            "music_bands": [
                "hidden",
                str(pamh_band.uuid),
            ],
        },
    )
    assert response.status_code == 200, response.text
    music.refresh()

    assert music.title == "Music name"
    assert music.composer == "A composer"
    assert music.author == "An author"
    assert music.dance == "Valse"
    assert pamh_band in music.bands


def test_connected_musician_get_profile(connected_musician):
    response = connected_musician.get("/profile")
    assert response.status_code == 200, response.text
