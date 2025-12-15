from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_kms as kms,
    Duration
)
from constructs import Construct
from ...config import SoundDDEnvConfig

class DatabaseConstruct(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, config: SoundDDEnvConfig, kms_key: kms.Key, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.db_sg = ec2.SecurityGroup(
            self, "DBSecurityGroup", vpc=vpc, description="Allow inbound from App Layer"
        )
        self.db_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(5432))

        # RDS Instance (Postgres)
        self.db_instance = rds.DatabaseInstance(
            self, "SoundDD-Postgres",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16_1),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED), # Higher security
            
            # Enterprise Configurations
            instance_type=config.db_instance_type,
            multi_az=config.db_multi_az, # High Availability
            storage_encrypted=True,
            storage_encryption_key=kms_key,
            
            # Monitoring & Maintenance
            enable_performance_insights=True,
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT, # 7 days free
            auto_minor_version_upgrade=True,
            
            # Storage
            allocated_storage=20,
            max_allocated_storage=1000, # Auto-scale up to 1TB
            
            # Identity & Access
            credentials=rds.Credentials.from_generated_secret("postgres"), # Uses Secrets Manager automatically
            database_name="sound_dd_core",
            
            # Backup & Safety
            backup_retention=Duration.days(config.db_backup_retention_days),
            deletion_protection=config.enable_deletion_protection,
            removal_policy=config.removal_policy,
            security_groups=[self.db_sg]
        )

        if config.use_rds_proxy:
            self.db_proxy = rds.DatabaseProxy(
                self, "SoundDD-DBProxy",
                proxy_target=rds.ProxyTarget.from_instance(self.db_instance),
                secrets=[self.db_instance.secret],
                vpc=vpc,
                security_groups=[self.db_sg],
                debug_logging=False,
                require_tls=True
            )