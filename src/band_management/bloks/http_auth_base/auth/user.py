from band_management.bloks.http_auth_base.schemas.auth import TokenDataSchema
from anyblok import Declarations
from anyblok.relationship import Many2Many, One2One


@Declarations.register(Declarations.Model.Auth)
class User(Declarations.Mixin.PrimaryColumn):
    """Represent a HTTP Client user (human/bot/Application...)"""

    musician = One2One(
        model=Declarations.Model.BandManagement.Musician,
        nullable=False,
        unique=True,
        backref="user",
    )
    scopes = Many2Many(
        model=Declarations.Model.Auth.Scope,
        join_table="http_client_scope_rel",
        local_columns="uuid",
        m2m_local_columns="client_uuid",
        m2m_remote_columns="scope_code",
        remote_columns="code",
        many2many="users",
    )

    def get_access_token_data(self) -> TokenDataSchema:
        """This generate access token data in
        JWT token. Do not add sensitive data inside.

        Extra data you may add are considered true for the
        life time of the token without a way to invalidate it.
        """
        return TokenDataSchema(
            **{
                "sub": self.uuid,
                "scopes": [scope.code for scope in self.scopes],
            }
        )
