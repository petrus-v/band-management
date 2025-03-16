def test_accept_member_invitation(joe_musician, joe_http_client, pamh_band):
    member = joe_musician.member_of(pamh_band)
    response = joe_http_client.put(f"/member/{member.uuid}/accept")
    assert response.status_code == 201, response.text
    member.refresh()
    assert member.invitation_state == "accepted"


def test_reject_member_invitation(joe_musician, joe_http_client, pamh_band):
    member = joe_musician.member_of(pamh_band)
    response = joe_http_client.put(f"/member/{member.uuid}/reject")
    assert response.status_code == 201, response.text
    member.refresh()
    assert member.invitation_state == "rejected"


def test_accept_member_mismatched(joe_musician, pverkest_http_client, pamh_band):
    member = joe_musician.member_of(pamh_band)
    response = pverkest_http_client.put(f"/member/{member.uuid}/accept")
    assert response.status_code == 401


def test_reject_member_mismatched(joe_musician, pverkest_http_client, pamh_band):
    member = joe_musician.member_of(pamh_band)
    response = pverkest_http_client.put(f"/member/{member.uuid}/reject")
    assert response.status_code == 401
