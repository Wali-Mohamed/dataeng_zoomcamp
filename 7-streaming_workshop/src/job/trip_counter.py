import os
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def run_window_job():
    # 1. Setup Environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(environment_settings=settings)
    
    # CRITICAL: Set parallelism to 1 for Watermark advancement
    t_env.get_config().get_configuration().set_string("parallelism.default", "1")

    # 2. Source DDL (Reading from Redpanda)
    t_env.execute_sql("""
        CREATE TABLE green_trips (
            lpep_pickup_datetime STRING,
            PULocationID INT,
            -- Convert String to Timestamp
            event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda-1:29092',
            'properties.group.id' = 'flink-window-job',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        );
    """)


 
    # 3. Sink DDL (Writing to PostgreSQL)
    t_env.execute_sql("""
        CREATE TABLE sink_postgres (
            window_start TIMESTAMP(3),
            PULocationID INT,
            num_trips BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres', 
            'table-name' = 'processed_trips_window',
            'username' = 'postgres',   -- CHANGED FROM 'your_user'
            'password' = 'postgres',   -- CHANGED FROM 'your_password'
            'driver' = 'org.postgresql.Driver'
        );
    """)

    # 4. The Transformation (Tumbling Window)
    # Using Table API or SQL to count trips in 5-minute blocks
    t_env.execute_sql("""
        INSERT INTO sink_postgres
        SELECT 
            TUMBLE_START(event_timestamp, INTERVAL '5' MINUTES) AS window_start,
            PULocationID,
            COUNT(*) as num_trips
        FROM green_trips
        GROUP BY 
            TUMBLE(event_timestamp, INTERVAL '5' MINUTES),
            PULocationID
    """)

if __name__ == '__main__':
    run_window_job()