from anyblok import Declarations
import datetime
from band_management import config

register = Declarations.register
Mixin = Declarations.Mixin
Model = Declarations.Model


@register(Model.BandManagement)
class Musician:
    @classmethod
    def insert(cls, *args, invitation_token_delta: datetime.timedelta = None, **kwargs):
        if not invitation_token_delta:
            invitation_token_delta = datetime.timedelta(
                days=config.INVITATION_TOKEN_EXPIRE_DAYS
            )
        musician = super().insert(*args, **kwargs)
        Auth = cls.anyblok.Auth
        new_user = Auth.User.insert(musician=musician)
        new_user.scopes.append(Auth.Scope.query().get("musician-auth"))
        new_user.refresh_invitation_token(expires_delta=invitation_token_delta)
        return musician
