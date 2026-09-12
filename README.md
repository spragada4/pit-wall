# Pit Wall

A CI/CD pipeline modeled on F1 race-weekend strategy: Free Practice (lint/test) → Qualifying (build/push) → Race Start (canary deploy) → Safety Car (automated rollback) → Podium (full rollout).

Built with FastAPI, Docker, and Jenkins.

## Status

**Working:**
- FastAPI service pulling live F1 standings from the Jolpica-F1 API (Ergast's successor)
- SQLite-backed data storage, containerized with Docker
- Jenkins pipeline: Lint → Test → Build → Push → Canary Deploy → Health Gate → Promote
- Automatic image publishing to GitHub Container Registry (ghcr.io)
- Automatic pipeline trigger on every push via GitHub webhook
- **Canary deploy with automated, health-check-gated rollback**: every new image is deployed alongside the running version first. If it fails its health check, the pipeline tears down the bad deploy and fails the build — production is never touched. Only a passing canary gets promoted.

**Not yet built:**
- A documented chaos demo: deliberately breaking a deploy to prove the rollback fires, with captured pipeline output
- Terraform for environment provisioning
- Basic observability (structured logs or Prometheus/Grafana)

## Architecture

```
GitHub push
  -> Jenkins webhook trigger
    -> Free Practice: Lint (flake8, in python:3.11-slim container)
    -> Free Practice: Test (pytest, in python:3.11-slim container)
    -> Build (docker build, tagged with git commit SHA)
    -> Push (docker push to ghcr.io/spragada4/pit-wall)
    -> Race Start: Canary Deploy (new image on port 8001, alongside prod on 8000)
    -> Safety Car: Health Gate (polls canary's /health up to 5x; on failure,
       tears down the canary and fails the build -- production untouched)
    -> Podium: Promote to Production (retires old prod + canary, promotes
       the new image to port 8000)
```

The Safety Car stage is the core safety mechanism: it's what makes a bad deploy a non-event instead of an outage.

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

Jenkins is configured with a webhook-triggered pipeline (`Jenkinsfile`) that runs on every push to `main`. Lint and test stages run in disposable `python:3.11-slim` Docker agents; build/push/deploy stages run against the host Docker daemon via the mounted Docker socket.

**Note on local networking:** because Jenkins itself runs inside a container, health checks against sibling containers use `host.docker.internal` rather than `localhost` — Jenkins' container and the deployed app container don't share a network namespace even though both run on the same Docker host.

## Roadmap

- [x] Canary deploy: route to the new version on a separate port first
- [x] Automated rollback: health-check-gated, tears down a failing canary before it ever reaches production
- [ ] Chaos demo: deliberately break the canary, capture and document the pipeline catching it
- [ ] Terraform for environment provisioning
- [ ] Basic observability (structured logs or Prometheus/Grafana)







