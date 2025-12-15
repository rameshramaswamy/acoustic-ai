from aws_cdk import (
    aws_s3 as s3,
    aws_kms as kms,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct
from ...config import SoundDDEnvConfig

class StorageConstruct(Construct):
    def __init__(self, scope: Construct, id: str, config: SoundDDEnvConfig, kms_key: kms.Key, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. Access Logging Bucket (Compliance)
        self.log_bucket = s3.Bucket(
            self, "AccessLogBucket",
            bucket_name=f"sound-dd-{config.env_name}-logs-{config.aws_account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=config.removal_policy,
            lifecycle_rules=[s3.LifecycleRule(expiration=Duration.days(90))]
        )

        # 2. Raw Audio Data Lake
        self.raw_bucket = s3.Bucket(
            self, "RawAudioBucket",
            bucket_name=f"sound-dd-{config.env_name}-raw-{config.aws_account}",
            versioned=True,
            encryption=s3.BucketEncryption.KMS, # Enterprise Encryption
            encryption_key=kms_key,
            server_access_logs_bucket=self.log_bucket, # Traceability
            server_access_logs_prefix="raw-audio-logs/",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True, # Security Best Practice
            removal_policy=config.removal_policy,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="IntelligentTiering",
                    status=s3.LifecycleRuleStatus.ENABLED,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                            transition_after=Duration.days(0) # Move immediately to auto-tiering
                        )
                    ]
                ),
                s3.LifecycleRule(
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                    enabled=True,
                    id="AbortFailedUploads"
                )
            ]
        )