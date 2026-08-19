# Flask To-Do App with Docker Compose and Jenkins

A Flask and PostgreSQL task-management application packaged with Docker Compose, with a Jenkins pipeline for build, deployment, and smoke-test automation. Tasks and comments are stored in a persistent Docker named volume.

## Features

- Create, edit, advance, filter, and delete tasks
- Add, edit, and delete comments associated with a task
- Persist application data in PostgreSQL
- Report application and database readiness through `GET /health`
- Build and run the application and database with Docker Compose
- Serve the Flask application with Gunicorn as an unprivileged container user
- Define Jenkins pipeline stages for checkout, image build, deployment, and smoke testing

## Prerequisites

- Docker Desktop, or Docker Engine with Docker Compose v2
- Git

## Start the application

1. Clone the repository and enter it:

   ```bash
   git clone https://github.com/DharshineKannan/flask-todo-jenkins.git
   cd flask-todo-jenkins
   ```

2. Create your local environment file:

   macOS/Linux:

   ```bash
   cp .env.example .env
   ```

   Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Open `.env` and replace the example password with a strong local password:

   ```dotenv
   DB_USER=tododb_user
   DB_PASSWORD=replace_with_a_strong_password
   DB_NAME=tododb
   ```

   Do not commit `.env`. It is already excluded by `.gitignore` and `.dockerignore`.

4. Create the external network used by the application and Jenkins. This is a one-time command:

   ```bash
   docker network create shared-net
   ```

   If Docker reports that `shared-net` already exists, continue to the next step.

5. Build and start the containers:

   ```bash
   docker compose up --build -d
   ```

6. Open <http://localhost:5000>.

## Verify container health

```bash
docker compose ps
curl http://localhost:5000/health
```

The health endpoint returns the following response after Flask can connect to PostgreSQL:

```json
{"status":"healthy"}
```

To follow the application logs:

```bash
docker compose logs -f web db
```

## Stop the application

Stop and remove the containers while retaining database data:

```bash
docker compose down
```

To also permanently delete the PostgreSQL named volume and all stored tasks:

```bash
docker compose down --volumes
```

## Configuration

Docker Compose reads these variables from `.env`:

| Variable | Purpose | Example |
| --- | --- | --- |
| `DB_USER` | PostgreSQL user | `tododb_user` |
| `DB_PASSWORD` | PostgreSQL password; required | `replace_with_a_strong_password` |
| `DB_NAME` | PostgreSQL database | `tododb` |

`DB_USER` and `DB_NAME` have Compose defaults matching `.env.example`. `DB_PASSWORD` is intentionally required, so Compose stops with a clear error when it is missing.

## Jenkins pipeline

`Jenkinsfile` defines the following stages:

1. Clone the `main` branch from GitHub.
2. Build the application image with Docker Compose.
3. Create the persistent `shared-net` network if needed and attach the Jenkins container.
4. Recreate the Compose deployment.
5. Run an HTTP smoke test.

The Jenkins environment must have:

- Access to a Docker daemon
- Docker Compose v2 (`docker compose`)
- A Jenkins secret-text credential with the ID `db-password`
- Network access to GitHub

`Dockerfile.jenkins` is the custom Jenkins image definition intended to provide the Docker CLI. The Jenkins runtime must also be configured with access to the host Docker socket or another Docker daemon before the pipeline can build or deploy containers.

The application uses the external Docker network `shared-net`. The pipeline creates it when missing and attaches the executing Jenkins container using `$HOSTNAME`. Because Compose does not own an external network, `docker compose down` does not remove it; Jenkins therefore remains connected across deployments and can resolve the `web` service during the smoke test.

The smoke test retries `http://web:5000/health` for up to 30 seconds and only succeeds when it receives `{"status":"healthy"}`. Because `/health` executes `SELECT 1` through SQLAlchemy, it checks both the Gunicorn process and PostgreSQL connectivity.

## Infrastructure choices

- **Docker Compose instead of separate Docker commands:** the application needs a web service, PostgreSQL, health-based startup ordering, persistent storage, environment configuration, and shared networking. Compose keeps that multi-container configuration declarative and repeatable.
- **Jenkins instead of GitHub Actions:** this project demonstrates a self-hosted pipeline that builds and deploys through the Docker daemon on the deployment host. It provides hands-on experience with Jenkins credentials, pipeline stages, container networking, and deployment smoke tests.

## Project structure

```text
.
|-- .dockerignore
|-- .env.example
|-- .gitignore
|-- app.py
|-- Dockerfile
|-- Dockerfile.jenkins
|-- Jenkinsfile
|-- docker-compose.yml
|-- requirements.txt
|-- wsgi.py
`-- templates/
    `-- index.html
```

The `pg_data` named volume persists PostgreSQL data between container restarts and rebuilds.
