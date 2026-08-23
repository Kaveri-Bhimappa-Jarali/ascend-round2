# CloudCompliance Sentinel

CloudCompliance Sentinel is a lightweight, read-only multi-cloud compliance monitoring system designed for AWS and GCP. It evaluates cloud resource configurations against configurable policy rules to detect GDPR and HIPAA violations, displays compliance status on an interactive dashboard, and generates compliance reports.

## Key Features
* **Multi-Cloud Collection**: Modular design with dedicated AWS and GCP collector interfaces.
* **Compliance Rules Engine**: Flexible rules mapping to GDPR/HIPAA standards.
* **Local Storage**: Stores configurations and compliance checks locally using SQLite.
* **Interactive Dashboard**: Modern user interface to view compliance metrics.
* **Reporting**: Generates summary compliance reports.

## Project Structure
* **`backend/`**: FastAPI backend application with Compliance Engine and Database layers.
* **`frontend/`**: Vite + React frontend dashboard.
* **`reports/`**: PDF/HTML compliance report generator module.
* **`demo/`**: Mock data, walkthrough script, and visuals.
* **`docs/`**: Detailed project documentation (Architecture, APIs, Rules, Setup).

## Getting Started
Please refer to [docs/setup.md](docs/setup.md) for detailed instructions on installing and running both the backend and frontend modules locally.