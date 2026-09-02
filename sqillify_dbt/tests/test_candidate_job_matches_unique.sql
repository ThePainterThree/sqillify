-- tests if candidate job pair dont show up twice. if it returns 0 rows, the test passess
select candidate_id, job_id,
    count(*) as row_count
from {{ ref('mart_candidate_job_matches') }}
group by candidate_id, job_id
having count(*) > 1