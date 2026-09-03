import mysql.connector
from database import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE,
    MYSQL_USER,
    MYSQL_PASSWORD,
)

def get_top_job_matches(candidate_id: int, limit: int = 10):
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        database=MYSQL_DATABASE,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
    )

    cursor = connection.cursor(dictionary=True)

    sql = """
        SELECT
            title,
            company,
            experience_level,
            location,
            remote_status,
            matched_skill_count,
            job_url
        FROM mart_candidate_job_details
        WHERE candidate_id = %s
        ORDER BY matched_skill_count DESC
        LIMIT %s
    """

    cursor.execute(
        sql,
        (candidate_id, limit),
    )

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()
    return jobs

def format_job_matches(jobs):
    if not jobs:
        return "No jobs matched your selected criteria."

    lines = [
        "Here is a selection of jobs matching your criteria:",
        "",
    ]

    for index, job in enumerate(jobs, start=1):
        lines.extend([
            f"*{index}. {job['title']}*",
            f"Company: {job['company']}",
            f"Location: {job['location']}",
            f"Experience: {job['experience_level'].title()}",
            f"Remote: {job['remote_status']}",
            f"Matched skills: {job['matched_skill_count']}",
            f"<{job['job_url']}|View job>",
            "",
        ])

    return "\n".join(lines)