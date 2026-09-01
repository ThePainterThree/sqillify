{{ config(materialized='table') }}

select
    matches.candidate_id,
    matches.job_id,
    matches.matched_skill_count,
    jobs.title,
    jobs.company,
    jobs.experience_level,
    jobs.location,
    jobs.remote_status,
    jobs.published_at,
    jobs.job_url
from {{ ref('mart_candidate_job_matches') }} as matches
inner join {{ ref('stg_jobs') }} as jobs
    on matches.job_id = jobs.job_id