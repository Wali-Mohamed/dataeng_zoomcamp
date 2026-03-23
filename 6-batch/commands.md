spark-submit \
    --master spark://localhost:7077 \
    --deploy-mode client \
    --executor-memory 512m \
    --total-executor-cores 2 \
    --verbose \
    06_spark_sql.py \
    --input_green "/home/wali/data_eng_2026/6-batch/data/pq/green/2021/*" \
    --input_yellow "/home/wali/data_eng_2026/6-batch/data/pq/yellow/2021/*" \
    --output /home/wali/data_eng_2026/6-batch/data/reports-2021