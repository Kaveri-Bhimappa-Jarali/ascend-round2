"""
AWS client session and connection management helper.
"""
import os
import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

class AWSClient:
    """
    Manages centralized boto3 clients using environment variable configuration.
    """
    region_name: str = None

    def __init__(self, region_name: str = None, access_key: str = None, secret_key: str = None):
        self.region_name = region_name or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        self.access_key = access_key or os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_key = secret_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        self._session = None

    def get_session(self) -> boto3.Session:
        """
        Creates and returns a cached boto3.Session.
        """
        if self._session is not None:
            return self._session

        session_kwargs = {}
        if self.region_name:
            session_kwargs["region_name"] = self.region_name
        if self.access_key:
            session_kwargs["aws_access_key_id"] = self.access_key
        if self.secret_key:
            session_kwargs["aws_secret_access_key"] = self.secret_key

        try:
            self._session = boto3.Session(**session_kwargs)
            return self._session
        except Exception as e:
            logger.error("Failed to initialize boto3 Session. Check your credentials.")
            raise e

    def get_s3_client(self):
        """
        Returns S3 client.
        """
        return self.get_session().client("s3")

    def get_rds_client(self):
        """
        Returns RDS client.
        """
        return self.get_session().client("rds")

    def get_ec2_client(self):
        """
        Returns EC2/VPC client.
        """
        return self.get_session().client("ec2")
