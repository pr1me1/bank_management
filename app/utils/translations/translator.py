import logging
from typing import Dict, Optional

from app.models import Language

logger = logging.getLogger(__name__)


class Translator:
    def __init__(self, messages: Dict[str, Dict[str, str]]):
        self.messages = messages
        self.default_lang = Language.RUSSIAN.value

    def get(
            self,
            key: str,
            lang: Optional[str] = None,
            **kwargs
    ):
        lang = lang or self.default_lang

        if isinstance(lang, Language):
            lang = lang.value

        message_dict = self.messages.get(key, None)

        if not message_dict:
            logger.warning(f"Missing translation key: {key}")
            return f"Missing translation key: {key}"

        translation = message_dict.get(lang)
        if not translation:
            translation = message_dict.get(self.default_lang)
            if not translation:
                logger.warning(f"Missing translation: {key}.{lang}")
                return f"[Missing: {key}.{lang}]"

        if kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Format error in {key}: missing {e}")
                return translation

        return translation


_translator: Optional[Translator] = None


def initialize_translator(messages: Dict[str, Dict[str, str]]) -> Translator:
    global _translator
    _translator = Translator(messages)
    return _translator


def get_translator() -> Translator:
    if _translator is None:
        raise RuntimeError("Translator not initialized")
    return _translator


def t(key: str, lang: Optional[str] = None, **kwargs):
    return get_translator().get(key, lang, **kwargs)

