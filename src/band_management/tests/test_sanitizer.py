from band_management.sanitizer import sanitize_html


def test_sanitize_html_empty():
    assert sanitize_html("") == ""
    assert sanitize_html(None) == ""


def test_sanitize_html_safe():
    html = "<p>Hello <strong>world</strong></p>"
    assert sanitize_html(html) == html


def test_sanitize_html_unsafe():
    html = "<p>Hello <script>alert(1)</script></p>"
    # JustHTML strips script tags by default
    assert sanitize_html(html) == "<p>Hello </p>"


def test_sanitize_html_allowed_tags():
    html = "<h1>Title</h1><table><tr><td>Cell</td></tr></table>"
    # JustHTML adds tbody for correctness
    assert (
        sanitize_html(html)
        == "<h1>Title</h1><table><tbody><tr><td>Cell</td></tr></tbody></table>"
    )


def test_sanitize_html_disallowed_tags():
    html = "<div><span>Text</span><blink>Blink</blink></div>"
    # blink should be unwrapped or stripped. Default is unwrap.
    # JustHTML by default unwraps.
    assert "Text" in sanitize_html(html)
    assert "Blink" in sanitize_html(html)
    assert "<blink>" not in sanitize_html(html)


def test_sanitize_html_attributes():
    html = '<p class="my-class" onclick="alert(1)">Text</p>'
    sanitized = sanitize_html(html)
    assert 'class="my-class"' in sanitized
    assert "onclick" not in sanitized
