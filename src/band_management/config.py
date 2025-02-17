import os
from pathlib import Path

DATA_PATH = Path(os.environ.get("DATA_PATH", "./bm-management-data"))
if os.environ.get("ORIGINAL_SCORE_PATH"):
    ORIGINAL_SCORE_PATH = Path(os.environ.get("ORIGINAL_SCORE_PATH"))
else:
    ORIGINAL_SCORE_PATH = DATA_PATH / "original"
