import yaml

class AlertGenerator:
    """
    Generates Prometheus AlertManager Rules.
    Defines thresholds for Critical Enterprise Events.
    """
    
    @staticmethod
    def generate_rules():
        groups = []
        
        # Group 1: API Health
        api_rules = [
            {
                "alert": "HighErrorRate",
                "expr": 'rate(http_requests_total{status=~"5.."}[5m]) > 1',
                "for": "2m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "API Error Rate High",
                    "description": "More than 1 error per second in Ingestion API."
                }
            },
            {
                "alert": "SlowResponseTime",
                "expr": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0',
                "for": "5m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "API Latency High",
                    "description": "95th percentile latency is > 1 second."
                }
            }
        ]
        
        # Group 2: IoT Device Health
        iot_rules = [
            {
                "alert": "MassSensorDropoff",
                "expr": 'sum(sound_dd_connected_sensors) < 50', # Assuming 100 is baseline
                "for": "10m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "Mass Sensor Disconnection",
                    "description": "Active sensors dropped below 50%. Check Network/Power."
                }
            }
        ]

        groups.append({"name": "sound-dd-api", "rules": api_rules})
        groups.append({"name": "sound-dd-iot", "rules": iot_rules})
        
        return {"groups": groups}

    @staticmethod
    def export_to_yaml(filename="prometheus_alerts.yml"):
        rules = AlertGenerator.generate_rules()
        with open(filename, 'w') as f:
            yaml.dump(rules, f, sort_keys=False)
        print(f"✅ Alerts exported to {filename}")

if __name__ == "__main__":
    AlertGenerator.export_to_yaml()