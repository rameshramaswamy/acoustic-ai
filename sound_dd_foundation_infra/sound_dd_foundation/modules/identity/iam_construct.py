from aws_cdk import (
    aws_iam as iam,
)
from constructs import Construct

class IdentityConstruct(Construct):
    def __init__(self, scope: Construct, id: str, raw_bucket_arn: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. IoT Ingestion Role (Least Privilege)
        # Allows devices to ONLY PutObject into the raw bucket
        self.iot_role = iam.Role(
            self, "IoTSensorRole",
            assumed_by=iam.ServicePrincipal("iot.amazonaws.com"),
            description="Role for Edge devices to upload audio"
        )
        
        self.iot_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:PutObject"],
            resources=[f"{raw_bucket_arn}/*"],
            effect=iam.Effect.ALLOW
        ))

        # 2. Researcher Read-Only Role
        self.researcher_group = iam.Group(
            self, "ResearcherGroup",
            group_name="SoundDD-Researchers"
        )
        
        # Researchers can read data but not delete it
        self.researcher_group.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject", "s3:ListBucket"],
            resources=[raw_bucket_arn, f"{raw_bucket_arn}/*"],
            effect=iam.Effect.ALLOW
        ))