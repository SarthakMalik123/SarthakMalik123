from __future__ import annotations
import json
import os
from dataclasses import dataclass
from typing import Optional
import bcrypt

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "users.json")

@dataclass
class User:
    email: str
    password_hash: str


def _ensure_users_file():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        demo_hash = bcrypt.hashpw(b"demo123", bcrypt.gensalt()).decode()
        default = {"users": [{"email": "demo@surakshitpath.ai", "password_hash": demo_hash}]}
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)


def _load_users() -> list[User]:
    _ensure_users_file()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
        return [User(**u) for u in raw.get("users", [])]


def find_user(email: str) -> Optional[User]:
    for u in _load_users():
        if u.email.lower() == email.lower():
            return u
    return None


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


def register_user(email: str, password: str) -> bool:
    if find_user(email):
        return False
    new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    _ensure_users_file()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    raw.setdefault("users", []).append({"email": email, "password_hash": new_hash})
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)
    return True