def test_add_band(bm, joe_pamh_current_active_band, pamh_band):
    band = bm.Band.insert_by(joe_pamh_current_active_band, name="My new band")
    assert len(band.members) == 1
    assert band.members[0].musician == joe_pamh_current_active_band
    assert band.members[0].is_admin is True
    assert band in joe_pamh_current_active_band.active_bands
    assert pamh_band in joe_pamh_current_active_band.active_bands
