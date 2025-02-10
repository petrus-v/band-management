from anyblok import Declarations
from anyblok.column import String, Text


@Declarations.register(Declarations.Model.Auth)
class Scope:
    """Scope are used as the way to check if http client
    is allowed to use HTTP API endpoint
    """

    code = String(label="Name", nullable=False, primary_key=True)
    label = Text(label="Description", nullable=False)
