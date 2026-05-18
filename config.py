import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

# Path to your SQLite jobs database — set JOB_DB_PATH in .env to override
DB_PATH = Path(os.getenv("JOB_DB_PATH", BASE_DIR / "earlyapply.db"))

CHROMA_DIR = BASE_DIR / ".chroma"
COLLECTION  = "jobs"
TOP_K       = 8       # results returned per query
DESC_CHARS  = 1000    # chars to embed from job description
MAX_INGEST  = 5000    # most recent jobs to index
