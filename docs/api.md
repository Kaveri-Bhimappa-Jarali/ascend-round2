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
  "total_violations": 15,
  "compliance_percentage": 70.0,
  "violations_by_severity": {
    "CRITICAL": 0,
    "HIGH": 10,
    "MEDIUM": 5,
    "LOW": 0
  }
}

```

### 5. Get JSON Compliance Audit Report
* **URI**: `GET /api/reports/json`
* **Note**: The `resources` and `violations` array lists in the example response below are abbreviated for documentation brevity.
* **Response**:
```json
{
  "metadata": {
    "report_id": "b74df4e1-1936-4cc1-99e6-9528823b1bfb",
    "schema_version": "1.0.0",
    "generated_at": "2026-08-23T05:18:13.823956+00:00",
    "environment": "production"
  },
  "summary": {
    "total_resources": 6,
    "compliant_resources": 2,
    "non_compliant_resources": 4,
    "total_violations": 7,
    "compliance_percentage": 33.33,
    "violations_by_severity": {
      "CRITICAL": 0,
      "HIGH": 5,
      "MEDIUM": 2,
      "LOW": 0
    }
  },
  "resources": [
    {
      "provider": "AWS",
      "resource_type": "storage",
      "resource_id": "demo-aws-s3-compliant",
      "resource_name": "aws-prod-data-bucket",
      "status": "COMPLIANT",
      "configuration": {
        "encryption_enabled": true,
        "logging_enabled": true,
        "public_access": false
      },
      "last_seen": "2026-08-23T05:18:13.740474"
    }
  ],
  "violations": [
    {
      "provider": "AWS",
      "resource_type": "storage",
      "resource_id": "demo-aws-s3-non-compliant",
      "resource_name": "aws-public-unencrypted-bucket",
      "rule_id": "ENCRYPTION_REQUIRED",
      "severity": "HIGH",
      "message": "Resource encryption is disabled",
      "status": "FAIL",
      "detected_at": "2026-08-23T05:18:13.760381"
    }
  ]
}
```


