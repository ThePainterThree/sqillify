{{ config(materialized='table') }}

select skills.skill_name, count(distinct jobs.job_id) as job_count
from {{ ref('stg_jobs') }} as jobs
cross join json_table(
    CAST(jobs.ad_skills_found AS JSON),
    '$[*]' columns (
        skill_name varchar(100) path '$'
    )
) as skills
group by skills.skill_name
order by job_count desc, skills.skill_name
