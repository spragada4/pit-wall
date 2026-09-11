# Pit Wall

A CI/CD pipeline modeled on F1 race-weekend strategy: Free Practice (lint/test) → Qualifying (staging) → Race Start (canary deploy) → Safety Car (automated rollback) → Podium (full rollout).

Built with FastAPI, Docker, and Jenkins.

## Status

**Working:**
- FastAPI service pulling live F1 standings from the Jolpica-F1 API (Ergast's successor)
- SQLite-backed data storage, containerized with Docker
- 5-stage Jenkins pipeline: Lint → Test → Build → Push → Deploy
- Automatic image publishing to GitHub Container Registry (ghcr.io)
- Automatic pipeline trigger on every push via GitHub webhook

**Not yet built:**
- Canary deployment with automated rollback ("Safety Car" logic)
- Chaos-injection demo and incident writeup

## Architecture

```
GitHub push
  -> Jenkins webhook trigger
    -> Lint (flake8, in python:3.11-slim container)
    -> Test (pytest, in python:3.11-slim container)
    -> Build (docker build, tagged with git commit SHA)
    -> Push (docker push to ghcr.io/spragada4/pit-wall)
    -> Deploy (docker run, replaces running container)
```

## API

- `GET /health` — health check
- `GET /standings/{season}` — driver standings for a season (`current` for latest)
- `POST /refresh/{season}` — force a refresh from the Jolpica-F1 API

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Running in Docker

```bash
docker compose up --build
```

## CI/CD

Jenkins is configured with a webhook-triggered pipeline (`Jenkinsfile`) that runs on every push to `main`. See the Jenkinsfile for full stage definitions.

## Roadmap

- [ ] Canary deploy: route a fraction of traffic to the new version first
- [ ] Automated rollback: health-check-gated, reverts to previous image on failure
- [ ] Chaos demo: deliberately break the canary, document the pipeline catching it
- [ ] Terraform for environment provisioning
- [ ] Basic observability (structured logs or Prometheus/Grafana)
