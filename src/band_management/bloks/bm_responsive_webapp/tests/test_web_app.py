def test_anonymous_band_management_brand_page(anonymous):
    response = anonymous.get("/")
    assert response.status_code == 200, response.text


def test_anonymous_band_management_login_page(anonymous):
    response = anonymous.get("/login")
    assert response.status_code == 200, response.text


def test_band_leader_home(band_leader):
    response = band_leader.get("/home")
    assert response.status_code == 200, response.text


def test_band_leader_get_bands(band_leader):
    response = band_leader.get("/bands")
    assert response.status_code == 200, response.text


def test_band_leader_search_bands(bm, band_leader):
    response = band_leader.post("/bands", data={"search": "PA"})
    assert response.status_code == 200, response.text


def test_band_leader_post_band(bm, band_leader):
    response = band_leader.post("/band/", data={"band_name": "Band name"})
    assert response.status_code == 200, response.text

    band = bm.Band.query().filter(bm.Band.name.like("Band name")).one()
    assert band.name == "Band name"


def test_band_leader_prepare_band(bm, band_leader):
    response = band_leader.get("/band/prepare")
    assert response.status_code == 200, response.text


def test_band_leader_get_band(bm, band_leader):
    band = bm.Band.query().filter(bm.Band.name.like("PAMH")).one()
    response = band_leader.get(f"/band/{band.uuid}")
    assert response.status_code == 200, response.text


def test_band_leader_update_band(bm, band_leader):
    band = bm.Band.query().filter(bm.Band.name.like("PAMH")).one()
    response = band_leader.put(f"/band/{band.uuid}", data={"band_name": "other"})
    assert response.status_code == 200, response.text
    band.refresh()
    assert band.name == "other"


def test_band_leader_get_musics(band_leader):
    response = band_leader.get("/musics")
    assert response.status_code == 200, response.text


def test_band_leader_get_profile(band_leader):
    response = band_leader.get("/profile")
    assert response.status_code == 200, response.text
