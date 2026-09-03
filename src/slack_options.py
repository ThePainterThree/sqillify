import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = PROJECT_ROOT / "skills.json"

def load_skills():
    with open(SKILLS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
EXPERIENCE_LEVELS = [
    ("Student", "student"),
    ("Junior", "junior"),
    ("Senior", "senior"),
    ("Unspecified", "unspecified"),
]

MATCH_FREQUENCIES = [
    ("Manual", "manual"),
    ("Weekly", "weekly"),
]