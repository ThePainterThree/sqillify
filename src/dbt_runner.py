import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "sqillify_dbt"


def rebuild_candidate_matches():
    result = subprocess.run(
        [
            "python",
            "-m",
            "dbt.cli.main",
            "build",
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--select",
            "mart_candidate_job_matches+",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout