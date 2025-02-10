from anyblok import Declarations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anyblok.registy import Registry as Anyblok


def import_declarations(reload=None):
    from . import scope
    from . import user
    from . import credential_store

    if reload is not None:
        reload(scope)
        reload(user)
        reload(credential_store)


@Declarations.register(Declarations.Model)
class Auth:
    """Namespace class to manage Authorization and
    authentification models."""

    @classmethod
    def authenticate(cls, key, secret) -> "Anyblok.Auth.User":
        Credential = cls.anyblok.Auth.CredentialStore
        credential = Credential.query().filter(Credential.key == key).one_or_none()
        if credential:
            if credential.secret == secret:
                return credential.user
        return None
