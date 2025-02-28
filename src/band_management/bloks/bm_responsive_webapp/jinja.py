import re
from pathlib import Path
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def highlight_match(text: str, search: str) -> str:
    if not search:
        return text

    def replace_case_sensitive(match):
        return f'<strong class="has-text-danger">{match.group(0)}</strong>'

    pattern = re.escape(search)
    return re.sub(pattern, replace_case_sensitive, text, flags=re.IGNORECASE)


templates.env.filters["highlight"] = highlight_match
