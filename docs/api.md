# API Documentation

## Endpoints

### 1. Health Probe
* **URI**: `GET /health`
* **Response**:
```json
{
  "status": "healthy"
}
```

### 2. Evaluate Configurations
* **URI**: `POST /api/resources/evaluate`
* **Payload**:
```json
[
  {
    "provider": "AWS",
    "resource_type": "storage",
    "resource_id": "bucket-123",
    "resource_name": "customer-data",
    "configuration": {
      "encryption_enabled": false,
      "public_access": true,
      "logging_enabled": false
    }
  }
]
```
* **Response**:
```json
[
  {
    "resource_id": "bucket-123",
    "provider": "AWS",
    "resource_type": "storage",
    "status": "NON_COMPLIANT",
    "violations": [
      {
        "rule_id": "ENCRYPTION_REQUIRED",
        "severity": "HIGH",
        "message": "Resource encryption is disabled"
      }
    ]
  }
]
```

### 3. Get Compliance Violations
* **URI**: `GET /api/violations`
* **Response**:
```json
[
  {
    "resource_id": "bucket-123",
    "provider": "AWS",
    "resource_type": "storage",
    "rule_id": "ENCRYPTION_REQUIRED",
    "severity": "HIGH",
    "message": "Resource encryption is disabled"
  }
]
```

### 4. Get Compliance Summary
* **URI**: `GET /api/compliance/summary`
* **Response**:
```json
{
  "total_resources": 50,
  "compliant_resources": 35,
  "non_compliant_resources": 15,
  "compliance_percentage": 70.0,
  "critical": 0,
  "high": 10,
  "medium": 5,
  "low": 0
}
```
