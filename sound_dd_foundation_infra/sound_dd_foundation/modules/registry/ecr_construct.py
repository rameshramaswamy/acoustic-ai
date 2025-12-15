from aws_cdk import (
    aws_ecr as ecr,
    RemovalPolicy
)
from constructs import Construct

class RegistryConstruct(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Repo for the ML Model (CNNLeaf)
        self.ml_repo = ecr.Repository(
            self, "CNNLeafRepo",
            repository_name="sound-dd/cnn-leaf",
            image_scan_on_push=True, # Security requirement
            image_tag_mutability=ecr.TagMutability.IMMUTABLE,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                ecr.LifecycleRule(max_image_count=10) # Keep last 10 versions
            ]
        )

        # Repo for the API Backend
        self.api_repo = ecr.Repository(
            self, "BackendRepo",
            repository_name="sound-dd/backend-api",
            image_scan_on_push=True
        )