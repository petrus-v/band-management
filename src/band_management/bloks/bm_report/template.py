from anyblok import Declarations
import jinja2
from jinja2.sandbox import SandboxedEnvironment as Environment
from pathlib import Path
from anyblok.column import String, Text
from band_management import config
from band_management import get_translations
from datetime import datetime
from babel.dates import format_datetime, format_date
from functools import partial

register = Declarations.register
Model = Declarations.Model


@register(Model.Report)
class JinjaTemplate:
    code: str = String(label="Template code", primary_key=True)
    directories: str = Text(
        label="list of directories to look for separated by new line character (`\n`)."
    )
    template: str = String(label="Relative path to the template to use")

    @classmethod
    def common_rendering_directories(cls):
        return [
            (Path(__file__).parent / "templates").absolute(),
        ]

    def render(self, data: dict = None) -> str:
        """Rendering template using jinja"""
        if not data:
            data = {}

        lang = data.get("lang")

        if lang not in config.AVAILABLE_LANGS:
            lang = config.DEFAULT_LANG

        jinja_env = self._jinja_env(lang=lang)
        translate = get_translations(lang)

        data.update(
            {
                "lang": lang,
                "gettext": translate,  # support for {% trans %} using jinja2.ext.i18n
                "_t": translate,  # support for {{ _t() }} in templates
                "print_date": datetime.now(),
            }
        )
        template = jinja_env.get_template(self.template)
        return template.render(**data)

    def get_url_local_path(self, url):
        """Transform 'url_for:logo.png' to absolute path"""
        filename = url[7:]
        for directory in self.assets_directories:
            absolute_path = Path(directory) / filename
            if absolute_path.exists():
                return str(absolute_path)

    @property
    def assets_directories(self):
        return [*self.directories.split("\n"), *self.common_rendering_directories()]

    def _jinja_env(self, lang: str = "en") -> jinja2.Environment:
        # this should be cache-able at record level somehow
        loader = jinja2.FileSystemLoader(self.assets_directories)

        env = Environment(
            loader=loader,
            autoescape=True,
        )
        self._setup_env_defaults(env, lang=lang)
        return env

    def _setup_env_defaults(self, env: jinja2.Environment, lang: str = "en") -> None:
        """provide a way to configure default globals and extensions"""
        env.add_extension("jinja2.ext.i18n")
        env.filters["format_datetime"] = partial(format_datetime, locale=lang)
        env.filters["format_date"] = partial(format_date, locale=lang)
