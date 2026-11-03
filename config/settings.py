
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")

API_TOKEN = os.getenv("API_TOKEN", "")

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

VERIFY_TLS = (
    os.getenv("VERIFY_TLS", "true").lower() == "true"
)

MAPINDIA_TOKEN = os.getenv("MAPINDIA_TOKEN", "")


def env_value(key, default=None):
    return os.getenv(key, default)


def env_id(key):
    return os.getenv(key, "").strip()
