def test_connected_musician_get_bands(connected_musician):
    response = connected_musician.get("/bands")
    assert response.status_code == 200, response.text


def test_connected_musician_search_bands(bm, connected_musician):
    response = connected_musician.post("/bands", data={"search": "PA"})
    assert response.status_code == 200, response.text


def test_connected_musician_post_band(bm, connected_musician):
    response = connected_musician.post("/band/", data={"band_name": "Band name"})
    assert response.status_code == 201, response.text

    band = bm.Band.query().filter(bm.Band.name.like("Band name")).one()
    assert band.name == "Band name"


def test_connected_musician_prepare_band(bm, connected_musician):
    response = connected_musician.get("/band/prepare")
    assert response.status_code == 200, response.text


def test_connected_musician_get_band(bm, connected_musician):
    band = bm.Band.query().filter(bm.Band.name.like("PAMH")).one()
    response = connected_musician.get(f"/band/{band.uuid}")
    assert response.status_code == 200, response.text


def test_connected_musician_update_band(bm, connected_musician):
    band = bm.Band.query().filter(bm.Band.name.like("PAMH")).one()
    response = connected_musician.put(f"/band/{band.uuid}", data={"band_name": "other"})
    assert response.status_code == 200, response.text
    band.refresh()
    assert band.name == "other"
