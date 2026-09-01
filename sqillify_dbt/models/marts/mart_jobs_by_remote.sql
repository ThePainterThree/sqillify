{{ config(materialized='table') }}

select remote_status, count(distinct job_id) as job_count
from {{ ref('stg_jobs') }}
group by remote_status