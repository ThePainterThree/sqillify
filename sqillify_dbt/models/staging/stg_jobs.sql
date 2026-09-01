{{ config(materialized='view') }}

select job_id, title, company, experience_level,
    location,
    case
        when remote = 1 then 'YES'
        else 'NO'
    end as remote_status,
    description,
    ad_skills_found,
    ad_skills_count,
    published_at,
    job_url,
    source
from {{ source('sqillify', 'jobs') }}
