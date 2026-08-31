import json
import unittest
from pathlib import Path
from pyspark.sql import SparkSession
from src.matching import add_experience_level, extract_ad_skills, filter_suitable_jobs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = PROJECT_ROOT / "skills.json"

with open(SKILLS_FILE, "r", encoding="utf-8") as file:
    SKILLS = json.load(file)

class TestJobMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = (
            SparkSession.builder
            .master("local[1]")
            .appName("SqillifyMatchingTest")
            .getOrCreate()
        )

        cls.spark.sparkContext.setLogLevel("ERROR")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def setUp(self):
        test_jobs = [
            (
                "Junior SQL Developer",
                "We use Python and SQL.",
            ),
            (
                "NoSQL Engineer",
                "Experience with NoSQL and reactive systems.",
            ),
            (
                "React Intern",
                "Build interfaces with React and JavaScript.",
            ),
            (
                "IT Praktikant",
                "Work with Spark and Kafka.",
            ),
            (
                "Data Trainee",
                "Learn Python and Databricks.",
            ),
            (
                "Werkstudent Data Analyst",
                "Experience with Python and SQL.",
            ),
            (
                "Student React Developer",
                "Knowledge of React.",
            ),
            (
                "Senior Python Engineer",
                "Advanced Python experience.",
            ),
            (
                "Engineering Manager",
                "Lead an engineering team.",
            ),
        ]

        jobs_df = self.spark.createDataFrame(
            test_jobs,
            ["title", "description"],
        )

        jobs_df = add_experience_level(jobs_df)
        self.result_df = extract_ad_skills(jobs_df, SKILLS)

    def test_false_skill_matches(self):
        results = {
            row["title"]: row
            for row in self.result_df.collect()
        }

        self.assertEqual(
            results["NoSQL Engineer"]["ad_skills_found"],
            [],
        )
    def test_manager_classification(self):
        results = {
            row["title"]: row["experience_level"]
            for row in self.result_df.collect()
        }

        self.assertEqual(
            results["Engineering Manager"],
            "senior",
        )
    
    def test_junior_classification(self):
        results = {
            row["title"]: row["experience_level"]
            for row in self.result_df.collect()
        }

        self.assertEqual(results["React Intern"], "junior")
        self.assertEqual(results["IT Praktikant"], "junior")
        self.assertEqual(results["Data Trainee"], "junior")

    def test_student_classification(self):
        results = {
            row["title"]: row["experience_level"]
            for row in self.result_df.collect()
        }

        self.assertEqual(
            results["Werkstudent Data Analyst"],
            "student",
        )
        self.assertEqual(
            results["Student React Developer"],
            "student",
        )

    def test_suitable_job_filter(self):
        suitable_jobs = filter_suitable_jobs(self.result_df)

        included_titles = {
            row["title"]
            for row in suitable_jobs.select("title").collect()
        }

        self.assertIn("Junior SQL Developer", included_titles)
        self.assertIn("React Intern", included_titles)
        self.assertIn("IT Praktikant", included_titles)
        self.assertIn("Data Trainee", included_titles)

        self.assertNotIn(
            "Werkstudent Data Analyst",
            included_titles,
        )
        self.assertNotIn(
            "Student React Developer",
            included_titles,
        )
        self.assertNotIn(
            "Senior Python Engineer",
            included_titles,
        )


if __name__ == "__main__":
    unittest.main()