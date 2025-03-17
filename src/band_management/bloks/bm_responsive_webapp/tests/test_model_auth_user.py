import datetime
from band_management.bloks.bm_responsive_webapp.fastapi_utils import parse_jwt_token


def test_refresh_invitation_token(bm, pverkest_user):
    assert pverkest_user.invitation_token is None
    assert pverkest_user.invitation_token_expiration_date is None
    pverkest_user.refresh_invitation_token()

    assert pverkest_user.invitation_token is not None
    assert pverkest_user.invitation_token_expiration_date is not None
    token = parse_jwt_token(pverkest_user.invitation_token)
    assert token.sub == str(pverkest_user.uuid)
    assert (
        datetime.datetime.fromtimestamp(token.exp, tz=datetime.timezone.utc)
        == pverkest_user.invitation_token_expiration_date
    )
    assert pverkest_user.invitation_token_expiration_date > datetime.datetime.now(
        tz=datetime.timezone.utc
    ) + datetime.timedelta(seconds=30)


def test_refresh_invitation_token_explicit_expires_delta(bm, pverkest_user):
    assert pverkest_user.invitation_token is None
    assert pverkest_user.invitation_token_expiration_date is None
    pverkest_user.refresh_invitation_token(expires_delta=datetime.timedelta(seconds=5))

    assert pverkest_user.invitation_token is not None
    assert pverkest_user.invitation_token_expiration_date is not None
    token = parse_jwt_token(pverkest_user.invitation_token)
    assert token.sub == str(pverkest_user.uuid)
    assert (
        datetime.datetime.fromtimestamp(token.exp, tz=datetime.timezone.utc)
        == pverkest_user.invitation_token_expiration_date
    )
    assert pverkest_user.invitation_token_expiration_date <= datetime.datetime.now(
        tz=datetime.timezone.utc
    ) + datetime.timedelta(seconds=5)
