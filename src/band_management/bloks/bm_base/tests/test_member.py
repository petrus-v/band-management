import pytest
from band_management.exceptions import PermissionDenied


def test_reject_invitation(joe_pamh_current_active_band, trib_band):
    joe_member_trib = joe_pamh_current_active_band.member_of(trib_band)
    assert joe_member_trib.invitation_state == "invited"
    joe_member_trib.reject_invitation()
    assert joe_member_trib.invitation_state == "rejected"


def test_accept_invitation(joe_pamh_current_active_band, trib_band):
    joe_member_trib = joe_pamh_current_active_band.member_of(trib_band)
    assert joe_member_trib.invitation_state == "invited"
    joe_member_trib.accept_invitation()
    assert joe_member_trib.invitation_state == "accepted"


def test_create_invitation_by(bm, pverkest_musician, doe_musician, pamh_band):
    joe_in_pahm_member = bm.Member.create_invitation_by(
        pamh_band,
        doe_musician,
        invited_by=pverkest_musician,
    )
    assert joe_in_pahm_member.invitation_state == "invited"
    assert joe_in_pahm_member.musician == doe_musician
    assert joe_in_pahm_member.band == pamh_band


def test_create_invitation_by_permission_denied_invited_member(
    bm, pverkest_musician, doe_musician, pamh_band
):
    pv_in_pamh = pverkest_musician.member_of(pamh_band)
    pv_in_pamh.invitation_state = "invited"
    with pytest.raises(
        PermissionDenied,
        match=(
            "You must have an acepted admin access to this band "
            "PAMH before invite new musicians."
        ),
    ):
        bm.Member.create_invitation_by(
            pamh_band,
            doe_musician,
            invited_by=pverkest_musician,
        )


def test_create_invitation_by_permission_denied_non_admin_member(
    bm, pverkest_musician, doe_musician, pamh_band
):
    pv_in_pamh = pverkest_musician.member_of(pamh_band)
    pv_in_pamh.is_admin = False
    with pytest.raises(
        PermissionDenied,
        match=(
            "You must have an acepted admin access to this band "
            "PAMH before invite new musicians."
        ),
    ):
        bm.Member.create_invitation_by(
            pamh_band,
            doe_musician,
            invited_by=pverkest_musician,
        )


def test_create_invitation(bm, doe_musician, pamh_band):
    joe_in_pahm_member = bm.Member.create_invitation_by(
        pamh_band,
        doe_musician,
    )
    assert joe_in_pahm_member.invitation_state == "invited"
    assert joe_in_pahm_member.musician == doe_musician
    assert joe_in_pahm_member.band == pamh_band


def test_reject_invitation_remove_active_band(bm, pverkest_musician, pamh_band):
    assert pamh_band in pverkest_musician.active_bands
    pv_in_pamh = pverkest_musician.member_of(pamh_band)
    pv_in_pamh.reject_invitation()
    assert pamh_band not in pverkest_musician.active_bands


def test_members_relationship_ingore_reject(pverkest_musician, pamh_band, trib_band):
    assert pverkest_musician.members.band == [pamh_band, trib_band]
    pv_in_pamh = pverkest_musician.member_of(pamh_band)
    pv_in_pamh.reject_invitation()
    pverkest_musician.refresh()
    assert pverkest_musician.members.band == [trib_band]


def test_rejected_invitations_relationship(pverkest_musician, pamh_band, trib_band):
    pv_in_pamh = pverkest_musician.member_of(pamh_band)
    pv_in_pamh.reject_invitation()
    assert pverkest_musician.rejected_invitations.band == [pamh_band]
