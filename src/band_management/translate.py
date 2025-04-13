import gettext
from band_management import config
from pathlib import Path

I18N_DIRECTORY = Path(__file__).parent / "i18n"

if not I18N_DIRECTORY.exists():  # pragma: no cover
    raise RuntimeError("Missing translation directory")


def get_translations(lang):
    return gettext.translation(
        "messages", localedir=I18N_DIRECTORY, languages=[lang], fallback=True
    ).gettext


def translate_string(string: str, lang: str = config.DEFAULT_LANG):
    return get_translations(lang)(string)


_t = translate_string
