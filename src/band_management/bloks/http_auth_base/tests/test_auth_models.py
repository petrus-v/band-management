def test_authenticate(Auth, joe_user):
    user = Auth.authenticate("joe", "password")
    assert user is not None, (
        "Authentication failed expected receive authenticated user (not None)"
    )
    assert user == joe_user


def test_wrong_password(Auth, joe_user):
    user = Auth.authenticate("joe", "wrong pwd")
    assert user is None


def test_wrong_username(Auth, joe_user):
    user = Auth.authenticate("wrong name", "password")
    assert user is None


def test_not_a_user(Auth):
    user = Auth.authenticate("test", "test")
    assert user is None
