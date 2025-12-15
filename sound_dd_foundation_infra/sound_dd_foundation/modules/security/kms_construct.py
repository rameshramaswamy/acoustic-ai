from aws_cdk import (
    aws_kms as kms,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct

class KMSConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Central Key for Encrypting S3 Data and RDS
        self.data_key = kms.Key(
            self, "SoundDD-DataKey",
            description=f"Master Key for SoundDD {env_name} Data Encryption",
            enable_key_rotation=True, # Compliance requirement (rotates yearly)
            alias=f"alias/sound-dd/{env_name}/data-key",
            removal_policy=RemovalPolicy.RETAIN if env_name == "prod" else RemovalPolicy.DESTROY
        )