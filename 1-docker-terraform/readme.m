docker run -it --rm \
  -e POSTGRES_USER="wali" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18


  uv run pgcli -h localhost -p 5432 -u root -d ny_taxi