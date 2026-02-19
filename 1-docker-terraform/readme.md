# Docker Quick Cheat-Sheet

## 1) Health checks (is Docker working?)

**Command**
```bash
docker version
 ```
Note: Confirms Docker client can talk to the engine + shows versions. 


Command

docker info
Note: Shows engine status and setup details (WSL backend, storage driver, etc.).

Command

```bash
docker run hello-world 
 ```

Note: Full test: pulls an image (if needed) and runs a container.

2) Images (blueprints)
Command

docker pull ubuntu:24.04
Note: Download an image to your machine.

Command

docker images
Note: List images stored locally.

Command

docker rmi ubuntu:24.04
Note: Remove an image (only works if no containers rely on it).

3) Containers (instances)
Create / run
Command

docker run ubuntu:24.04 echo "hi"
Note: Create + run a container to execute one command, then exit.

Command

docker run -it ubuntu:24.04 bash
Note: Start an interactive terminal inside a new container.

Command

docker run -d --name mynginx nginx:alpine
Note: Run in background (detached) and name the container.

List / manage
Command

docker ps
Note: List running containers.

Command

docker ps -a
Note: List all containers (running + stopped).

Command

docker stop mynginx
Note: Stop a running container.

Command

docker start mynginx
Note: Start a stopped container.

Command

docker restart mynginx
Note: Restart a container.

Command

docker rm mynginx
Note: Delete a stopped container.

Command

docker rm -f mynginx
Note: Force delete a container (even if running).

4) Exec + Logs (inspect running containers)
Command

docker exec -it mynginx sh
Note: Open a shell inside an already running container.

Command

docker logs mynginx
Note: Show container logs.

Command

docker logs -f mynginx
Note: Follow logs live.

5) Ports (access services)
Command

docker run -d --name web -p 8080:80 nginx:alpine
Note: Map PC port 8080 → container port 80 (open http://localhost:8080).

6) Volumes (persist data)
Bind mount (share your folder)
Command

docker run -it --rm -v "$PWD":/work -w /work python:3.12-slim python -V
Note: Share your current folder with the container and run Python there.

Named volume (best for databases)
Command

docker volume create pgdata
Note: Create a named volume.

Command

docker run -d --name pg -e POSTGRES_PASSWORD=pass -v pgdata:/var/lib/postgresql/data -p 5432:5432 postgres:16
Note: Run Postgres with persistent storage and expose port 5432.

Command

docker volume ls
Note: List volumes.

7) Entry points + commands (how containers start)
Key idea
A container starts by running a command.

ENTRYPOINT = the main executable (harder to replace)

CMD = default arguments (easy to override)

In Dockerfile terms:

ENTRYPOINT ["python"]

CMD ["app.py"]

So running the container executes:

python app.py
Inspect an image’s ENTRYPOINT / CMD
Command

docker image inspect nginx:alpine --format='Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
Note: Shows what will run by default when the container starts.

Override CMD (keep ENTRYPOINT, change args)
Command

docker run ubuntu:24.04 echo "hello"
Note: If the image has no ENTRYPOINT, this replaces the default CMD.
If it has an ENTRYPOINT, echo "hello" becomes arguments to it.

Override ENTRYPOINT (replace the main executable)
Command

docker run --rm --entrypoint sh nginx:alpine -c 'echo hi; nginx -v'
Note: Useful for debugging when the default startup command is not what you want.

Typical examples
Example: Nginx image

ENTRYPOINT is usually empty (or a script), CMD starts nginx in the foreground.

If you run:

docker run nginx:alpine
It starts nginx.

Example: Python app

If your image has:

ENTRYPOINT ["python"]

CMD ["main.py"]

Then you can run a different script by overriding CMD:

docker run mypythonimage other.py
8) Cleanup (when messy)
Command

docker container prune
Note: Remove all stopped containers.

Command

docker image prune
Note: Remove unused images.

Command

docker system prune -a
Note: Remove all unused containers/images/networks (aggressive—be careful).


If you want, paste your `git status` after saving and I’ll tell you the exact commit/push commands for your current branch.
::contentReference[oaicite:0]{index=0}

bash ```
docker run -it --rm \
  -e POSTGRES_USER="wali" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```

# how to open pgcli on command line
  uv run pgcli -h localhost -p 5432 -u wali -d ny_taxi

# create docker network
```
docker network create pg-network
```
### see the list of networks
```
docker network ls
```

 uv run python ingest_data1.py \
  --pg-user=wali \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips_code \
  --year=2021 \
  --month=1 \
  --chunksize=100000 

# build a new image
docker build -t taxi_ingest:v001 .
### run the container of postgress
docker run -it --rm \
  -e POSTGRES_USER="wali" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18



# ingest data to the database
 ```
  docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --pg-user=wali \
    --pg-pass=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips_2021_1 \
    --year=2021 \
    --month=2 \
    --chunksize=100000
### run pgadmin
```
 docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```
1-docker-terraform-default-1

docker run -it \
  --network 1-docker-terraform_default \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips_2021_1 \
    --year=2021 \
    --month=1 \
    --chunksize=100000
  docker run -it \
  --network 2-workflow-orchestration_default \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips_2021_1 \
    --year=2021 \
    --month=1 \
    --chunksize=100000