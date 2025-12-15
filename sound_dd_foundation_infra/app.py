#!/usr/bin/env python3
import aws_cdk as cdk
from sound_dd_foundation.main_stack import SoundDDFoundationStack
from sound_dd_foundation.config import get_config

app = cdk.App()

# Fetch target environment from Context or Default
target_env = app.node.try_get_context("env") or "dev"
config = get_config(target_env)

SoundDDFoundationStack(
    app, 
    f"SoundDD-Foundation-{config.env_name.capitalize()}",
    config=config,
    env=cdk.Environment(account=config.aws_account, region=config.aws_region),
)

app.synth()