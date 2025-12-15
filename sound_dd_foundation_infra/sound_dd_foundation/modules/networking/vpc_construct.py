from aws_cdk import (
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct
from ...config import SoundDDEnvConfig

class NetworkingConstruct(Construct):
    def __init__(self, scope: Construct, id: str, config: SoundDDEnvConfig, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. VPC Creation
        self.vpc = ec2.Vpc(
            self, "SoundDD-VPC",
            vpc_name=f"SoundDD-{config.env_name}-VPC",
            ip_addresses=ec2.IpAddresses.cidr(config.vpc_cidr),
            max_azs=config.max_azs,
            nat_gateways=config.nat_gateways, # Configurable for HA
            subnet_configuration=[
                ec2.SubnetConfiguration(name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24),
                ec2.SubnetConfiguration(name="Private", subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, cidr_mask=24),
                ec2.SubnetConfiguration(name="Isolated", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, cidr_mask=28) # For Databases
            ]
        )
        self.vpc.add_gateway_endpoint(
            "S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3
        )

        self.vpc.add_gateway_endpoint(
            "DynamoDBEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB
        )
        self.vpc.add_interface_endpoint(
            "SSMEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM
        )
        
        self.vpc.add_interface_endpoint(
            "SSMMessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES
        )
        
        self.vpc.add_interface_endpoint(
            "EC2MessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES
        )

        # 2. VPC Flow Logs (Enterprise Requirement for Auditing)
        log_group = logs.LogGroup(
            self, "FlowLogGroup",
            log_group_name=f"/aws/vpc/sound-dd-{config.env_name}-flow",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=config.removal_policy
        )

        role = iam.Role(self, "FlowLogRole", assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"))
        
        ec2.FlowLog(
            self, "VPCFlowLog",
            resource_type=ec2.FlowLogResourceType.FROM_VPC,
            resource=self.vpc,
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group, role)
        )