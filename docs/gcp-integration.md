# GCP Integration Contract & Setup Guide

This document describes the design, setup, environment configurations, and integration interfaces for the **GCP Cloud Integration** module of CloudCompliance Sentinel.

---

## 1. Credentials and Settings

Configure environment variables in your `backend/.env` file:

### Real Cloud Mode
To scan an actual Google Cloud project, ensure `GCP_DEMO_MODE=False` and supply credential configs:
```ini
GCP_DEMO_MODE=False
GCP_DEFAULT_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
```
*Note: Service Account files must contain the credentials key. If `GOOGLE_APPLICATION_CREDENTIALS` is not set or auth parameters are missing, the collector automatically falls back to Demo Mode to prevent system crashes.*

### Demo Mode
```ini
GCP_DEMO_MODE=True
```
When GCP Demo Mode is active, the scanner immediately returns 5 pre-configured mock resources representing standard compliant and violating storage, SQL, and network setups. All demo resources are prefixed with `demo-gcp-`.

---

## 2. Required IAM Read-Only Permissions

If scanning a live GCP project, the service account or User account must be granted the following IAM roles at the project level:

1. **Storage Object Viewer (`roles/storage.objectViewer`)** or **Storage Admin (Read-only)**:
   - Required to list buckets and retrieve IAM policies.
2. **Cloud SQL Viewer (`roles/cloudsql.viewer`)**:
   - Required to list database instances and review SSL configurations.
3. **Compute Network Viewer (`roles/compute.networkViewer`)**:
   - Required to list networks and subnets.

Specifically, the following underlying API permissions are utilized:
* `storage.buckets.list` & `storage.buckets.get` & `storage.buckets.getIamPolicy`
* `cloudsql.instances.list` & `cloudsql.instances.get`
* `compute.networks.list` & `compute.networks.get`

---

## 3. Normalized GCP Output Contract

When calling `GCPCollector().collect_resources()`, the Compliance Engine receives a Python `List` of standard `ResourceModel` structures:

### GCS Bucket Output Payload
```json
{
  "provider": "GCP",
  "resource_type": "storage",
  "resource_id": "customer-uploads-bucket",
  "resource_name": "customer-uploads-bucket",
  "configuration": {
    "encryption_enabled": true,
    "public_access": false,
    "logging_enabled": true,
    "region": "us-central1",
    "arn": "gs://customer-uploads-bucket"
  }
}
```

### Cloud SQL Instance Output Payload
```json
{
  "provider": "GCP",
  "resource_type": "database",
  "resource_id": "mysql-db-replica",
  "resource_name": "mysql-db-replica",
  "configuration": {
    "encryption_enabled": true,
    "public_access": true,
    "logging_enabled": false,
    "engine": "MYSQL_8_0",
    "region": "europe-west3",
    "arn": "gcp:sqladmin:europe-west3:my-project:instances:mysql-db-replica"
  }
}
```

### VPC Network Output Payload
```json
{
  "provider": "GCP",
  "resource_type": "vpc",
  "resource_id": "9876543210",
  "resource_name": "custom-vpc-network",
  "configuration": {
    "routing_mode": "global",
    "auto_create_subnetworks": false,
    "subnets_count": 5,
    "region": "global",
    "encryption_enabled": true,
    "public_access": false,
    "logging_enabled": true
  }
}
```

---

## 4. Integration with Compliance Engine

The scanner exports standard domain structures that match the AWS outputs, keeping the Compliance Engine decoupled from the Google Cloud SDK:

```python
from app.collectors.gcp import GCPCollector

# Scans GCP resources (Returns List[ResourceModel])
gcp_resources = GCPCollector().collect_resources()

# Evaluate directly via the Compliance Engine
for resource in gcp_resources:
    result = compliance_engine.evaluate(resource)
```
