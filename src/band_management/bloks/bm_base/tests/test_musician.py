import pytest
from band_management.exceptions import PermissionDenied, ValidationError


def test_toogle_add_current_band(joe_pamh_current_active_band, pamh_band, trib_band):
    joe_pamh_current_active_band.toggle_musician_active_band(trib_band.uuid)
    assert joe_pamh_current_active_band.active_bands == [pamh_band, trib_band]


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
