# DevOps CI/CD Project

A simple Python Flask service that is built, tested, containerized with Docker, and verified automatically by a GitHub Actions CI/CD pipeline on every push to `main`. Optionally, the pipeline also deploys the container to a Docker host over SSH.

## Technologies Used

- **Python 3.12** and **Flask 3.1.0** for the web service
- **unittest** (Python standard library) for the basic tests
- **Docker** to package and run the service in a container
- **GitHub** to host the source code
- **GitHub Actions** (YAML workflow) for the CI/CD pipeline

## Project Structure

```text
DevOps/
│
├── app.py                      # Flask application with / and /health endpoints
├── test_app.py                 # Unit tests for the endpoints
├── requirements.txt            # Python dependencies (Flask)
├── Dockerfile                  # Instructions to build the Docker image
├── .dockerignore               # Files excluded from the Docker build
├── .gitignore                  # Files excluded from Git
├── README.md                   # This file
│
└── .github/
    └── workflows/
        └── cicd.yml            # GitHub Actions CI/CD pipeline
```

## API Endpoints

| Endpoint  | Method | Response                                                  |
|-----------|--------|-----------------------------------------------------------|
| `/`       | GET    | `{"message": "Welcome to the DevOps CI/CD demo service!"}` |
| `/health` | GET    | `{"status": "healthy"}`                                   |

## Run the Application Locally

Requires Python 3.12 or newer.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the tests
python -m unittest -v test_app

# 4. Start the application
python app.py
```

Open http://localhost:5000 and http://localhost:5000/health in your browser.

To use a different port, set the `PORT` environment variable before running (for example `PORT=8080 python app.py`).

## Build and Run with Docker

Requires Docker Desktop (or Docker Engine) to be installed and running.

```bash
# Build the image
docker build -t devops-cicd-app .

# Run the container, mapping host port 5000 to container port 5000
docker run -d --name devops-cicd-app -p 5000:5000 devops-cicd-app

# Test the endpoints
curl http://localhost:5000/
curl http://localhost:5000/health

# View logs
docker logs devops-cicd-app

# Stop and remove the container
docker stop devops-cicd-app
docker rm devops-cicd-app
```

## CI/CD Pipeline (GitHub Actions)

The workflow file is `.github/workflows/cicd.yml`. It runs automatically when code is pushed to the `main` branch and performs these steps on an Ubuntu runner:

**Job 1: `build-test`**

1. **Checkout repository**: downloads the code from GitHub.
2. **Set up Python**: installs Python 3.12 (with pip caching).
3. **Install dependencies**: runs `pip install -r requirements.txt`.
4. **Run tests**: runs the unit tests in `test_app.py`. If a test fails, the pipeline stops.
5. **Build Docker image**: builds the image from the `Dockerfile`, tagged with the commit SHA and `latest`.
6. **Run Docker container**: starts the container and maps port 5000.
7. **Verify application is responding**: calls `/health` (retrying for up to about 30 seconds). The pipeline fails if the service does not respond successfully, and the container logs are printed.
8. **Save image as artifact**: exports the image to `image.tar.gz` and uploads it for the deploy job (kept for 1 day).
9. **Stop and remove container**: cleans up the container, even if an earlier step failed.

**Job 2: `deploy`** (optional)

Runs only on `main` when the repository variable `DEPLOY_ENABLED` is `true`. It copies the saved image to a Docker host over SSH, loads it, and runs it on port 8080 with a health check. Until the variable is set, this job is skipped.

## Set Up Deployment (optional)

1. In **Settings → Environments**, create an environment named `production` and add these secrets:

   | Secret               | Value                                                                      |
   |----------------------|----------------------------------------------------------------------------|
   | `DEPLOY_HOST`        | Hostname or IP of the Docker host                                          |
   | `DEPLOY_USER`        | SSH user on that host (must be able to run `docker`)                       |
   | `DEPLOY_SSH_KEY`     | Private key for that user (the public key goes in the host's `authorized_keys`) |
   | `DEPLOY_KNOWN_HOSTS` | Output of `ssh-keyscan -H <host>`, so the host key is verified             |

2. In **Settings → Secrets and variables → Actions → Variables**, add `DEPLOY_ENABLED` with the value `true`.

The Docker host needs Docker and `curl` installed. Port 8080 on the host must be open to whoever should reach the service.

## Push the Project to GitHub

1. Create an empty repository on GitHub (https://github.com/new). Do **not** add a README, `.gitignore`, or license, because this project already has them.
2. From this project folder, run:

```bash
git init
git add .
git commit -m "Initial commit: Flask app with Docker and GitHub Actions CI/CD"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

Replace `<your-username>` and `<your-repo-name>` with your own values. The push to `main` triggers the pipeline.

## Verify the Pipeline

1. Open your repository on GitHub.
2. Click the **Actions** tab.
3. Open the latest run of **CI/CD Pipeline**. A green check mark means every step passed.
4. Click the **build-test** job to see each step's output, including the `/health` response.

## Security Notes

- No secrets or credentials are stored in the code or the workflow.
- The Docker container runs as a non-root user.
- The base image is `python:3.12-slim` to keep the image small.
- The workflow uses `permissions: contents: read`, so it has only read access to the repository.
- Deployment credentials live in the `production` environment secrets, and the SSH key is deleted from the runner at the end of the job.
