select count(*) from {{ref('monthly_revenue_per_locations')}} # 11947
select count(*) from {{ref('int_trips_unioned')}} # 113 417 203
select count(*) from {{ref('int_trips')}}   # 110693632
select count(*) from {{ref('fct_trips')}}  # 110693632
