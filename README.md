# CloudCompliance Sentinel

CloudCompliance Sentinel is a lightweight, read-only multi-cloud compliance monitoring system designed for AWS and GCP. It evaluates cloud resource configurations against configurable policy rules to detect GDPR and HIPAA violations, displays compliance status on an interactive dashboard, and generates compliance reports.

---

## 🚀 Module Status: AWS Integration Complete

The **AWS Cloud Integration** module is fully implemented, tested, and documented. 

### Supported Resources
* **S3 Buckets**: Scans encryption status, public access block configurations, and audit logging.
* **RDS Databases**: Scans storage encryption, engine versions, public accessibility, and CloudWatch logging exports.
* **VPC Networks**: Scans CIDR blocks, states, defaults, and tag names.

### Key Features
* **Zero-Credential Demo Mode**: Automatically falls back to Demo Mode if credentials are not found, returning mock compliant/non-compliant AWS resources for demo videos or presentations.
* **Fail-Safe Processing**: Scans ignore individual bucket failures (e.g. AccessDenied on specific folders) to preserve partial scan outputs instead of crashing.
* **Abstract Interface**: Converts boto3 responses into a standard `ResourceModel` format consumed directly by the Compliance Engine.

---

## 🛠️ Project Structure
* **`backend/`**: FastAPI backend application with Compliance Engine and Database layers.
  * **`backend/run_aws_scan.py`**: Independent CLI utility to scan and output AWS resources.
* **`frontend/`**: Vite + React frontend dashboard.
* **`reports/`**: PDF/HTML compliance report generator module.
* **`demo/`**: Mock data, walkthrough scripts, and visuals.
* **`docs/`**: Detailed project documentation (Architecture, APIs, Rules, Setup).

---

## 💻 Running the AWS Scanner CLI

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the CLI tool:
   * **Demo/Mock Mode** (Run instantly with no credentials):
     ```bash
     python run_aws_scan.py --demo
     ```
   * **Real AWS Scan** (Scans actual cloud configurations using credentials in `.env`):
     ```bash
     python run_aws_scan.py --real
     ```

For full integration details and IAM permission policy checklist, refer to the [docs/aws-integration.md](docs/aws-integration.md) contract guide.