import aioboto3
from botocore.exceptions import ClientError
from ..config import settings
import uuid
from datetime import datetime
import logging

logger = logging.getLogger("sound_dd.storage")

class StorageService:
    def __init__(self):
        self.session = aioboto3.Session()

    async def generate_presigned_post_async(self, device_id: str, file_type: str, checksum_md5: str = None) -> dict:
        """
        Generates S3 URL asynchronously.
        OPTIMIZATION: Added 'Checksum' enforcement. S3 will reject the upload 
        if the uploaded file doesn't match this hash.
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y/%m/%d')
        unique_id = str(uuid.uuid4())
        extension = "wav" if "wav" in file_type else "flac"
        object_key = f"raw/{date_str}/{device_id}/{unique_id}.{extension}"

        # Conditions
        conditions = [
            {'acl': 'private'},
            {'Content-Type': file_type},
            ['content-length-range', 100, 52428800]
        ]
        
        fields = {
            'acl': 'private', 
            'Content-Type': file_type
        }

        # Integrity Check Optimization
        if checksum_md5:
            conditions.append({'Content-MD5': checksum_md5})
            fields['Content-MD5'] = checksum_md5

        async with self.session.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        ) as s3:
            try:
                response = await s3.generate_presigned_post(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=object_key,
                    Fields=fields,
                    Conditions=conditions,
                    ExpiresIn=3600
                )
                return {"url": response['url'], "fields": response['fields'], "key": object_key}
            except ClientError as e:
                logger.error(f"Async S3 Error: {e}")
                raise Exception("Storage Infrastructure Error")

    async def check_file_exists_async(self, s3_key: str) -> bool:
        async with self.session.client('s3', region_name=settings.AWS_REGION) as s3:
            try:
                await s3.head_object(Bucket=settings.AWS_BUCKET_NAME, Key=s3_key)
                return True
            except ClientError:
                return False