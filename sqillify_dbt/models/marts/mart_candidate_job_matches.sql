{{ config(materialized='table') }}

select candidates.candidate_id, jobs.job_id,
    count(distinct skills.skill_name) as matched_skill_count

from {{ ref('stg_jobs') }} as jobs

cross join json_table(
    cast(jobs.ad_skills_found as json),
    '$[*]' columns (
        skill_name varchar(100) path '$'
    )
) as skills

inner join {{ source('sqillify', 'candidate_skills') }} as candidates
    on lower(trim(candidates.skill_name))
        = lower(trim(skills.skill_name))

inner join {{ source('sqillify', 'candidate_experience_levels') }} as experience
    on experience.candidate_id = candidates.candidate_id
    and experience.experience_level = jobs.experience_level

group by candidates.candidate_id, jobs.job_id