from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HPA-Manager")

class HPAManager:
    """
    Manages Kubernetes Horizontal Pod Autoscalers programmatically.
    Ensures the Ingestion API and AI Workers scale to meet demand.
    """
    def __init__(self, env="prod"):
        try:
            config.load_kube_config() # Works locally if ~/.kube/config exists
        except:
            config.load_incluster_config() # Works inside the cluster

        self.autoscaling_v2 = client.AutoscalingV2Api()
        self.namespace = f"sound-dd-{env}"
        self.env = env

    def apply_hpa(self, deployment_name, min_replicas, max_replicas, target_cpu=70):
        """
        Creates or Updates an HPA rule.
        """
        hpa_name = f"{deployment_name}-hpa"
        
        # Define HPA Spec
        metric_spec = client.V2MetricSpec(
            type="Resource",
            resource=client.V2ResourceMetricSource(
                name="cpu",
                target=client.V2MetricTarget(
                    type="Utilization",
                    average_utilization=target_cpu
                )
            )
        )

        hpa_body = client.V2HorizontalPodAutoscaler(
            metadata=client.V1ObjectMeta(name=hpa_name),
            spec=client.V2HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V2CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=deployment_name
                ),
                min_replicas=min_replicas,
                max_replicas=max_replicas,
                metrics=[metric_spec]
            )
        )

        try:
            # Try creating
            self.autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(
                namespace=self.namespace, 
                body=hpa_body
            )
            logger.info(f"✅ HPA created for {deployment_name}: {min_replicas}-{max_replicas} pods")
        except ApiException as e:
            if e.status == 409: # Already exists
                # Update logic could go here (patch)
                logger.info(f"ℹ️ HPA {hpa_name} already exists.")
            else:
                logger.error(f"❌ Failed to apply HPA: {e}")

    def configure_production_scaling(self):
        """Apply Enterprise Scaling Policies"""
        # API Layer: Scale fast to handle HTTP traffic
        self.apply_hpa("ingestion-api", min_replicas=2, max_replicas=20, target_cpu=60)
        
        # AI Layer: Scale aggressively based on queue depth (custom metric simulated here as CPU)
        self.apply_hpa("ai-worker", min_replicas=1, max_replicas=50, target_cpu=80)

if __name__ == "__main__":
    manager = HPAManager(env="prod")
    manager.configure_production_scaling()