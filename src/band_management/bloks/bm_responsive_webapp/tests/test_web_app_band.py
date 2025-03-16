def test_connected_musician_get_bands(connected_musician):
    response = connected_musician.get("/bands")
    assert response.status_code == 200, response.text


def test_connected_musician_search_bands(connected_musician):
    response = connected_musician.post("/bands", data={"search": "PA"})
    assert response.status_code == 200, response.text


def test_connected_musician_post_band(bm, connected_musician):
    response = connected_musician.post("/band/", data={"band_name": "Band name"})
    assert response.status_code == 201, response.text

    band = bm.Band.query().filter(bm.Band.name.like("Band name")).one()
    assert band.name == "Band name"


def test_connected_musician_prepare_band(connected_musician):
    response = connected_musician.get("/band/prepare")
    assert response.status_code == 200, response.text


def test_band_admin_musician_get_band(joe_user, connected_musician, pamh_band):
    joe_in_pahm_member = joe_user.musician.member_of(pamh_band)
    joe_in_pahm_member.is_admin = True
    joe_in_pahm_member.anyblok.flush()
    response = connected_musician.get(f"/band/{pamh_band.uuid}")
    assert response.status_code == 200, response.text


def test_non_band_admin_musician_get_band(connected_musician, pamh_band):
    response = connected_musician.get(f"/band/{pamh_band.uuid}")
    assert response.status_code == 401, response.text
    assert response.headers["hx-redirect"] == "/bands/"


def test_non_band_member_musician_get_band(joe_user, connected_musician, pamh_band):
    joe_in_pahm_member = joe_user.musician.member_of(pamh_band)
    joe_in_pahm_member.delete()
    response = connected_musician.get(f"/band/{pamh_band.uuid}")
    assert response.status_code == 401, response.text
    assert response.headers["hx-redirect"] == "/bands/"


def test_connected_admin_musician_update_band(
    pverkest_musician, joe_musician, pverkest_http_client, pamh_band
):
    joe_in_pahm = joe_musician.member_of(pamh_band)
    pverekst_in_pahm = pverkest_musician.member_of(pamh_band)
    assert [member for member in pamh_band.members if member.is_admin] == [
        pverekst_in_pahm
    ]
    response = pverkest_http_client.put(
        f"/band/{pamh_band.uuid}",
        data={
            "band_name": "other",
            "administrators": [str(pverekst_in_pahm.uuid), str(joe_in_pahm.uuid)],
        },
    )
    assert response.status_code == 200, response.text
    pamh_band.refresh()
    joe_in_pahm.refresh()
    pverekst_in_pahm.refresh()

    assert pamh_band.name == "other"

    assert [member for member in pamh_band.members if member.is_admin] == [
        pverekst_in_pahm,
        joe_in_pahm,
    ]


def test_connected_non_admin_musician_get_invite_new_member_page_permission_denied(
    joe_http_client, pamh_band
):
    response = joe_http_client.get(
        f"band/{str(pamh_band.uuid)}/invite",
    )
    assert response.status_code == 401, response.text
    assert response.headers["hx-redirect"] == "/bands/"


def test_connected_admin_musician_get_invite_new_member_page(
    pverkest_http_client, pamh_band
):
    response = pverkest_http_client.get(
        f"band/{str(pamh_band.uuid)}/invite",
    )
    assert response.status_code == 200, response.text


def test_connected_admin_musician_invite_new_member(
    doe_musician, pverkest_http_client, pamh_band
):
    response = pverkest_http_client.post(
        f"band/{str(pamh_band.uuid)}/invite",
        data={
            "musician_uuid": str(doe_musician.uuid),
        },
    )
    assert response.status_code == 200, response.text
    doe_musician.refresh()
    member = doe_musician.member_of(pamh_band)
    assert member.invitation_state == "invited"
