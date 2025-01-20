from enum import Enum
from typing import Any


class OpenWeatherLang(Enum):
    RU: str = "ru"
    EN: str = "en"

class AvailableLanguages(Enum):
    EN: str = "EN"
    RU: str = "RU"

    @classmethod
    def get(cls, value: Any, default: Any = None):
        """
        If this enum contains passed value, then return a corresponding enum item. Else returns default
        """
        result = default
        for item in cls:
            if value == item.value:
                result = item
                break
        return result