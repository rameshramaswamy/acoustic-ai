import pytest
from aws_cdk import App, Aspects
from aws_cdk.assertions import Template
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from sound_dd_foundation.main_stack import SoundDDFoundationStack
from sound_dd_foundation.config import PROD_CONFIG

@pytest.fixture
def stack_template():
    app = App()
    # Apply the Security Aspect to the entire app
    Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
    
    stack = SoundDDFoundationStack(
        app, "ProdStack", 
        config=PROD_CONFIG # Test against Prod config
    )
    
    # Example Suppression: If we really accept a risk (e.g., IAM policy wildcard for a specific limited scope)
    # NagSuppressions.add_resource_suppressions(...)
    
    return Template.from_stack(stack)

def test_compliance_no_public_s3(stack_template):
    # Verify S3 Block Public Access is globally enabled
    stack_template.has_resource_properties("AWS::S3::Bucket", {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True
        }
    })

def test_compliance_vpc_flow_logs(stack_template):
    # Ensure Flow Logs are attached to VPC
    stack_template.resource_count_is("AWS::EC2::FlowLog", 1)

def test_compliance_rds_storage_encrypted(stack_template):
    # Ensure DB storage encryption is mandatory
    stack_template.has_resource_properties("AWS::RDS::DBInstance", {
        "StorageEncrypted": True
    })