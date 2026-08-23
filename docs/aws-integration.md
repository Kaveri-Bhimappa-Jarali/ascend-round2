# AWS Integration Contract & Setup Guide

This document describes the design, API usage, environment configurations, and integration interfaces for the **AWS Cloud Integration** module of CloudCompliance Sentinel.

---

## 1. Integration Flow

The module functions as a read-only discoverer that polls AWS, maps metadata, and yields normalized outputs:

```
    AWS Cloud Resources (S3, RDS, VPC)
                  │ (Official APIs)
                  ▼
         boto3 SDK Sessions
                  │ (Credentials / IAM Role)
                  ▼
      AWS Collectors (S3, RDS, VPC)
                  │ (Data Mapping)
                  ▼
    List of Normalized ResourceModels
                  │ (Saved to SQLite DB)
                  ▼
      Compliance Policies Evaluation
```

---

## 2. Environment Configurations

Configure environment settings in `backend/.env` (based on [backend/.env.example](file:///c:/Users/anupa/ascend-round2/backend/.env.example)):

### Real Cloud Mode
To scan actual cloud environments, supply active AWS credentials.
```ini
AWS_DEMO_MODE=False
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```
*Note: If no credentials are supplied, the collector automatically falls back to Demo Mode to prevent errors/crashes.*

### Demo / Simulation Mode
```ini
AWS_DEMO_MODE=True
```
In Demo Mode, the scanner bypasses boto3 and immediately returns 6 mock resources representing compliant and violating resources, all prefixed with `demo-` (e.g. `demo-aws-s3-unencrypted`).

---

## 3. Required IAM Read-Only Permissions

If using a real AWS account, the credentials must be attached to an IAM policy with at least the following read-only privileges:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ComplianceSentinelReadOnly",
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:GetEncryptionConfiguration",
                "s3:GetBucketLogging",
                "s3:GetBucketPublicAccessBlock",
                "rds:DescribeDBInstances",
                "ec2:DescribeVpcs"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 4. API Interface Contract (Output Format)

When calling `AWSCollector().collect_resources()`, the module returns a Python `List` of `ResourceModel` objects. The Compliance Engine can consume these records without needing any dependency on `boto3`.

### S3 Output Payload Schema
```json
{
  "provider": "AWS",
  "resource_type": "storage",
  "resource_id": "customer-invoices-2026",
  "resource_name": "customer-invoices-2026",
  "configuration": {
    "encryption_enabled": true,
    "public_access": false,
    "logging_enabled": true,
    "region": "us-east-1",
    "arn": "arn:aws:s3:::customer-invoices-2026"
  }
}
```

### RDS Output Payload Schema
```json
{
  "provider": "AWS",
  "resource_type": "database",
  "resource_id": "postgres-prod",
  "resource_name": "postgres-prod",
  "configuration": {
    "encryption_enabled": true,
    "public_access": false,
    "logging_enabled": true,
    "engine": "postgres",
    "engine_version": "14.5",
    "region": "us-west-2",
    "arn": "arn:aws:rds:us-west-2:123456789012:db:postgres-prod"
  }
}
```

### VPC Output Payload Schema
```json
{
  "provider": "AWS",
  "resource_type": "vpc",
  "resource_id": "vpc-0abc123def456",
  "resource_name": "production-network",
  "configuration": {
    "cidr_block": "10.0.0.0/16",
    "is_default": false,
    "state": "available",
    "region": "us-east-1",
    "encryption_enabled": true,
    "public_access": false,
    "logging_enabled": true
  }
}
```
