# CloudCompliance Sentinel

CloudCompliance Sentinel is a lightweight, read-only multi-cloud compliance monitoring system designed for AWS and GCP. It evaluates cloud resource configurations against configurable policy rules to detect GDPR and HIPAA violations, displays compliance status on an interactive dashboard, and generates compliance reports.

---

## 🚀 Module Status: AWS & GCP Integrations Complete

The **AWS Cloud Integration** and **GCP Cloud Integration** modules are fully implemented, tested, and documented.

### Supported AWS Resources
* **S3 Buckets**: Scans encryption status, public access block configurations, and audit logging.
* **RDS Databases**: Scans storage encryption, engine versions, public accessibility, and CloudWatch logging exports.
* **VPC Networks**: Scans CIDR blocks, states, defaults, and tag Names.

### Supported GCP Resources
* **GCS Storage Buckets**: Scans locations, CMEK configurations, uniform bucket-level access settings, and IAM-based public bindings.
* **Cloud SQL Databases**: Scans engine versions, SSL requirements, public IP settings, and database logging flags.
* **VPC Networks**: Scans routing modes, subnet counts, and auto-creation flags.

### Key Features
* **Zero-Credential Demo Mode**: Automatically falls back to Demo Mode if credentials are not found, returning mock compliant/non-compliant cloud resources for demo videos or presentations.
* **Fail-Safe Processing**: Scans ignore individual bucket or instance failures (e.g. AccessDenied on specific folders) to preserve partial scan outputs instead of crashing.
* **Abstract Interface**: Converts SDK/API responses into a standard `ResourceModel` format consumed directly by the Compliance Engine.

---

## 🛠️ Project Structure
* **`backend/`**: FastAPI backend application with Compliance Engine and Database layers.
  * **`backend/seed_demo_data.py`**: Seeder CLI to populate SQLite with sample AWS & GCP resources and export JSON report.
  * **`backend/run_all_scans.py`**: Combined CLI utility to scan and output both AWS and GCP resources.
  * **`backend/run_aws_scan.py`**: Independent CLI utility to scan and output AWS resources.
  * **`backend/run_gcp_scan.py`**: Independent CLI utility to scan and output GCP resources.
* **`frontend/`**: Vite + React frontend dashboard.
* **`reports/`**: JSON compliance report generator module (`JSONReportGenerator`).
* **`demo/`**: Mock data, walkthrough scripts, and visuals.
* **`docs/`**: Detailed project documentation (Architecture, APIs, Rules, Setup).


---

## 💻 Running the Scanner CLIs

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the CLI tools:
   * **Combined Scanner (Demo Mode)**:
     ```bash
     python run_all_scans.py --demo
     ```
   * **Combined Scanner (Real Scan)**:
     ```bash
     python run_all_scans.py --real
     ```
   * **AWS Scanner (Demo Mode)**:
     ```bash
     python run_aws_scan.py --demo
     ```
   * **AWS Scanner (Real Scan)**:
     ```bash
     python run_aws_scan.py --real
     ```
   * **GCP Scanner (Demo Mode)**:
     ```bash
     python run_gcp_scan.py --demo
     ```
   * **GCP Scanner (Real Scan)**:
     ```bash
     python run_gcp_scan.py --real
     ```

For full integration contracts and permissions check-lists, refer to:
* **AWS Integration Guide**: [docs/aws-integration.md](docs/aws-integration.md)
* **GCP Integration Guide**: [docs/gcp-integration.md](docs/gcp-integration.md)