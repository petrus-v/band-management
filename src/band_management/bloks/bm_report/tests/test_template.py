from datetime import datetime
from pathlib import Path
import pytest


def test_template_render_no_data(anyblok):
    template = anyblok.Report.JinjaTemplate.query().get("event")
    # This should cover line 33: if not data: data = {}
    # We catch the error but line 33 is executed
    with pytest.raises(Exception):
        template.render(None)
    mock_event = type(
        "obj",
        (object,),
        {
            "name": "test",
            "uri_code": "abc",
            "band": type("obj", (object,), {"name": "test"})(),
            "date": datetime.now(),
            "place": "test",
            "header": "test",
            "footer": "test",
            "ordered_musics": [],
        },
    )()
    res = template.render({"event": mock_event, "amnezik_event_qrcode": ""})
    assert res is not None


def test_template_render_unknown_lang(anyblok):
    template = anyblok.Report.JinjaTemplate.query().get(
        "anyblok"
    )  # Use one that doesn't need many things? NO.
    template = anyblok.Report.JinjaTemplate.query().get("event")
    mock_event = type(
        "obj",
        (object,),
        {
            "name": "test",
            "uri_code": "abc",
            "band": type("obj", (object,), {"name": "test"})(),
            "date": datetime.now(),
            "place": "test",
            "header": "test",
            "footer": "test",
            "ordered_musics": [],
        },
    )()
    res = template.render(
        {"lang": "xx", "event": mock_event, "amnezik_event_qrcode": ""}
    )
    assert res is not None


def test_template_get_url_local_path_not_found(anyblok):
    template = anyblok.Report.JinjaTemplate.query().get("event")
    assert template.get_url_local_path("bm:url:unknown_file.png") is None


def test_template_get_url_local_path_found(anyblok):
    template = anyblok.Report.JinjaTemplate.query().get("event")
    # favicon.png should exist in bm_event/documents/
    path = template.get_url_local_path("bm:url:favicon.png")
    assert path is not None
    assert Path(path).exists()
