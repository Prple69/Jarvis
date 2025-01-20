import json

from .translation_manager import Translation

def save_translation_as_json(translation: Translation, path: str = "RU.json"):
    with open(path, "w") as f:
        f.write(json.dumps(translation.model_dump()))

def load_translation_from_json(path: str = "RU.json") -> Translation:
    with open(path, "r") as f:
        text = f.read()

    return Translation(**json.loads(text))