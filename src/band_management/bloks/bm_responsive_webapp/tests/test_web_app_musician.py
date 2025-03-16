def test_toggle_musician_active_band(connected_musician, joe_user, pamh_band):
    response = connected_musician.put(
        f"/musician/{joe_user.musician_uuid}/toggle-active-band/{pamh_band.uuid}"
    )
    assert response.status_code == 201, response.text
    assert response.headers["HX-Refresh"] == "true"


def test_toggle_musician_active_band_permission_denied(
    connected_musician, doe_musician, pamh_band
):
    response = connected_musician.put(
        f"/musician/{doe_musician.uuid}/toggle-active-band/{pamh_band.uuid}"
    )
    assert response.status_code == 401, response.text


def test_connected_musician_search_musicians_dropdown_name_search(connected_musician):
    response = connected_musician.post("/musicians/dropdown", data={"search": "do"})
    assert response.status_code == 200, response.text


def test_connected_musician_search_musicians_dropdown_name_search_band(
    connected_musician, pamh_band
):
    response = connected_musician.post(
        "/musicians/dropdown", data={"search": "do", "band_uuid": str(pamh_band.uuid)}
    )
    assert response.status_code == 200, response.text


def test_connected_musician_search_musicians_dropdown_band_filter(
    connected_musician, pamh_band
):
    response = connected_musician.post(
        "/musicians/dropdown", data={"search": "", "band_uuid": str(pamh_band.uuid)}
    )
    assert response.status_code == 200, response.text


def test_prepare_musician(connected_musician):
    response = connected_musician.get(
        "/musician/prepare", params={"musician_name": "test"}
    )
    assert response.status_code == 200, response.text


def test_prepare_musician_with_band_uuid(connected_musician, pamh_band):
    response = connected_musician.get(
        "/musician/prepare",
        params={"musician_name": "test", "band_uuid": str(pamh_band.uuid)},
    )
    assert response.status_code == 200, response.text


def test_add_musician(bm, connected_musician):
    response = connected_musician.post(
        "/musician",
        data={
            "musician_name": "abc",
            "musician_email": "abc@band.name",
        },
    )
    assert response.status_code == 200
    musician = bm.Musician.query().filter_by(name="abc").one()
    assert musician.email == "abc@band.name"
    assert musician.lang == "en"
