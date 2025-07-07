import pytest
from band_management.tools import slugify


@pytest.mark.parametrize(
    "term,expected_slug",
    [
        ("hello world!", "hello-world"),
        ("Héloïse", "heloise"),
        ("_hello_WORLD-", "hello-world"),
    ],
)
def test_slugigy(term, expected_slug):
    assert slugify(term) == expected_slug
