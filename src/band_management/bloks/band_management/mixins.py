from uuid_extensions import uuid7

from anyblok import Declarations
from anyblok.column import UUID


Mixin = Declarations.Mixin


@Declarations.register(Mixin)
class PrimaryColumn:
    """`UUID` id primary key mixin"""

    uuid: uuid7 = UUID(primary_key=True, default=uuid7, binary=False)
