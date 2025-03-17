import datetime

from anyblok import Declarations
from anyblok.column import Text, DateTime

from jose import jwt

from band_management import config


@Declarations.register(Declarations.Model.Auth)
class User:
    """Represent a HTTP Client user (human/bot/Application...)"""

    # no needs to store it
    # remove this column once we send this by email
    invitation_token = Text(
        label="Invitation token",
        nullable=True,
    )
    invitation_token_expiration_date = DateTime(nullable=True)

    def refresh_invitation_token(self, expires_delta: datetime.timedelta | None = None):
        data = self.get_access_token_data()
        if expires_delta:
            expire = datetime.datetime.now(tz=datetime.timezone.utc) + expires_delta
        else:
            expire = datetime.datetime.now(
                tz=datetime.timezone.utc
            ) + datetime.timedelta(days=config.INVITATION_TOKEN_EXPIRE_DAYS)
        expire = expire.replace(microsecond=0)
        data.exp = int(expire.timestamp())
        encoded_jwt = jwt.encode(
            data.model_dump(mode="json"), config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        self.invitation_token_expiration_date = expire
        self.invitation_token = encoded_jwt
