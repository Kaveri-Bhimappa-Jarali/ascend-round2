# CloudCompliance Sentinel

CloudCompliance Sentinel is a lightweight, read-only multi-cloud compliance monitoring system designed for AWS and GCP. It evaluates cloud resource configurations against configurable policy rules to detect GDPR and HIPAA violations, displays compliance status on an interactive dashboard, and generates compliance reports.

---

## 🚀 Module Status: Fully Integrated and Demo-Ready (Auto-Fallback)

The **Compliance Engine**, **SQLite Database Layer**, **Backend REST APIs**, **PDF & JSON Reporting Engine**, and **AWS & GCP Cloud Integrations** are fully implemented, tested, and documented.

### Compliance & Backend Features
* **Configurable Compliance Engine**: Provider-agnostic policy evaluator supporting `equals` and `not_equals` operators across storage, database, and VPC resource types.
* **SQLite Persistence**: Relational storage for normalized resource configurations and compliance violations with foreign-key cascade enforcement and concurrency-safe savepoints.
* **PDF & JSON Audit Reporting**: Standardized JSON and PDF report generators compiling metadata, summary stats, severity counts, and resource violation logs. Reports can be fetched via API or downloaded directly via the UI.
* **REST APIs**: FastAPI endpoints for health probes, evaluations (`POST /api/resources/evaluate`), violations (`GET /api/violations`), compliance summary (`GET /api/compliance/summary`), JSON reports (`GET /api/reports/json`), and PDF reports (`GET /api/reports/pdf`).
* **Database Seeder CLI**: `seed_demo_data.py` populates SQLite with sample multi-cloud resources.
* **Automatic Demo Fallback**: If no active AWS or GCP credentials are found on the machine, the system **automatically falls back to interactive Demo/Mock mode**, allowing immediate evaluation of all features with a single click.

### Supported Cloud Resources
* **AWS S3 Buckets**: Scans encryption status, public access block configurations, and audit logging.
* **AWS RDS Databases**: Scans storage encryption, engine versions, public accessibility, and CloudWatch logging exports.
* **AWS VPC Networks**: Scans CIDR blocks, states, defaults, and tag Names.
* **GCP GCS Storage Buckets**: Scans locations, CMEK configurations, uniform bucket-level access settings, and IAM-based public bindings.
* **GCP Cloud SQL Databases**: Scans engine versions, SSL requirements, public IP settings, and database logging flags.
* **GCP VPC Networks**: Scans routing modes, subnet counts, and auto-creation flags.

---

## 🛠️ Project Structure
* **`backend/`**: FastAPI backend application with Compliance Engine, Database, and Reporting.
  * **`backend/seed_demo_data.py`**: Seeder CLI to populate SQLite with sample AWS & GCP resources and export JSON report.
  * **`backend/run_all_scans.py`**: Combined CLI utility to scan and output both AWS and GCP resources.
  * **`backend/run_aws_scan.py`**: Independent CLI utility to scan and output AWS resources.
  * **`backend/run_gcp_scan.py`**: Independent CLI utility to scan and output GCP resources.
* **`frontend/`**: Vite + React frontend dashboard featuring interactive layout, charts, and direct PDF report download trigger.
* **`reports/`**: JSON & PDF compliance report generator modules (`JSONReportGenerator`, `PDFReportGenerator`).
* **`demo/`**: Mock data, walkthrough scripts, and visuals.
* **`docs/`**: Detailed project documentation (Architecture, APIs, Rules, Setup).

---

## 💻 Running the Backend & CLIs

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the CLI tools:
   * **Database Seeder & JSON Report CLI**:
     ```bash
     python seed_demo_data.py --reset-demo
     ```
   * **Combined AWS & GCP Scanner (Demo Mode)**:
     ```bash
     python run_all_scans.py --demo
     ```
   * **AWS Scanner**:
     ```bash
     python run_aws_scan.py --demo
     ```
   * **GCP Scanner**:
     ```bash
     python run_gcp_scan.py --demo
     ```

4. Start the FastAPI Backend Server:
   ```bash
   uvicorn app.main:app --reload
   ```

For full integration contracts and permissions check-lists, refer to:
* **API Documentation**: [docs/api.md](docs/api.md)
* **Demo & Validation Guide**: [docs/demo.md](docs/demo.md)
* **AWS Integration Guide**: [docs/aws-integration.md](docs/aws-integration.md)
* **GCP Integration Guide**: [docs/gcp-integration.md](docs/gcp-integration.md)