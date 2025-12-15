import mlflow
import os

class ModelRegistry:
    def __init__(self, tracking_uri="http://localhost:5000"):
        mlflow.set_tracking_uri(tracking_uri)

    def get_production_model_path(self, model_name="NewCNNLeaf"):
        """
        Fetches the artifact URI for the model tagged 'Production'
        """
        try:
            client = mlflow.tracking.MlflowClient()
            # In a real scenario, this queries the Model Registry
            # For this prototype, we mock a return path or use a local default
            # versions = client.get_latest_versions(model_name, stages=["Production"])
            # return versions[0].source
            
            # Fallback for dev
            return "cnn_leaf_model/weights/default.pth"
        except Exception as e:
            print(f"Registry Warning: {e}")
            return None