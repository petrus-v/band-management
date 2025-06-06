import pytest
from band_management.exceptions import ValidationError
from band_management.bloks.bm_responsive_webapp.fastapi_utils import (
    csrf_token,
    assert_valid_csrf_token,
)
from jose import JWTError
from band_management.bloks.http_auth_base.auth_api import create_access_token
from band_management.bloks.http_auth_base.schemas.auth import TokenDataSchema
from datetime import timedelta
from html import parser


class HTMLLangParser(parser.HTMLParser):
    lang = None

    def __init__(self, *args, html=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "html":
            for attr_key, attr_value in attrs:
                if attr_key == "lang":
                    self.lang = attr_value
                    return


@pytest.mark.asyncio
async def test_assert_valid_csrf_token():
    token = csrf_token(1)
    assert await assert_valid_csrf_token(token) is True


@pytest.mark.asyncio
async def test_assert_valid_csrf_token_raises_expire():
    token = csrf_token(-1)
    with pytest.raises(JWTError, match="expire"):
        await assert_valid_csrf_token(token)


@pytest.mark.asyncio
async def test_assert_valid_csrf_token_raises_invalid():
    token = create_access_token(
        TokenDataSchema(sub="something else"), expires_delta=timedelta(minutes=5)
    )
    with pytest.raises(ValidationError, match="Not a valid csrf token"):
        await assert_valid_csrf_token(token)


def test_anonymous_unknown_lang_use_english(anonymous):
    anonymous.headers["accept-language"] = "zz99"
    response = anonymous.get("/")
    assert response.status_code == 200
    assert HTMLLangParser(html=response.text).lang == "en"


def test_anonymous_fr(anonymous):
    anonymous.headers["accept-language"] = "fr"
    response = anonymous.get("/")
    assert response.status_code == 200
    assert HTMLLangParser(html=response.text).lang == "fr"
