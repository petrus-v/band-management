import datetime
from band_management.bloks.bm_responsive_webapp.jinja import NextAction
from band_management.bloks.bm_responsive_webapp.fastapi_utils import csrf_token


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


def test_add_musician_modal_mode(bm, connected_musician):
    response = connected_musician.post(
        "/musician",
        data={
            "musician_name": "abc",
            "musician_email": "abc@band.name",
            "next_action": NextAction.UPDATE_FIELD_SELECTION,
            "csrf_token": csrf_token(5),
        },
    )
    assert response.status_code == 200
    musician = bm.Musician.query().filter_by(name="abc").one()
    assert musician.email == "abc@band.name"
    assert musician.lang == "en"
    assert (
        musician.user.invitation_token_expiration_date
        - datetime.datetime.now(tz=datetime.timezone.utc)
    ) < datetime.timedelta(days=5, hours=1)

    assert (
        musician.user.invitation_token_expiration_date
        - datetime.datetime.now(tz=datetime.timezone.utc)
    ) > datetime.timedelta(days=5, hours=-1)


def test_add_musician(bm, connected_musician):
    response = connected_musician.post(
        "/musician",
        data={
            "musician_name": "abc",
            "musician_email": "abc@band.name",
            "next_action": NextAction.EDIT_FORM_VIEW,
            "csrf_token": csrf_token(5),
        },
    )
    assert response.status_code == 200
    musician = bm.Musician.query().filter_by(name="abc").one()
    assert musician.email == "abc@band.name"
    assert musician.lang == "en"
    assert (
        musician.user.invitation_token_expiration_date
        - datetime.datetime.now(tz=datetime.timezone.utc)
    ) < datetime.timedelta(minutes=10, seconds=10)

    assert (
        musician.user.invitation_token_expiration_date
        - datetime.datetime.now(tz=datetime.timezone.utc)
    ) > datetime.timedelta(minutes=10, seconds=-10)


def test_update_musician(bm, joe_user, connected_musician):
    response = connected_musician.put(
        f"/musician/{joe_user.musician_uuid}",
        data={
            "musician_name": "abc",
            "musician_email": "abc@band.name",
            "musician_lang": "fr",
            "csrf_token": csrf_token(5),
        },
    )
    assert response.status_code == 200
    bm.anyblok.flush()
    joe_user.musician.refresh()
    musician = bm.Musician.query().filter_by(name="abc").one()
    assert musician == joe_user.musician
    # do not allow change email this way for security reason
    # should send an email to the old and new address email.
    assert musician.email == "joe@test.fr"
    assert musician.lang == "fr"


def test_update_musician_unknown_lang_use_default(bm, joe_user, connected_musician):
    response = connected_musician.put(
        f"/musician/{joe_user.musician_uuid}",
        data={
            "musician_name": "abc",
            "musician_email": "abc@band.name",
            "musician_lang": "zz",
            "csrf_token": csrf_token(5),
        },
    )
    assert response.status_code == 200
    bm.anyblok.flush()
    joe_user.musician.refresh()
    assert joe_user.musician.lang == "en"


def test_update_other_musician_profile(bm, doe_musician, connected_musician):
    response = connected_musician.put(
        f"/musician/{doe_musician.uuid}",
        data={
            "musician_name": "abc",
            "musician_email": "abc@band.name",
            "musician_lang": "fr",
            "csrf_token": csrf_token(5),
        },
    )
    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Your are not allowed to update other musician profiles"
    )
