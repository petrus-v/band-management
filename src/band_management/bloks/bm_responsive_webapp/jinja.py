import re
from pathlib import Path
from fastapi.templating import Jinja2Templates
from enum import StrEnum
from band_management.bloks.bm_responsive_webapp.fastapi_utils import csrf_token

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


class NextAction(StrEnum):
    UPDATE_FIELD_SELECTION = "UPDATE_FIELD_SELECTION"
    BACK_TO_LIST = "BACK_TO_LIST"
    EDIT_FORM_VIEW = "EDIT_FORM_VIEW"
    EDIT_MODAL_FROM_VIEW = "EDIT_MODAL_FROM_VIEW"


def highlight_match(text: str, search: str) -> str:
    if not search:
        return text

    def replace_case_sensitive(match):
        return f'<strong class="has-text-danger">{match.group(0)}</strong>'

    pattern = re.escape(search)
    return re.sub(pattern, replace_case_sensitive, text, flags=re.IGNORECASE)


templates.env.filters["highlight"] = highlight_match
templates.env.globals["NextAction"] = NextAction
templates.env.globals["csrf_token"] = csrf_token
