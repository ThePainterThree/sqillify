import re
from collections.abc import Sequence
from pyspark.sql import DataFrame
from pyspark.sql.functions import array, array_compact, col, lit,lower, size, when

def add_experience_level(jobs_df: DataFrame) -> DataFrame:
    return jobs_df.withColumn(
        "experience_level",
        when(
            lower(col("title")).rlike(
                r"\b(student|working student|werkstudent)\b"
            ),
            "student",
        )
        .when(
            lower(col("title")).rlike(
                r"\b(junior|jr\.?|trainee|intern|internship|praktikant|praktikantin|praktikum)\b"
            ),
            "junior",
        )
        .when(
            lower(col("title")).rlike(
                r"\b(senior|sr\.?|lead|principal|director|manager)\b|head of"
            ),
            "senior",
        )
        .otherwise("unspecified"),
    )

def extract_ad_skills(
    jobs_df: DataFrame,
    skills_list: Sequence[str],
) -> DataFrame:
    ad_skill_matches = [
        when(
            lower(col("description")).rlike(
                rf"(?<![a-z0-9]){re.escape(skill.lower())}(?![a-z0-9])"
            ),
            lit(skill),
        )
        for skill in skills_list
    ]

    return (
        jobs_df
        .withColumn(
            "ad_skills_found",
            array_compact(array(*ad_skill_matches)),
        )
        .withColumn(
            "ad_skills_count",
            size(col("ad_skills_found")),
        )
    )

def filter_suitable_jobs(jobs_df: DataFrame) -> DataFrame:
    return (
        jobs_df
        .filter(col("match_count") > 0)
        .filter(
            col("experience_level").isin(
                "junior",
                "unspecified",
            )
        )
    )