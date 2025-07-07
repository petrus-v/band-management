import re
from unicodedata import normalize


def slugify(name):
    """inspired from django.utils.text.slugify"""
    normalized = normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^\w\s-]", "", normalized.lower())
    return re.sub(r"[-\s]+", "-", normalized).strip("-_").replace("_", "-")
