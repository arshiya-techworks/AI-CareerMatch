import sqlite3
from pathlib import Path
import json


# Database location
DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = DATABASE_DIR / "resume_screening.db"


def create_database():
    """Create the resume screening database."""

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS screening_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            email TEXT,
            phone TEXT,
            education TEXT,
            experience_years REAL,
            skills TEXT,
            recommended_role TEXT,
            role_match_score REAL,
            skill_score REAL,
            quality_score REAL,
            experience_score REAL,
            overall_score REAL,
            status TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_result(result):
    """Save a screening result to the database."""

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    skills = result.get(
        "skills",
        []
    )

    if isinstance(skills, list):
        skills = json.dumps(skills)

    cursor.execute(
        """
        INSERT INTO screening_results (
            candidate_name,
            email,
            phone,
            education,
            experience_years,
            skills,
            recommended_role,
            role_match_score,
            skill_score,
            quality_score,
            experience_score,
            overall_score,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result.get(
                "candidate_name",
                "Not detected"
            ),
            result.get(
                "email",
                "Not detected"
            ),
            result.get(
                "phone",
                "Not detected"
            ),
            result.get(
                "education",
                "Not detected"
            ),
            result.get(
                "experience_years",
                0
            ),
            skills,
            result.get(
                "recommended_role",
                "N/A"
            ),
            result.get(
                "role_match_score",
                0
            ),
            result.get(
                "skill_score",
                0
            ),
            result.get(
                "quality_score",
                0
            ),
            result.get(
                "experience_score",
                0
            ),
            result.get(
                "overall_score",
                0
            ),
            result.get(
                "status",
                "Needs Review"
            )
        )
    )

    connection.commit()
    connection.close()