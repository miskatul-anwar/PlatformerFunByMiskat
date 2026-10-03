import json
from src.platformer.config import SAVE_FILE

def load_save_data():
    try:
        if SAVE_FILE.exists():
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Save load warning: {e}")
    return {"high_score": 0, "unlocked_level": 1, "stars": {}}

def write_save_data(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save write warning: {e}")
