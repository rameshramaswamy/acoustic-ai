import pytest
from observability.alert_rules import AlertGenerator

def test_alert_rules_format():
    """Verify generated alerts structure matches Prometheus spec."""
    output = AlertGenerator.generate_rules()
    
    assert "groups" in output
    assert len(output["groups"]) >= 2
    
    api_group = output["groups"][0]
    assert api_group["name"] == "sound-dd-api"
    assert len(api_group["rules"]) > 0
    
    # Check severity
    critical_rule = next(r for r in api_group["rules"] if r["alert"] == "HighErrorRate")
    assert critical_rule["labels"]["severity"] == "critical"