# generate_ops_scaffold.py
import os

def create_structure():
    root_dir = "sound_dd_production_ops"
    
    structure = {
        "": ["requirements.txt", "README.md", "run_load_test.sh"],
        "autoscaling": ["__init__.py", "hpa_manager.py"],
        "observability": ["__init__.py", "alert_rules.py", "grafana_dashboards.py"],
        "load_testing": ["__init__.py", "locustfile.py", "test_data_generator.py"],
        "disaster_recovery": ["__init__.py", "dr_manager.py", "chaos_simulator.py"],
        "tests": ["__init__.py", "test_ops_tools.py"]
    }

    print(f"🛡️ Generating Scaffolding for {root_dir}...")

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    for folder, files in structure.items():
        path = os.path.join(root_dir, folder)
        os.makedirs(path, exist_ok=True)
        for file in files:
            file_path = os.path.join(path, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    if file == "requirements.txt":
                        f.write("""
kubernetes==28.1.0
boto3==1.34.0
locust==2.20.0
pyyaml
requests
pytest
                        """.strip())
                    elif file == "run_load_test.sh":
                        f.write("#!/bin/bash\nlocust -f load_testing/locustfile.py --host=http://localhost:8000")
                        os.chmod(file_path, 0o755)
                print(f"  ✅ Created: {file_path}")

    print("\n🚀 Scaffolding Complete. Run 'pip install -r requirements.txt'")

if __name__ == "__main__":
    create_structure()