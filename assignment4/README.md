# Say Hi API
This repository exists to serve as an example for the CD part of CI/CD.

### CI
- Push to `main` to run checks (pytest, mypy, pylint).
- Checks are scoped to `assignment4` in this monorepo.

### CD
- Merge and push to `prod` to trigger deploy.
- In repo settings, add the following GitHub Actions secrets:
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN`
  - `SERVER_HOST`
  - `SERVER_USER`
  - `SERVER_PORT` (optional, defaults to 22)
  - `SERVER_SSH_KEY` (new key pair for GitHub Actions only)
- Optional variable:
  - `DOCKER_IMAGE` (defaults to `mleng-sayhi`)

Deployment pulls your image and runs:
`docker run --name mleng-sayhi --rm -v /opt/assignment_outputs:/app/data <image>:latest`
