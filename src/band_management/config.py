import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_PATH = Path(os.environ.get("DATA_PATH", "./bm-management-data"))
if os.environ.get("ORIGINAL_SCORE_PATH"):
    ORIGINAL_SCORE_PATH = Path(os.environ.get("ORIGINAL_SCORE_PATH"))
else:
    ORIGINAL_SCORE_PATH = DATA_PATH / "original"

# to get a string more secure you could run something like this:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# make it configurable over anyblok config
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "insecrure_secretkey"
    logger.warning("Insecure secret key to generate JW-Token")

ALGORITHM = "HS256"
"""JWT TOKEN hash lagorithm"""

ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 120)
"""How long access token is valid

Both on responsive web app end api.
"""

ACCESS_TOKEN_RENEW_MINUTES = os.environ.get("ACCESS_TOKEN_RENEW_MINUTES", 30)
"""How long we accept user to not use the application
and keep the session valid must be lower than
ACCESS_TOKEN_EXPIRE_MINUTES

So any request done while ACCESS_TOKEN_EXPIRE_MINUTES is valid and
ACCESS_TOKEN_RENEW_MINUTES before the end of life will renew the
token for a new ACCESS_TOKEN_EXPIRE_MINUTES.

Long enough to play a score entirely before consult it again
without the needs to reconnect.

Only for the responsive web app. The api endpoint must handle a new
connexion
"""

INVITATION_TOKEN_EXPIRE_DAYS = os.environ.get("INVITATION_TOKEN_EXPIRE_DAYS", 15)
"""How long the invitation token is valid
to let new user access to their new account.
"""
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = os.environ.get(
    "RESET_PASSWORD_TOKEN_EXPIRE_MINUTES", 30
)
"""How long the reset password token is valid
Also used while registering new user
"""

DEFAULT_LANG = os.environ.get("DEFAULT_LANG", "en")
AVAILABLE_LANGS = ["fr", "en"]


ITEM_PER_PAGE = os.environ.get("ITEM_PER_PAGE", 60)
"""How many items per page
"""
