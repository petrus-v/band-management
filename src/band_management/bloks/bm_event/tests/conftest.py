import pytest


@pytest.fixture()
def event(bm):
    return bm.Event.query().filter_by(name="A great event").one()
