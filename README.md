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

4. Build and start the containers:

   ```bash
   docker compose up --build -d
   ```

5. Open <http://localhost:5000>.

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
3. Recreate the Compose deployment.
4. Run an HTTP smoke test.

The Jenkins environment must have:

- Access to a Docker daemon
- Docker Compose v2 (`docker compose`)
- A Jenkins secret-text credential with the ID `db-password`
- Network access to GitHub
- Membership in the Compose network so the smoke test can resolve `todo-app`

`Dockerfile.jenkins` is the custom Jenkins image definition intended to provide the Docker CLI. The Jenkins runtime must also be configured with access to the host Docker socket or another Docker daemon before the pipeline can build or deploy containers.

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
