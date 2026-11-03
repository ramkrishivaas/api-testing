import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(filename):
    path = ROOT / "test_data" / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def load_schema(filename):
    path = ROOT / "schemas" / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
