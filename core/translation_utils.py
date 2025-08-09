import json

def load_translation(lang="en"):
    with open(f"translations/{lang}.json", "r", encoding="utf-8") as f:
        return json.load(f)