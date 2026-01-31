from justhtml import JustHTML, SanitizationPolicy

ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "u",
    "s",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "h1",
    "h2",
    "h3",
    "span",
    "div",
}

# We also need to allow some attributes for tables usually,
# but let's start with tags. Quill uses some classes.


def sanitize_html(html):
    if not html:
        return ""

    # We allow some basic attributes like class (for Quill) and style if needed
    # But for now let's just allow common ones.
    allowed_attributes = {
        "*": ["class"],
        "a": ["href", "title"],
        "table": ["border", "cellspacing", "cellpadding"],
    }

    policy = SanitizationPolicy(
        allowed_tags=ALLOWED_TAGS,
        allowed_attributes=allowed_attributes,
    )
    return JustHTML(html, fragment=True, policy=policy).to_html(pretty=False)
