from anyblok.blok import Blok
from fastapi import FastAPI
from band_management import __version__ as VERSION


def import_declarations(reload=None):
    from . import auth

    if reload is not None:
        reload(auth)

    auth.import_declarations(reload=reload)


class HTTPAuthBase(Blok):
    """Blok to manage authentification and authorization.

    Sessions are managed by end user using JWT !

    Those should be handle security on frontal HTTP API not for
    business rules.
    """

    version = VERSION
    author = "Pierre Verkest"
    required = [
        "anyblok-core",
        "band-management-base",
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
            Auth = self.anyblok.Auth
            Auth.Scope.insert(
                code="musician-auth",
                label="Connected musician scop",
            )

        if latest and latest < "0.2.0":
            # do something while moving to version 0.2.0
            pass

    def update_demo(self, latest_version):
        """Called on install or update to set or update demo data"""
        if not latest_version:
            BM = self.anyblok.BandManagement
            Auth = self.anyblok.Auth

            pierre_musician = (
                BM.Musician.query()
                .filter(BM.Musician.email.ilike("pierre@verkest.fr"))
                .one()
            )

            scope_musician = Auth.Scope.query().get("musician-auth")
            pverkest = Auth.User.insert(musician=pierre_musician)
            pverkest.scopes.append(scope_musician)
            Auth.CredentialStore.insert(
                label="pverkest access",
                key="pverkest",
                user=pverkest,
                secret="password",  # password
            )
            joe_musician = (
                BM.Musician.query().filter(BM.Musician.email.ilike("joe@test.fr")).one()
            )
            joe = Auth.User.insert(musician=joe_musician)
            joe.scopes.append(scope_musician)
            Auth.CredentialStore.insert(
                label="joe access",
                key="joe",
                user=joe,
                secret="password",  # password
            )

        if latest_version and latest_version < "0.2.0":
            # do something while moving to version 0.2.0
            pass

    @classmethod
    def prepare_fastapi(cls, app: FastAPI) -> None:
        from . import auth_api

        app.include_router(auth_api.router_auth)
        app.include_router(auth_api.api_user)
