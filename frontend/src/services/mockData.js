/**
 * Mock data representing the backend API response payloads.
 * Used for demo purposes and fallback when the backend API is unavailable.
 */

export const mockComplianceSummary = {
  total_resources: 11,
  compliant_resources: 6,
  non_compliant_resources: 5,
  compliance_percentage: 54.5,
  critical: 0,
  high: 3,
  medium: 2,
  low: 0,
  providers: {
    AWS: {
      total: 6,
      compliant: 3,
      violations: 3,
      percentage: 50.0
    },
    GCP: {
      total: 5,
      compliant: 3,
      violations: 2,
      percentage: 60.0
    }
  }
};

export const mockViolations = [
  {
    resource_id: "demo-aws-s3-unencrypted",
    resource_name: "demo-aws-s3-unencrypted",
    provider: "AWS",
    resource_type: "storage",
    status: "NON_COMPLIANT",
    rule_id: "ENCRYPTION_REQUIRED",
    severity: "HIGH",
    message: "Resource encryption is disabled. SSE-S3 or KMS must be enabled on buckets hosting customer data.",
    detected_at: "2026-08-23T08:50:00Z",
    configuration: {
      encryption_enabled: false,
      public_access: false,
      logging_enabled: true,
      region: "us-east-1",
      arn: "arn:aws:s3:::demo-aws-s3-unencrypted"
    }
  },
  {
    resource_id: "demo-aws-s3-public",
    resource_name: "demo-aws-s3-public",
    provider: "AWS",
    resource_type: "storage",
    status: "NON_COMPLIANT",
    rule_id: "PUBLIC_EXPOSURE_FORBIDDEN",
    severity: "HIGH",
    message: "Public access block configuration is disabled. Objects in the bucket are exposed to the public internet.",
    detected_at: "2026-08-23T08:51:00Z",
    configuration: {
      encryption_enabled: true,
      public_access: true,
      logging_enabled: true,
      region: "us-east-1",
      arn: "arn:aws:s3:::demo-aws-s3-public"
    }
  },
  {
    resource_id: "demo-aws-rds-public",
    resource_name: "demo-aws-rds-public",
    provider: "AWS",
    resource_type: "database",
    status: "NON_COMPLIANT",
    rule_id: "PUBLIC_EXPOSURE_FORBIDDEN",
    severity: "HIGH",
    message: "RDS Database instance has publiclyAccessible set to True. DB should be configured in private subnets.",
    detected_at: "2026-08-23T08:52:00Z",
    configuration: {
      encryption_enabled: true,
      public_access: true,
      logging_enabled: false,
      engine: "mysql",
      engine_version: "8.0",
      region: "us-east-1",
      arn: "arn:aws:rds:us-east-1:123456789012:db:demo-aws-rds-public"
    }
  },
  {
    resource_id: "demo-gcp-storage-public",
    resource_name: "demo-gcp-storage-public",
    provider: "GCP",
    resource_type: "storage",
    status: "NON_COMPLIANT",
    rule_id: "PUBLIC_EXPOSURE_FORBIDDEN",
    severity: "HIGH",
    message: "GCS bucket IAM policy grants access to 'allUsers' or public access prevention is not enforced.",
    detected_at: "2026-08-23T08:53:00Z",
    configuration: {
      encryption_enabled: true,
      public_access: true,
      logging_enabled: false,
      region: "us-central1",
      arn: "gs://demo-gcp-storage-public"
    }
  },
  {
    resource_id: "demo-gcp-sql-public",
    resource_name: "demo-gcp-sql-public",
    provider: "GCP",
    resource_type: "database",
    status: "NON_COMPLIANT",
    rule_id: "PUBLIC_EXPOSURE_FORBIDDEN",
    severity: "HIGH",
    message: "Cloud SQL database instance has external public IP enabled, and SSL requireSsl enforcement is disabled.",
    detected_at: "2026-08-23T08:54:00Z",
    configuration: {
      encryption_enabled: true,
      public_access: true,
      logging_enabled: false,
      engine: "MYSQL_8_0",
      region: "us-central1",
      arn: "gcp:sqladmin:us-central1:demo-project:instances:demo-gcp-sql-public"
    }
  }
];

export const mockResourcesList = [
  // Compliant resources
  {
    resource_id: "demo-aws-s3-compliant",
    resource_name: "demo-aws-s3-compliant",
    provider: "AWS",
    resource_type: "storage",
    status: "COMPLIANT",
    configuration: {
      encryption_enabled: true,
      public_access: false,
      logging_enabled: true,
      region: "us-east-1",
      arn: "arn:aws:s3:::demo-aws-s3-compliant"
    }
  },
  {
    resource_id: "demo-aws-rds-compliant",
    resource_name: "demo-aws-rds-compliant",
    provider: "AWS",
    resource_type: "database",
    status: "COMPLIANT",
    configuration: {
      encryption_enabled: true,
      public_access: false,
      logging_enabled: true,
      engine: "postgres",
      engine_version: "14.5",
      region: "us-east-1",
      arn: "arn:aws:rds:us-east-1:123456789012:db:demo-aws-rds-compliant"
    }
  },
  {
    resource_id: "demo-aws-vpc-default",
    resource_name: "demo-aws-vpc-default",
    provider: "AWS",
    resource_type: "vpc",
    status: "COMPLIANT",
    configuration: {
      cidr_block: "172.31.0.0/16",
      is_default: true,
      state: "available",
      region: "us-east-1"
    }
  },
  {
    resource_id: "demo-gcp-storage-compliant",
    resource_name: "demo-gcp-storage-compliant",
    provider: "GCP",
    resource_type: "storage",
    status: "COMPLIANT",
    configuration: {
      encryption_enabled: true,
      public_access: false,
      logging_enabled: true,
      region: "us-central1",
      arn: "gs://demo-gcp-storage-compliant"
    }
  },
  {
    resource_id: "demo-gcp-sql-compliant",
    resource_name: "demo-gcp-sql-compliant",
    provider: "GCP",
    resource_type: "database",
    status: "COMPLIANT",
    configuration: {
      encryption_enabled: true,
      public_access: false,
      logging_enabled: true,
      engine: "POSTGRES_14",
      region: "us-central1",
      arn: "gcp:sqladmin:us-central1:demo-project:instances:demo-gcp-sql-compliant"
    }
  },
  {
    resource_id: "demo-gcp-vpc-default",
    resource_name: "demo-gcp-vpc-default",
    provider: "GCP",
    resource_type: "vpc",
    status: "COMPLIANT",
    configuration: {
      routing_mode: "regional",
      auto_create_subnetworks: true,
      subnets_count: 4,
      region: "global"
    }
  }
];
