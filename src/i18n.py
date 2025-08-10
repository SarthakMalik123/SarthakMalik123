import json
import os
from functools import lru_cache
from typing import Dict

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "xx": "Other",
}

DEFAULT_LANGUAGE = "en"

@lru_cache(maxsize=8)
def load_translations(lang_code: str) -> Dict[str, str]:
    lang_code = lang_code if lang_code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "i18n", f"{lang_code}.json")
    if not os.path.exists(path):
        path = os.path.join(base_dir, "i18n", f"{DEFAULT_LANGUAGE}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class Translator:
    def __init__(self, lang: str):
        self.lang = lang
        self.translations = load_translations(lang)

    def set_lang(self, lang: str):
        self.lang = lang
        self.translations = load_translations(lang)

    def t(self, key: str, default: str | None = None) -> str:
        if key in self.translations:
            return self.translations[key]
        if default is not None:
            return default
        # fallback to English if available
        fallback = load_translations(DEFAULT_LANGUAGE)
        return fallback.get(key, key)