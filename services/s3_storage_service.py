import boto3
from core.utils.logger import Logger


class S3StorageService:
    """Service responsible for storing and managing objects in AWS S3"""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "ap-south-1",
    ):
        self.s3_client = boto3.client(
            "s3",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.bucket_name = bucket_name

    def generate_s3():
        pass
