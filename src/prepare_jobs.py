import json
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
import re
from html import unescape

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "bronze" / "raw_jobs.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "silver" / "standard_jobs.json"

def clean_html(html_text):
    if not html_text:
        return ""

    decoded_text = str(html_text)

    for _ in range(3):
        new_text = unescape(decoded_text)

        if new_text == decoded_text:
            break

        decoded_text = new_text

    clean_text = BeautifulSoup(
        decoded_text,
        "html.parser"
    ).get_text(" ", strip=True)

    clean_text = clean_text.replace("\xa0", " ")
    clean_text = re.sub(r"\s+", " ", clean_text)

    return clean_text.strip()

def convert_timestamp(unix_timestamp):
    return datetime.fromtimestamp(
        unix_timestamp,
        tz=timezone.utc
    ).isoformat().replace("+00:00", "Z")

def prepare_job(raw_job):
    return {
        "job_id": raw_job["slug"],
        "title": raw_job["title"],
        "company": raw_job["company_name"],
        "location": raw_job["location"],
        "remote": raw_job["remote"],
        "job_types": raw_job["job_types"],
        "tags": raw_job["tags"],
        "description": clean_html(raw_job["description"]),
        "published_at": convert_timestamp(raw_job["created_at"]),
        "job_url": raw_job["url"],
        "source": "arbeitnow"
    }

with INPUT_FILE.open("r", encoding="utf-8") as file:
    raw_jobs = json.load(file)

standard_jobs = []

for raw_job in raw_jobs:
    standard_job = prepare_job(raw_job)
    standard_jobs.append(standard_job)


with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    json.dump(
        standard_jobs,
        file,
        ensure_ascii=False,
        indent=2
    )
print(f"Prepared {len(standard_jobs)} jobs.")