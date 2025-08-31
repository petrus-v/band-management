import pytest
from uuid_extensions import uuid7
from band_management.exceptions import PermissionDenied
from sqlalchemy.exc import IntegrityError


def test_toogle_add_current_band(joe_pamh_current_active_band, pamh_band, trib_band):
    joe_pamh_current_active_band._set_active_band(trib_band)
    assert joe_pamh_current_active_band.active_band == trib_band


def test_cant_toogle_rejected_band_as_active_band(
    joe_pamh_current_active_band, trib_band
):
    joe_member_trib = joe_pamh_current_active_band.member_of(trib_band)
    joe_member_trib.reject_invitation()
    with pytest.raises(
        PermissionDenied,
        match="Permission denied. You must be part of the band to be able to active it.",
    ):
        joe_pamh_current_active_band._set_active_band(trib_band)


def test_toogle_remove_band_raise_validation_error_at_least_one_active(
    bm, joe_pamh_current_active_band, pamh_band
):
    with pytest.raises(IntegrityError, match="active_band_uuid"):
        joe_pamh_current_active_band.active_band = None
        bm.anyblok.flush()


def test_toogle_other_band_raise_permission_denied(
    joe_pamh_current_active_band, tradamuse_band
):
    with pytest.raises(
        PermissionDenied,
        match="Permission denied. You must be part of the band to be able to active it.",
    ):
        joe_pamh_current_active_band._set_active_band(tradamuse_band)


def test_insert_musician_create_band(bm):
    musician = bm.Musician.insert(name="Test", email="test@test.fr")
    assert len(musician.members) == 1
    assert musician.members[0].band == musician.active_band
    assert musician.members[0].invitation_state == "accepted"
    assert musician.members[0].is_admin is True
    assert musician.members[0].band.name == "Test Solo"


def test_insert_musician_no_band_create(bm, pamh_band):
    musician = bm.Musician.insert(
        name="Test", email="test@test.fr", active_band=pamh_band
    )
    assert len(musician.members) == 1


def test_insert_musician_with_defined_uuid(bm, pamh_band):
    musician_uuid = uuid7()
    musician = bm.Musician.insert(
        uuid=str(musician_uuid),
        name="Test",
        email="test@test.fr",
        active_band=pamh_band,
    )
    assert musician.uuid == str(musician_uuid)
