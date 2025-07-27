import asyncio
import boto3
import hashlib
from botocore.exceptions import ClientError
from datetime import datetime

from config.env_variables import get_settings


class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=get_settings().AWS_ACCESS_KEY_ID,
            aws_secret_access_key=get_settings().AWS_SECRET_ACCESS_KEY,
            region_name=get_settings().AWS_REGION,
        )
        self.bucket_name = get_settings().S3_BUCKET_NAME

    def generate_s3_key(self, banner_name: str, platform: str) -> str:
        """Generate unique S3 key for banner"""
        timestamp = datetime.now().strftime("%Y/%m/%d")
        safe_name = "".join(
            c for c in banner_name if c.isalnum() or c in ("-", "_")
        ).lower()
        unique_id = hashlib.md5(
            f"{banner_name}{platform}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        return f"banners/{timestamp}/{platform}/{safe_name}_{unique_id}.png".replace(
            "//", "/"
        )

    async def upload_image(
        self, image_data: bytes, s3_key: str, content_type: str = "image/png"
    ) -> str:
        """Upload image to S3 asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=image_data,
                    ContentType=content_type,
                    CacheControl="max-age=31536000",
                    Metadata={
                        "uploaded_at": datetime.now().isoformat(),
                        "service": "banner-generator",
                    },
                ),
            )

            aws_region = get_settings().AWS_REGION

            url = f"https://{self.bucket_name}.s3.{aws_region}.amazonaws.com/{s3_key}"
            return url

        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")

    async def upload_byte(
        self, byte: bytes, name: str, platform: str = "Facebook"
    ) -> str:
        """
        upload single byte to S3
        Args:
            takes bytes as input
        Returns:
            returns URL of the S3 uploaded img

        """
        key = self.generate_s3_key(name, platform)

        return await self.upload_image(byte, key)

    async def delete_image(self, s3_key: str) -> bool:
        """Delete image from S3"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=self.bucket_name, Key=s3_key
                ),
            )
            return True
        except ClientError:
            return False
