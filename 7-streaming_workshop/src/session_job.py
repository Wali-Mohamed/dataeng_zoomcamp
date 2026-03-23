import os
from pyflink.table import EnvironmentSettings, TableEnvironment

# 1. Initialize the Environment
env_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = TableEnvironment.create(env_settings)

# CRITICAL: This allows the watermark to move even if some Kafka partitions are empty
t_env.get_config().get_configuration().set_string("table.exec.source.idle-timeout", "10s")

# 2. Source DDL (Handles the 'T' in your strings)
t_env.execute_sql("""
    CREATE TABLE green_trips (
        lpep_pickup_datetime STRING,
        PULocationID INT,
        event_timestamp AS CAST(REPLACE(lpep_pickup_datetime, 'T', ' ') AS TIMESTAMP(3)),
        WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'green-trips',
        'properties.bootstrap.servers' = '172.20.0.2:29092',
        'properties.group.id' = 'flink-session-group-v2',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'json'
    );
""")

# 3. Sink DDL (Connects to Postgres)
t_env.execute_sql("""
    CREATE TABLE session_trips_sink (
        window_start TIMESTAMP(3),
        window_end TIMESTAMP(3),
        pulocationid INT,
        num_trips BIGINT
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = 'session_trips',
        'username' = 'postgres',
        'password' = 'postgres'
    );
""")

# 4. The Session Window Query
# This groups trips that occur within 5 minutes of each other.
t_env.execute_sql("""
    INSERT INTO session_trips_sink
    SELECT 
        SESSION_START(event_timestamp, INTERVAL '5' MINUTE) AS window_start,
        SESSION_END(event_timestamp, INTERVAL '5' MINUTE) AS window_end,
        PULocationID,
        COUNT(*) AS num_trips
    FROM green_trips
    GROUP BY SESSION(event_timestamp, INTERVAL '5' MINUTE), PULocationID
""")