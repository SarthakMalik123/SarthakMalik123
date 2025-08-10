from __future__ import annotations
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


def get_ors_api_key() -> str | None:
    return os.getenv("ORS_API_KEY")


def get_openweather_api_key() -> str | None:
    return os.getenv("OPENWEATHER_API_KEY")