CREATE DATABASE IF NOT EXISTS sqillify
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE sqillify;

CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255),
    experience_level VARCHAR(20),
    location VARCHAR(255),
    remote BOOLEAN,
    description LONGTEXT,
    ad_skills_found JSON,
    ad_skills_count INT,
    published_at VARCHAR(30),
    job_url VARCHAR(1000),
    source VARCHAR(100)
);

SELECT COUNT(*) AS total_jobs
FROM jobs;

SELECT title, company, experience_level, ad_skills_found, ad_skills_count
FROM jobs
ORDER BY ad_skills_count DESC, title
LIMIT 10;