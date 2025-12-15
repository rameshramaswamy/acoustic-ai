from dataclasses import dataclass
from typing import List
from aws_cdk import aws_ec2 as ec2
from aws_cdk import RemovalPolicy

@dataclass
class SoundDDEnvConfig:
    env_name: str
    aws_account: str
    aws_region: str
    vpc_cidr: str
    max_azs: int
    nat_gateways: int
    db_instance_type: ec2.InstanceType
    db_multi_az: bool
    db_backup_retention_days: int
    removal_policy: RemovalPolicy
    enable_deletion_protection: bool
    use_rds_proxy: bool

# --- CONFIGURATIONS ---

DEV_CONFIG = SoundDDEnvConfig(
    env_name="dev",
    aws_account="123456789012", # Replace with Dev Account
    aws_region="us-east-1",
    vpc_cidr="10.0.0.0/16",
    max_azs=2,
    nat_gateways=1, # Save cost
    db_instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
    db_multi_az=False,
    db_backup_retention_days=7,
    removal_policy=RemovalPolicy.DESTROY, # Clean up easily
    enable_deletion_protection=False
    use_rds_proxy=False,
)

PROD_CONFIG = SoundDDEnvConfig(
    env_name="prod",
    aws_account="987654321098", # Replace with Prod Account
    aws_region="us-east-1",
    vpc_cidr="10.1.0.0/16",
    max_azs=3, # High Availability
    nat_gateways=3, # 1 per AZ for resilience
    db_instance_type=ec2.InstanceType.of(ec2.InstanceClass.M6G, ec2.InstanceSize.LARGE), # Enterprise Grade
    db_multi_az=True, # Failover support
    db_backup_retention_days=30,
    removal_policy=RemovalPolicy.RETAIN, # Never lose data
    enable_deletion_protection=True
    use_rds_proxy=True,
)

def get_config(env_name: str) -> SoundDDEnvConfig:
    return PROD_CONFIG if env_name == "prod" else DEV_CONFIG