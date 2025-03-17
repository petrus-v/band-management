import pytest


@pytest.fixture()
def joe_pamh_current_active_band(joe_musician, pamh_band):
    # joe is member of pamh and trib not trad'amuse
    [joe_musician.active_bands.remove(b) for b in joe_musician.active_bands]
    joe_musician.active_bands.append(pamh_band)
    joe_musician.anyblok.flush()
    return joe_musician
