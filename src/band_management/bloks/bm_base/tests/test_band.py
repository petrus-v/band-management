import pytest
from uuid_extensions import uuid7
from band_management.exceptions import ValidationError, PermissionDenied
from sqlalchemy.exc import IntegrityError


def test_add_band(bm, joe_pamh_current_active_band, pamh_band):
    band = bm.Band.insert_by(joe_pamh_current_active_band, name="My new band")
    assert len(band.members) == 1
    assert band.members[0].musician == joe_pamh_current_active_band
    assert band.members[0].is_admin is True
    assert band in joe_pamh_current_active_band.active_bands
    assert pamh_band in joe_pamh_current_active_band.active_bands


def test_non_admin_update_by(joe_musician, pamh_band):
    with pytest.raises(PermissionDenied, match="not allowed to edit this band"):
        pamh_band.update_by(joe_musician, name="test")


def test_admin_update_by(joe_musician, pamh_band):
    member = joe_musician.member_of(pamh_band)
    member.is_admin = True
    member.anyblok.flush()
    pamh_band.update_by(joe_musician, name="test")
    assert pamh_band.name == "test"


def test_non_admin_update_administrator_by(joe_musician, pamh_band):
    member = joe_musician.member_of(pamh_band)
    with pytest.raises(
        PermissionDenied, match="not allowed to edit administrators's band"
    ):
        pamh_band.update_administrator_by(joe_musician, [member.uuid])


def test_admin_update_administrator_by_with_no_admin(joe_musician, pamh_band):
    member = joe_musician.member_of(pamh_band)
    member.is_admin = True
    with pytest.raises(
        ValidationError, match="You should set at least one administrator"
    ):
        pamh_band.update_administrator_by(joe_musician, [])


def test_admin_update_administrator_by_with_no_member_uuid_admin(
    joe_musician, pamh_band
):
    member = joe_musician.member_of(pamh_band)
    member.is_admin = True
    with pytest.raises(
        ValidationError, match="You should set at least one administrator"
    ):
        pamh_band.update_administrator_by(joe_musician, [uuid7()])


def test_admin_update_administrator_by(joe_musician, pamh_band):
    member = joe_musician.member_of(pamh_band)
    member.is_admin = True
    assert len([member for member in pamh_band.members if member.is_admin]) == 2
    pamh_band.update_administrator_by(joe_musician, [str(member.uuid)])
    assert [member for member in pamh_band.members if member.is_admin] == [member]


def test_add_member_by(joe_musician, doe_musician, pamh_band):
    member = joe_musician.member_of(pamh_band)
    member.is_admin = True
    member = pamh_band.add_member_by(joe_musician, doe_musician)
    assert not member.is_admin
    pamh_band.refresh()
    assert doe_musician in [member.musician for member in pamh_band.members]
    assert len(pamh_band.members) == 3


def test_add_member_by_is_admin(joe_musician, doe_musician, pamh_band):
    member = joe_musician.member_of(pamh_band)
    member.is_admin = True
    member = doe_musician.member_of(pamh_band)
    assert member is None
    member = pamh_band.add_member_by(joe_musician, doe_musician, is_admin=True)
    assert member.is_admin
    assert member.musician == doe_musician


def test_non_admin_add_member_by(joe_musician, doe_musician, pamh_band):
    member = doe_musician.member_of(pamh_band)
    assert member is None
    with pytest.raises(
        PermissionDenied, match="not allowed to invite new musician to this band"
    ):
        pamh_band.add_member_by(joe_musician, doe_musician)


def test_add_existing_member_add_member_by(joe_musician, pamh_band):
    member = joe_musician.member_of(pamh_band)
    member.is_admin = True
    with pytest.raises(IntegrityError, match="unique_musician_per_band"):
        pamh_band.add_member_by(joe_musician, joe_musician)
