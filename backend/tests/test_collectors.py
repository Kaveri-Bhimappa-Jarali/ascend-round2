"""
Unit tests for cloud collector interfaces and normalizations.
"""
from unittest.mock import MagicMock, patch
import pytest
from botocore.exceptions import ClientError

from app.collectors.aws.client import AWSClient
from app.collectors.aws.s3 import S3Collector
from app.collectors.aws.rds import RDSCollector
from app.collectors.aws.vpc import VPCCollector
from app.collectors.aws import AWSCollector

# ----------------------------------------------------
# 1. AWS Client Tests
# ----------------------------------------------------
@patch("app.collectors.aws.client.boto3.Session")
def test_aws_client_session_initialization(mock_session_class):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    client = AWSClient(region_name="us-west-2", access_key="test-key", secret_key="test-secret")
    session = client.get_session()

    mock_session_class.assert_called_once_with(
        region_name="us-west-2",
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret"
    )
    assert session == mock_session

# ----------------------------------------------------
# 2. S3 Collector Tests
# ----------------------------------------------------
def test_s3_collector_compliant_bucket():
    mock_client = MagicMock()
    mock_aws_client = MagicMock(spec=AWSClient)
    mock_aws_client.get_s3_client.return_value = mock_client

    # Configure return values for S3 API calls
    mock_client.list_buckets.return_value = {
        "Buckets": [{"Name": "compliant-bucket-1"}]
    }
    mock_client.get_bucket_location.return_value = {"LocationConstraint": "us-west-2"}
    mock_client.get_bucket_encryption.return_value = {
        "ServerSideEncryptionConfiguration": {
            "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
        }
    }
    mock_client.get_public_access_block.return_value = {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    }
    mock_client.get_bucket_logging.return_value = {
        "LoggingEnabled": {"TargetBucket": "log-bucket", "TargetPrefix": "logs/"}
    }

    collector = S3Collector(aws_client=mock_aws_client)
    resources = collector.collect_resources()

    assert len(resources) == 1
    res = resources[0]
    assert res.provider == "AWS"
    assert res.resource_type == "storage"
    assert res.resource_id == "compliant-bucket-1"
    assert res.configuration["encryption_enabled"] is True
    assert res.configuration["public_access"] is False
    assert res.configuration["logging_enabled"] is True
    assert res.configuration["region"] == "us-west-2"


def test_s3_collector_non_compliant_bucket():
    mock_client = MagicMock()
    mock_aws_client = MagicMock(spec=AWSClient)
    mock_aws_client.get_s3_client.return_value = mock_client

    mock_client.list_buckets.return_value = {
        "Buckets": [{"Name": "unencrypted-public-bucket"}]
    }
    mock_client.get_bucket_location.return_value = {"LocationConstraint": None} # Defaults to us-east-1

    # Simulate encryption configuration not found
    mock_client.get_bucket_encryption.side_effect = ClientError(
        {"Error": {"Code": "ServerSideEncryptionConfigurationNotFoundError", "Message": "Not found"}},
        "GetBucketEncryption"
    )
    # Simulate public access block missing (NoSuchPublicAccessBlockConfiguration)
    mock_client.get_public_access_block.side_effect = ClientError(
        {"Error": {"Code": "NoSuchPublicAccessBlockConfiguration", "Message": "Not found"}},
        "GetPublicAccessBlock"
    )
    # Simulate logging disabled (returns empty response or ClientError)
    mock_client.get_bucket_logging.return_value = {}

    collector = S3Collector(aws_client=mock_aws_client)
    resources = collector.collect_resources()

    assert len(resources) == 1
    res = resources[0]
    assert res.resource_id == "unencrypted-public-bucket"
    assert res.configuration["encryption_enabled"] is False
    assert res.configuration["public_access"] is True
    assert res.configuration["logging_enabled"] is False
    assert res.configuration["region"] == "us-east-1"


def test_s3_collector_bucket_level_error_tolerance():
    mock_client = MagicMock()
    mock_aws_client = MagicMock(spec=AWSClient)
    mock_aws_client.get_s3_client.return_value = mock_client

    mock_client.list_buckets.return_value = {
        "Buckets": [
            {"Name": "forbidden-bucket"},
            {"Name": "accessible-bucket"}
        ]
    }

    # First bucket fails location but continues, then raises unexpected exception during encryption check
    mock_client.get_bucket_location.side_effect = [
        ClientError({"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}, "GetBucketLocation"),
        {"LocationConstraint": "us-east-1"}
    ]
    # Raise unexpected exception on first bucket, succeed on second bucket
    mock_client.get_bucket_encryption.side_effect = [
        RuntimeError("Unexpected API failure"),
        {}
    ]
    
    # Configure returns for the second bucket
    mock_client.get_public_access_block.return_value = {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True, "IgnorePublicAcls": True,
            "BlockPublicPolicy": True, "RestrictPublicBuckets": True
        }
    }
    mock_client.get_bucket_logging.return_value = {}

    collector = S3Collector(aws_client=mock_aws_client)
    resources = collector.collect_resources()

    # The scanner should not fail entirely; it should log the first error and successfully scan the second bucket.
    assert len(resources) == 1
    assert resources[0].resource_id == "accessible-bucket"

# ----------------------------------------------------
# 3. RDS Collector Tests
# ----------------------------------------------------
def test_rds_collector():
    mock_client = MagicMock()
    mock_aws_client = MagicMock(spec=AWSClient)
    mock_aws_client.region_name = "us-east-1"
    mock_aws_client.get_rds_client.return_value = mock_client

    mock_client.describe_db_instances.return_value = {
        "DBInstances": [
            {
                "DBInstanceIdentifier": "prod-db",
                "DBInstanceArn": "arn:aws:rds:us-east-1:123456789012:db:prod-db",
                "StorageEncrypted": True,
                "PubliclyAccessible": False,
                "EnabledCloudwatchLogsExports": ["error", "audit"],
                "Engine": "postgres",
                "EngineVersion": "14.5"
            },
            {
                "DBInstanceIdentifier": "dev-db",
                "DBInstanceArn": "arn:aws:rds:us-west-2:123456789012:db:dev-db",
                "StorageEncrypted": False,
                "PubliclyAccessible": True,
                "EnabledCloudwatchLogsExports": [],
                "Engine": "mysql",
                "EngineVersion": "8.0"
            }
        ]
    }

    collector = RDSCollector(aws_client=mock_aws_client)
    resources = collector.collect_resources()

    assert len(resources) == 2
    
    # Assert prod-db details
    prod = next(r for r in resources if r.resource_id == "prod-db")
    assert prod.configuration["encryption_enabled"] is True
    assert prod.configuration["public_access"] is False
    assert prod.configuration["logging_enabled"] is True
    assert prod.configuration["region"] == "us-east-1"
    
    # Assert dev-db details
    dev = next(r for r in resources if r.resource_id == "dev-db")
    assert dev.configuration["encryption_enabled"] is False
    assert dev.configuration["public_access"] is True
    assert dev.configuration["logging_enabled"] is False
    assert dev.configuration["region"] == "us-west-2"

# ----------------------------------------------------
# 4. VPC Collector Tests
# ----------------------------------------------------
def test_vpc_collector():
    mock_client = MagicMock()
    mock_aws_client = MagicMock(spec=AWSClient)
    mock_aws_client.region_name = "us-east-1"
    mock_aws_client.get_ec2_client.return_value = mock_client

    mock_client.describe_vpcs.return_value = {
        "Vpcs": [
            {
                "VpcId": "vpc-0123456",
                "CidrBlock": "10.0.0.0/16",
                "IsDefault": False,
                "State": "available",
                "Tags": [{"Key": "Name", "Value": "prod-vpc"}]
            }
        ]
    }

    collector = VPCCollector(aws_client=mock_aws_client)
    resources = collector.collect_resources()

    assert len(resources) == 1
    vpc = resources[0]
    assert vpc.resource_id == "vpc-0123456"
    assert vpc.resource_name == "prod-vpc"
    assert vpc.configuration["cidr_block"] == "10.0.0.0/16"
    assert vpc.configuration["is_default"] is False
    assert vpc.configuration["state"] == "available"

# ----------------------------------------------------
# 5. AWSCollector (Demo Mode) Tests
# ----------------------------------------------------
def test_aws_collector_demo_mode():
    collector = AWSCollector(demo_mode=True)
    resources = collector.collect_resources()

    # Verify demo assets exist and are clearly identified
    assert len(resources) == 6
    for r in resources:
        assert r.provider == "AWS"
        assert r.resource_id.startswith("demo-")


# ====================================================
# GCP COLLECTORS TESTS
# ====================================================
from app.collectors.gcp.client import GCPClient
from app.collectors.gcp.storage import StorageCollector as GCPStorageCollector
from app.collectors.gcp.cloud_sql import CloudSQLCollector as GCPCloudSQLCollector
from app.collectors.gcp.vpc import VPCCollector as GCPVPCCollector
from app.collectors.gcp import GCPCollector

# ----------------------------------------------------
# 1. GCS Storage Collector Tests
# ----------------------------------------------------
def test_gcs_collector_compliant_bucket():
    mock_client = MagicMock()
    mock_gcp_client = MagicMock(spec=GCPClient)
    mock_gcp_client.get_storage_client.return_value = mock_client
    mock_gcp_client.project_id = "test-project"

    mock_bucket = MagicMock()
    mock_bucket.name = "compliant-bucket"
    mock_bucket.location = "US-CENTRAL1"
    mock_bucket.iam_configuration.public_access_prevention = "enforced"
    mock_bucket.logging = {"logBucket": "logs-bucket"}
    mock_client.list_buckets.return_value = [mock_bucket]

    collector = GCPStorageCollector(gcp_client=mock_gcp_client)
    resources = collector.collect_resources()

    assert len(resources) == 1
    res = resources[0]
    assert res.provider == "GCP"
    assert res.resource_type == "storage"
    assert res.resource_id == "compliant-bucket"
    assert res.configuration["encryption_enabled"] is True
    assert res.configuration["public_access"] is False
    assert res.configuration["logging_enabled"] is True
    assert res.configuration["region"] == "us-central1"


def test_gcs_collector_non_compliant_bucket():
    mock_client = MagicMock()
    mock_gcp_client = MagicMock(spec=GCPClient)
    mock_gcp_client.get_storage_client.return_value = mock_client
    mock_gcp_client.project_id = "test-project"

    mock_bucket = MagicMock()
    mock_bucket.name = "public-bucket"
    mock_bucket.location = "US"
    mock_bucket.iam_configuration.public_access_prevention = "inherited"
    mock_bucket.logging = None
    
    # Mock IAM policy bindings for public access check
    mock_policy = MagicMock()
    mock_binding = {"members": ["allUsers"], "role": "roles/storage.objectViewer"}
    mock_policy.bindings = [mock_binding]
    mock_bucket.get_iam_policy.return_value = mock_policy
    
    mock_client.list_buckets.return_value = [mock_bucket]

    collector = GCPStorageCollector(gcp_client=mock_gcp_client)
    resources = collector.collect_resources()

    assert len(resources) == 1
    res = resources[0]
    assert res.resource_id == "public-bucket"
    assert res.configuration["public_access"] is True
    assert res.configuration["logging_enabled"] is False


# ----------------------------------------------------
# 2. Cloud SQL Collector Tests
# ----------------------------------------------------
def test_gcp_cloud_sql_collector():
    mock_service = MagicMock()
    mock_gcp_client = MagicMock(spec=GCPClient)
    mock_gcp_client.get_sql_service.return_value = mock_service
    mock_gcp_client.project_id = "test-project"

    mock_instance = {
        "name": "sql-db",
        "databaseVersion": "POSTGRES_14",
        "region": "us-central1",
        "settings": {
            "ipConfiguration": {
                "ipv4Enabled": True,
                "requireSsl": True
            },
            "databaseFlags": [
                {"name": "log_connections", "value": "on"}
            ]
        }
    }
    
    mock_service.instances.return_value.list.return_value.execute.return_value = {
        "items": [mock_instance]
    }

    collector = GCPCloudSQLCollector(gcp_client=mock_gcp_client)
    resources = collector.collect_resources()

    assert len(resources) == 1
    res = resources[0]
    assert res.provider == "GCP"
    assert res.resource_type == "database"
    assert res.resource_id == "sql-db"
    assert res.configuration["encryption_enabled"] is True
    assert res.configuration["public_access"] is True
    assert res.configuration["logging_enabled"] is True


# ----------------------------------------------------
# 3. GCP VPC Collector Tests
# ----------------------------------------------------
def test_gcp_vpc_collector():
    mock_service = MagicMock()
    mock_gcp_client = MagicMock(spec=GCPClient)
    mock_gcp_client.get_compute_service.return_value = mock_service
    mock_gcp_client.project_id = "test-project"

    mock_network = {
        "id": 987654321,
        "name": "custom-vpc",
        "routingConfig": {
            "routingMode": "GLOBAL"
        },
        "autoCreateSubnetworks": False,
        "subnetworks": ["subnet-url-1", "subnet-url-2"]
    }
    
    mock_service.networks.return_value.list.return_value.execute.return_value = {
        "items": [mock_network]
    }

    collector = GCPVPCCollector(gcp_client=mock_gcp_client)
    resources = collector.collect_resources()

    assert len(resources) == 1
    res = resources[0]
    assert res.provider == "GCP"
    assert res.resource_type == "vpc"
    assert res.resource_id == "987654321"
    assert res.configuration["routing_mode"] == "global"
    assert res.configuration["auto_create_subnetworks"] is False
    assert res.configuration["subnets_count"] == 2


# ----------------------------------------------------
# 4. GCPCollector (Demo Mode) Tests
# ----------------------------------------------------
def test_gcp_collector_demo_mode():
    collector = GCPCollector(demo_mode=True)
    resources = collector.collect_resources()

    assert len(resources) == 5
    for r in resources:
        assert r.provider == "GCP"
        assert r.resource_id.startswith("demo-gcp-")

