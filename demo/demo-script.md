# Demo Walkthrough Script

Follow these steps to demonstrate the CloudCompliance Sentinel:

## 1. Setup Phase
1. Make sure you have python virtual environment set up and node dependencies installed.
2. Initialize backend in demo mode (`DEMO_MODE=True`).
3. Start the backend app server.

## 2. API Validation
1. Make a request to `GET /health` to confirm server status.
2. Send evaluate trigger using sample JSON.
3. Review evaluations and active violations.

## 3. UI Verification
1. Launch the React dashboard interface.
2. Observe overall compliance percentage indicator.
3. Filter resources by cloud provider (AWS/GCP) or severity.
