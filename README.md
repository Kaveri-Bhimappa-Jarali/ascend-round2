# CloudCompliance Sentinel

Repository: `ascend-round2`

CloudCompliance Sentinel is a lightweight FastAPI MVP for read-only multi-cloud compliance monitoring across AWS and GCP.

## Problem

Cloud teams need a quick way to spot basic security posture issues, such as unencrypted storage or publicly exposed buckets, without modifying infrastructure.

## Architecture

Cloud collection -> Normalization -> SQLite -> Compliance engine -> API -> Dashboard

Phase 1 establishes the application foundation. Compliance rules, demo scanning, and collectors are implemented in later phases.

## Features

- FastAPI application
- SQLite database foundation with SQLAlchemy models
- Basic API endpoints
- Server-rendered dashboard shell
- Read-only operating posture
- Environment-based configuration

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic
- HTML, CSS, vanilla JavaScript
- pytest

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Demo Mode

Set `DEMO_MODE=true` in `.env`. Demo resources and policy evaluation are planned for Phase 2.

## AWS Setup

AWS collection will use boto3 and standard AWS credential resolution. The application is designed to call read-only describe/get/list APIs only.

## GCP Setup

GCP collection will use the official Google Cloud Storage Python SDK and standard Google credential resolution.

## Running Application

```bash
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Running Tests

```bash
python -m pytest
```

## Compliance Rules

Rules will be loaded from `policies/policies.json` in Phase 2.

## API Endpoints

- `GET /`
- `GET /api/summary`
- `GET /api/resources`
- `GET /api/violations`
- `GET /api/providers`
- `POST /api/scan`

## Read-Only Guarantee

CloudCompliance Sentinel must never create, update, delete, or remediate cloud resources. Credentials are never stored in SQLite or exposed by API responses.

## Limitations

- Phase 1 contains placeholder API data.
- Compliance evaluation and scanning are not implemented yet.
- Real AWS/GCP collectors are not implemented yet.

## Future Enhancements

- Demo scan pipeline
- Policy engine
- AWS S3 and RDS collection
- GCP Cloud Storage collection
- Automatic 30-second scans
- Dashboard filtering and resource details
