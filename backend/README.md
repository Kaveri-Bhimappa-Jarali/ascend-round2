# Compliance Sentinel Backend

This is the FastAPI backend for CloudCompliance Sentinel. It hosts the REST API endpoints, compliance rules engine, and SQLite database repository layer.

## Setup Instructions

1. **Create Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/Scripts/activate # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings**:
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. **Run Application**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Package Overview

- **`app/api/`**: HTTP Request/Response routing and schemas.
- **`app/compliance/`**: Compliance engine, rules list, severity mapping, and policy standards.
- **`app/models/`**: Domain structures (e.g. normalized Cloud Resources).
- **`app/services/`**: Coordination of database operations and evaluation engine calls.
- **`app/collectors/`**: Interfaces and implementations for cloud config retrieval.
- **`app/database/`**: SQLite session initialization and table definitions.
- **`app/config/`**: Dynamic config handling.
