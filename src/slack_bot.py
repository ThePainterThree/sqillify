import os
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_views import build_preferences_modal
from database import save_candidate_preferences
from job_results import get_top_job_matches, format_job_matches
from dbt_runner import rebuild_candidate_matches

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

@app.command("/sqillify")
def handle_sqillify_command(ack, body, client):
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view=build_preferences_modal(),
    )

@app.view("sqillify_preferences")
def handle_preferences_submission(ack, body, view, client):
    ack()

    values = view["state"]["values"]

    experience_levels = [
        option["value"]
        for option in values["experience"]["experience_levels"]["selected_options"]
    ]

    skills = [
        option["value"]
        for option in values["skills"]["skills_selected"]["selected_options"]
    ]

    match_frequency = (
        values["frequency"]["match_frequency"]["selected_option"]["value"]
    )

    #  existing candidate profile.
    candidate_id = 1

    save_candidate_preferences(
        candidate_id=candidate_id,
        skills=skills,
        experience_levels=experience_levels,
        match_frequency=match_frequency,
    )

    rebuild_candidate_matches()
    
    jobs = get_top_job_matches(candidate_id)
    message = format_job_matches(jobs)

    client.chat_postMessage(
        channel=body["user"]["id"],
        text=message,
    )

    print(f"Preferences saved for candidate {candidate_id}")
    print("Experience:", experience_levels)
    print("Skills:", skills)
    print("Frequency:", match_frequency)

if __name__ == "__main__":
    print("Sqillify Slack bot starting...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()