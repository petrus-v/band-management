from anyblok import Declarations
from anyblok.column import Password, String
from anyblok.relationship import Many2One


@Declarations.register(Declarations.Model.Auth)
class CredentialStore:
    """Simple login / password table

    called key / secret because we don't know if
    user is an application or a human.
    """

    key = String(
        primary_key=True,
        nullable=False,
    )
    secret = Password(
        nullable=False,
        crypt_context={
            "schemes": ["bcrypt"],
        },
    )
    user = Many2One(model=Declarations.Model.Auth.User)
    label = String(label="Usage info", nullable=True)
