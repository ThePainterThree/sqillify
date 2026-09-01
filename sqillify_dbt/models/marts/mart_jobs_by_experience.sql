{{ config(materialized='table') }}

select experience_level, count(distinct job_id) as job_count
from {{ ref('stg_jobs') }}
group by experience_level