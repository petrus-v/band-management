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
            "You must have an accepted invitation with admin "
            "access to this band PAMH before invite new musicians."
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
    pv_in_pamh.invitation_state = "accepted"
    pv_in_pamh.is_admin = False
    with pytest.raises(
        PermissionDenied,
        match=(
            "You must have an accepted invitation with admin "
            "access to this band PAMH before invite new musicians."
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
    assert pamh_band == pverkest_musician.active_band
    pv_in_pamh = pverkest_musician.member_of(pamh_band)
    pv_in_pamh.reject_invitation()
    assert pamh_band != pverkest_musician.active_band


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


def test_reject_lastest_active_band(bm, doe_musician, trib_band, tradamuse_band):
    doe_in_trib = doe_musician.member_of(trib_band)
    doe_in_tradamuse = doe_musician.member_of(tradamuse_band)
    doe_in_tradamuse.reject_invitation()
    # bm.anyblok.flush()
    # doe_musician.refresh()
    with pytest.raises(
        ValueError,
        match="You must be part of at least one band, create an other one if you want to leave the current one",
    ):
        doe_in_trib.reject_invitation()
