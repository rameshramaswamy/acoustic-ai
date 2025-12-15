import aws_cdk as cdk
from constructs import Construct
from sound_dd_foundation_infra.sound_dd_foundation.modules.governance.budget_construct import BudgetConstruct
from .config import SoundDDEnvConfig
from .modules.networking.vpc_construct import NetworkingConstruct
from .modules.storage.s3_construct import StorageConstruct
from .modules.database.rds_construct import DatabaseConstruct
from .modules.identity.iam_construct import IdentityConstruct
from .modules.registry.ecr_construct import RegistryConstruct
from .modules.security.kms_construct import KMSConstruct

class SoundDDFoundationStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, config: SoundDDEnvConfig, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Apply Global Tags (Cost Allocation)
        cdk.Tags.of(self).add("Project", "SOUND-DD")
        cdk.Tags.of(self).add("Environment", config.env_name)
        cdk.Tags.of(self).add("CostCenter", "Research-AI-01")

        # 0. Security (KMS)
        security = KMSConstruct(self, "SecurityModule", env_name=config.env_name)

        # 1. Networking
        network = NetworkingConstruct(self, "NetworkModule", config=config)

        # 2. Storage
        storage = StorageConstruct(
            self, "StorageModule", 
            config=config, 
            kms_key=security.data_key
        )

        # 3. Database
        database = DatabaseConstruct(
            self, "DatabaseModule", 
            vpc=network.vpc, 
            config=config,
            kms_key=security.data_key
        )

        # 4. Identity
        identity = IdentityConstruct(
            self, "IdentityModule", 
            raw_bucket_arn=storage.raw_bucket.bucket_arn
        )

        # 5. Registry
        registry = RegistryConstruct(self, "RegistryModule")

        # Exports
        self.export_value(network.vpc.vpc_id, name="SoundDD-VpcId")
        self.export_value(storage.raw_bucket.bucket_name, name="SoundDD-RawBucket")
        self.export_value(security.data_key.key_arn, name="SoundDD-KMSKeyArn")
        self.export_value(
            database.db_instance.secret.secret_arn, 
            name="SoundDD-DBSecretArn"
        )

        # 6. Governance (Cost Controls)
        # Set budget: $50 for Dev, $1000 for Prod
        budget_limit = 1000 if config.env_name == "prod" else 50
        
        BudgetConstruct(
            self, "BudgetModule",
            amount=budget_limit,
            email="admin@sound-dd-platform.org" # Replace with valid email
        )