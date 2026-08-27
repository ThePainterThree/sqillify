import json
from pathlib import Path

import requests


API_URL = "https://www.arbeitnow.com/api/job-board-api"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw_jobs.json"


response = requests.get(API_URL, timeout=30)
response.raise_for_status()

api_result = response.json()
jobs = api_result["data"]


# Save the original jobs, no transforamtion
with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    json.dump(jobs, file, ensure_ascii=False, indent=2)

print("Status code:", response.status_code)
print("Number of jobs received:", len(jobs))


# preview of the first job
first_job = jobs[0]

print("\nFirst job:")
print("Title:", first_job["title"])
print("Company:", first_job["company_name"])
print("Location:", first_job["location"])
print("Remote:", first_job["remote"])
print("Job types:", first_job["job_types"])
print("Tags:", first_job["tags"])
print("Created at:", first_job["created_at"])
print("URL:", first_job["url"])
print("Description preview:", first_job["description"][:200])

print(f"\nRaw jobs saved to: {OUTPUT_FILE}")