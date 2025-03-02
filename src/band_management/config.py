import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_PATH = Path(os.environ.get("DATA_PATH", "./bm-management-data"))
if os.environ.get("ORIGINAL_SCORE_PATH"):
    ORIGINAL_SCORE_PATH = Path(os.environ.get("ORIGINAL_SCORE_PATH"))
else:
    ORIGINAL_SCORE_PATH = DATA_PATH / "original"

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
