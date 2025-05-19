from anyblok import Declarations
from weasyprint import HTML, default_url_fetcher
from typing import ByteString

register = Declarations.register
Model = Declarations.Model


@register(Model)
class Report:
    """Namespace for reporting engine"""

    @classmethod
    def _print(cls, template: "Report.JinjaTemplate", data: dict = None) -> ByteString:
        html = template.render(data)

        def my_fetcher(url):
            if url.startswith("bm:url:"):
                return default_url_fetcher(f"file://{template.get_url_local_path(url)}")
            return default_url_fetcher(url)

        return HTML(
            string=html,
            url_fetcher=my_fetcher,
        ).write_pdf()  # presentational_hints=True

    @classmethod
    def print(cls, template_code: str, data: dict = None) -> ByteString:
        template = cls.anyblok.Report.JinjaTemplate.query().get(template_code)
        return cls._print(template, data)
