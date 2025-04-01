import pytest
from band_management.exceptions import PermissionDenied, ValidationError


def test_toogle_add_current_band(joe_pamh_current_active_band, pamh_band, trib_band):
    joe_pamh_current_active_band.toggle_musician_active_band(trib_band.uuid)
    assert joe_pamh_current_active_band.active_bands == [pamh_band, trib_band]


def test_cant_toogle_rejected_band_as_active_band(
    joe_pamh_current_active_band, trib_band
):
    joe_member_trib = joe_pamh_current_active_band.member_of(trib_band)
    joe_member_trib.reject_invitation()
    with pytest.raises(
        ValidationError,
        match=(
            f"You, {joe_pamh_current_active_band.name}, should accept the invitation "
            f"before activate this band: {trib_band.name}\."
        ),
    ):
        joe_pamh_current_active_band.toggle_musician_active_band(trib_band.uuid)


def test_toogle_remove_band(joe_pamh_current_active_band, pamh_band, trib_band):
    joe_pamh_current_active_band.toggle_musician_active_band(trib_band.uuid)
    joe_pamh_current_active_band.toggle_musician_active_band(pamh_band.uuid)
    assert joe_pamh_current_active_band.active_bands == [trib_band]


def test_toogle_remove_band_raise_validation_error_at_least_one_active(
    joe_pamh_current_active_band, pamh_band
):
    with pytest.raises(ValidationError, match="require at least one active band."):
        joe_pamh_current_active_band.toggle_musician_active_band(pamh_band.uuid)


def test_toogle_other_band_raise_permission_denied(
    joe_pamh_current_active_band, tradamuse_band
):
    with pytest.raises(
        PermissionDenied,
        match="Permission denied. You must be part of the band to be able to active it.",
    ):
        joe_pamh_current_active_band.toggle_musician_active_band(tradamuse_band.uuid)


def test_insert_musician_create_band(bm):
    musician = bm.Musician.insert(name="Test", email="test@test.fr")
    assert len(musician.members) == 1
    assert musician.members.band == musician.active_bands
    assert musician.members[0].invitation_state == "accepted"
    assert musician.members[0].is_admin is True
    assert musician.members[0].band.name == "Test Solo"


def test_insert_musician_no_band_create(bm):
    musician = bm.Musician.insert(
        name="Test", email="test@test.fr", create_solo_band=False
    )
    assert len(musician.members) == 0
