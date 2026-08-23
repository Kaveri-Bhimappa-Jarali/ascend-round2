# Demo and Validation Mode

Because actual API integrations require setup (credentials, project scopes), this system is built with a native Demo/Simulation Mode.

## Configuring Demo Mode

In `backend/.env` (and `backend/app/config/settings.py`), set:
```ini
DEMO_MODE=True
```

When `DEMO_MODE` is enabled, the mock databases will auto-seed with representative non-compliant and compliant storage, database, and network configurations from both AWS and GCP.

## Seed Resource Definitions

The seeder inserts:
1. **AWS S3 Bucket**: Compliant (Encrypted, public access disabled).
2. **AWS S3 Bucket**: Non-Compliant (Unencrypted, public access enabled - High Severity).
3. **AWS RDS Database**: Non-Compliant (Public access enabled, logging disabled).
4. **GCP Storage Bucket**: Compliant (Encrypted, logging enabled).
5. **GCP Storage Bucket**: Non-Compliant (Public access allowed).
6. **GCP Cloud SQL Database**: Non-Compliant (Encryption disabled).

## Running Demo Database Seeder CLI

Populate SQLite with sample multi-cloud resources and generate a JSON audit report:
```bash
python backend/seed_demo_data.py
```
Options:
- `--reset-demo`: Clear existing records before seeding.
- `--no-report`: Skip writing `compliance_report.json` file.

The JSON compliance report is automatically saved to `reports/generated/compliance_report.json` and accessible via `GET /api/reports/json`.
