import configparser

from .enums import AvailableLanguages

from .schemas import Translation

from .language.EN import get_translation_en
from .language.RU import get_translation_ru


def get_translation() -> Translation:
    language = get_language()
    if language == AvailableLanguages.RU:
        return get_translation_ru()
    else:
        return get_translation_en()


def get_language() -> AvailableLanguages:
    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf-8')
    language = config.get('Settings', 'language')
    result = AvailableLanguages.get(language, AvailableLanguages.EN)
    return result