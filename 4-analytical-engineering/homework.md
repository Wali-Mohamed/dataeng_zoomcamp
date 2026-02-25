Question 3
select count(*) from {{ref('fct_trips')}}  # 110693632


Question 4
select    pickup_zone,   sum(revenue_monthly_total_amount) as total_revenue_2020
from {{ ref('monthly_revenue_per_locations') }}
where service_type = 'Green'
  and extract(year from revenue_month) = 2020
group by pickup_zone
order by total_revenue_2020 desc
limit 1
question 5
select sum(total_monthly_trips)
from {{ref('monthly_revenue_per_locations')}}
where service_type='Green'
AND revenue_month='2019-10-01'
group by revenue_month

Question 6
guessed as I did not download the data

