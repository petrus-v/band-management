from anyblok.blok import Blok
from band_management import __version__

VERSION = __version__


def import_declarations(reload=None):
    from . import report
    from . import template

    if reload is not None:
        reload(report)
        reload(template)


class BandManagementReport(Blok):
    """Report engine to generate pdf document

    We instantiate jinja engine in a different way
    than the web site to give a way to retrieve/generate
    document without current web site (which may change in a future)
    """

    version = VERSION
    author = "Pierre Verkest"
    required = [
        "anyblok-core",
    ]

    @classmethod
    def import_declaration_module(cls):
        import_declarations()

    @classmethod
    def reload_declaration_module(cls, reload):
        import_declarations(reload=reload)

    def update(self, latest):
        if not latest:
            # setup data on new version
            pass

        if latest and latest < "0.2.0":
            # do something while moving to version 0.2.0
            pass

    def update_demo(self, latest_version):
        """Called on install or update to set or update demo data"""

        if not latest_version:
            pass
