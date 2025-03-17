import datetime
from band_management import config


def test_insert_musician_create_user(bm):
    musician = bm.Musician.insert(name="Petrus", email="petrus-v@hotmail.fr")
    assert musician.user is not None
    assert musician.user.musician == musician
    assert len(musician.user.scopes) == 1
    assert musician.user.scopes[0].code == "musician-auth"
    assert musician.user.invitation_token is not None
    assert (
        datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(days=config.INVITATION_TOKEN_EXPIRE_DAYS)
        - musician.user.invitation_token_expiration_date
    ) < datetime.timedelta(seconds=3)
