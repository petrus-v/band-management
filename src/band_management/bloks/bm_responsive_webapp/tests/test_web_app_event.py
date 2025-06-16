from datetime import datetime
from band_management.bloks.bm_responsive_webapp.jinja import NextAction


def test_connected_musician_get_events(connected_musician):
    response = connected_musician.get("/events")
    assert response.status_code == 200, response.text


def test_connected_musician_search_events(bm, connected_musician):
    response = connected_musician.post("/events", data={"search": ""})
    assert response.status_code == 200, response.text


def test_connected_musician_post_event(
    bm,
    connected_musician,
    pamh_band,
):
    response = connected_musician.post(
        "/event/",
        data={
            "name": "Lovely event",
            "event_date": "2021-06-15 12:11:10",
            "band_uuid": str(pamh_band.uuid),
            "place": "Somewhere",
            "comment": "Bring microphone",
            "header": "Event information",
            "footer": "Artists: Pierre, Audrey",
        },
    )
    assert response.status_code == 201, response.text

    event = bm.Event.query().filter(bm.Event.name.like("Lovely event")).one()
    assert event.name == "Lovely event"
    assert event.date == datetime(2021, 6, 15, 12, 11, 10, tzinfo=event.date.tzinfo)
    assert event.band == pamh_band
    assert event.place == "Somewhere"
    assert event.comment == "Bring microphone"
    assert event.header == "Event information"
    assert event.footer == "Artists: Pierre, Audrey"


def test_connected_musician_prepare_event(bm, connected_musician):
    response = connected_musician.get("/event/prepare")
    assert response.status_code == 200, response.text


def test_connected_musician_prepare_music_modal_mode(bm, connected_musician):
    response = connected_musician.get(
        f"/event/prepare?next_action={NextAction.EDIT_MODAL_FROM_VIEW}&name=test"
    )
    assert response.status_code == 200, response.text


def test_connected_musician_get_event(bm, connected_musician):
    event = bm.Event.query().filter(bm.Event.name.ilike("A great event")).one()
    response = connected_musician.get(f"/event/{event.uuid}")
    assert response.status_code == 200, response.text


def test_connected_musician_get_event_with_uri_code(
    bm,
    connected_musician,
):
    event = bm.Event.query().filter(bm.Event.name.ilike("A great event")).one()
    response = connected_musician.get(f"/event/{event.uri_code}")
    assert response.status_code == 200, response.text


def test_connected_musician_update_event(bm, connected_musician, pamh_band):
    event = bm.Event.query().filter(bm.Event.name.like("A great event")).one()
    response = connected_musician.put(
        f"/event/{event.uuid}",
        data={
            "name": "Lovely event",
            "event_date": "2021-06-15T12:11",
            "band_uuid": str(pamh_band.uuid),
            "place": "Somewhere",
            "comment": "Bring microphone",
            "header": "Event information",
            "footer": "Artists: Pierre, Audrey",
        },
    )
    assert response.status_code == 200, response.text
    event.refresh()

    assert event.name == "Lovely event"
    assert event.date == datetime(2021, 6, 15, 12, 11, 0, tzinfo=event.date.tzinfo)
    assert event.band == pamh_band
    assert event.place == "Somewhere"
    assert event.comment == "Bring microphone"
    assert event.header == "Event information"
    assert event.footer == "Artists: Pierre, Audrey"


def test_connected_musician_get_event_print_with_uri_code(
    bm,
    connected_musician,
):
    event = bm.Event.query().filter(bm.Event.name.ilike("A great event")).one()
    response = connected_musician.get(f"/event/{event.uri_code}/print")
    assert response.status_code == 200, response.text


def test_connected_musician_get_event_print_with_uuid(
    bm,
    connected_musician,
):
    event = bm.Event.query().filter(bm.Event.name.ilike("A great event")).one()
    response = connected_musician.get(f"/event/{event.uuid}/print")
    assert response.status_code == 200, response.text
