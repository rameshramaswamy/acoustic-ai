from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s
import json

# Enterprise Resources Definition
compute_resources = k8s.V1ResourceRequirements(
    limits={"memory": "4Gi", "cpu": "2000m", "nvidia.com/gpu": "1"},
    requests={"memory": "2Gi", "cpu": "1000m"}
)

# Environment Variables for the Pod
env_vars = {
    "AWS_DEFAULT_REGION": "us-east-1",
    "REDIS_HOST": "sound-dd-redis.internal",
    "ENV": "prod"
}


def parse_k8s_batch_result(**context):
    pod_result = context['ti'].xcom_pull(task_ids='cnn_leaf_batch_inference')
    
    # Parse the JSON list output from the container
    try:
        results = json.loads(pod_result)
        print(f"Received {len(results)} inference results")
        
        # In a real scenario, perform Bulk Update to Postgres here
        # db_handler.bulk_update(results)
    except Exception as e:
        print(f"Failed to parse batch results: {e}")

with DAG(
    'sound_dd_batch_pipeline',
    default_args={'owner': 'sound-dd-ops'},
    schedule_interval=None, # Triggered by specific batch events
    tags=['production', 'batch', 'optimized']
) as dag:

    # The Optimized Batch Task
    inference_task = KubernetesPodOperator(
        namespace='sound-dd-compute',
        image='123456789012.dkr.ecr.us-east-1.amazonaws.com/sound-dd/ai-core:v1.2.0',
        cmds=["python3", "-m", "cnn_leaf_model.inference"],
        # Pass arguments: [JSON_LIST_OF_KEYS, BUCKET_NAME]
        arguments=[
            "{{ dag_run.conf['s3_keys'] | tojson }}", 
            "{{ var.value.S3_BUCKET_NAME }}" # Airflow Variable
        ],
        name="cnn-leaf-batch",
        task_id="cnn_leaf_batch_inference",
        resources=compute_resources, # Defined in previous step
        get_logs=True,
        do_xcom_push=True,
        # Increase memory limit for batch buffering
        limits={"memory": "8Gi", "cpu": "4000m", "nvidia.com/gpu": "1"},
    )

    save_result = PythonOperator(
        task_id='sync_batch_to_postgres',
        python_callable=parse_k8s_batch_result,
        provide_context=True
    )

    inference_task >> save_result