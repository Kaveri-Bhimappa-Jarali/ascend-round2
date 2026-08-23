# Demo Walkthrough Script

Follow these steps to demonstrate CloudCompliance Sentinel:

## 1. Setup & Seeding Phase
1. Make sure you have python virtual environment set up and node dependencies installed.
2. Run demo database seeder to populate SQLite and export JSON report:
   ```bash
   python backend/seed_demo_data.py --reset-demo
   ```
3. Start the backend app server.

## 2. API & Reporting Validation
1. Make a request to `GET /health` to confirm server status.
2. Request `GET /api/compliance/summary` to view aggregate percentages and severity breakdown.
3. Request `GET /api/reports/json` to fetch the complete structured compliance audit report.
4. Verify exported file at `reports/generated/compliance_report.json`.

## 3. UI Verification
1. Launch the React dashboard interface.
2. Observe overall compliance percentage indicator.
3. Filter resources by cloud provider (AWS/GCP) or severity.

