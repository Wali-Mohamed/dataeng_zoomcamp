import os
from pyflink.table import EnvironmentSettings, TableEnvironment

# 1. Initialize the Environment
env_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = TableEnvironment.create(env_settings)

# CRITICAL: This allows the watermark to move even if some Kafka partitions are empty
t_env.get_config().get_configuration().set_string("table.exec.source.idle-timeout", "10s")
# 1. Source DDL (Ensure the IP is 172.20.0.2!)
t_env.execute_sql("""
    CREATE TABLE green_trips (
        lpep_pickup_datetime STRING,
        tip_amount DOUBLE,
        event_timestamp AS CAST(REPLACE(lpep_pickup_datetime, 'T', ' ') AS TIMESTAMP(3)),
        WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'green-trips',
        'properties.bootstrap.servers' = '172.20.0.2:29092',
        'properties.group.id' = 'flink-tip-job-v1',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'json'
    );
""")

# 2. Sink DDL
t_env.execute_sql("""
    CREATE TABLE hourly_tips_sink (
        window_start TIMESTAMP(3),
        window_end TIMESTAMP(3),
        total_tips DOUBLE
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = 'hourly_tips',
        'username' = 'postgres',
        'password' = 'postgres'
    );
""")

# 3. The 1-Hour Tumble Query
t_env.execute_sql("""
    INSERT INTO hourly_tips_sink
    SELECT 
        TUMBLE_START(event_timestamp, INTERVAL '1' HOUR),
        TUMBLE_END(event_timestamp, INTERVAL '1' HOUR),
        SUM(tip_amount)
    FROM green_trips
    GROUP BY TUMBLE(event_timestamp, INTERVAL '1' HOUR)
""")