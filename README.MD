## Architecture Overview

The platform follows a **Cloud-Native, Event-Driven Microservices Architecture** split into 6 distinct phases:

1.  **Infrastructure (Foundation):** AWS CDK (IaC) provisioning VPCs, S3, RDS, and EKS.
2.  **Ingestion (The Senses):** High-throughput Async FastAPI handling IoT streams via Presigned URLs.
3.  **AI Core (The Brain):** Kubernetes-orchestrated inference using PyTorch/ONNX and Spot Instance resilience.
4.  **App Layer (The Bridge):** PostGIS-backed Query API with GraphQL, Caching, and Materialized Views.
5.  **Presentation (The Face):** Public 3D Digital Twins (Dash/Mapbox) and Researcher Dashboards (Streamlit).
6.  **Operations (Hardening):** Auto-scaling, Chaos Engineering, and Load Testing.

---

## Project Structure

The repository is structured as a Monorepo with modular domains:

```bash
sound-dd-platform/
├── sound_dd_foundation_infra/   # [Phase 1] AWS CDK Infrastructure as Code
├── sound_dd_ingestion/          # [Phase 2] FastAPI Ingestion & IoT Gateway
├── sound_dd_ai_core/            # [Phase 3] CNNLeaf Model, Docker, & Airflow DAGs
├── sound_dd_app_layer/          # [Phase 4] Read-Optimized API & Geospatial Logic
├── sound_dd_presentation_layer/ # [Phase 5] Public Portal & Admin Dashboard
└── sound_dd_production_ops/     # [Phase 6] Load Testing, HPA, & Observability
```

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- AWS CLI (configured)
- Node.js (for CDK)

### 1. Infrastructure Setup (Phase 1)

Provision the AWS environment (S3, RDS, VPC).

```bash
cd sound_dd_foundation_infra
pip install -r requirements.txt
# Deploy Dev Environment
cdk deploy -c env=dev
```

### 2. Start Ingestion Service (Phase 2)

The entry point for IoT sensors and mobile uploads.

```bash
cd ../sound_dd_ingestion
pip install -r requirements.txt
# Start Async API
uvicorn app.main:app --reload --port 8000
```

### 3. Run the AI Pipeline (Phase 3)

Simulate the AI processing locally using Docker.

```bash
cd ../sound_dd_ai_core
docker build -t sound-dd/ai-core:latest .
# Run inference on a test file
docker run --rm -v $(pwd):/data sound-dd/ai-core:latest ./CNNLeaf.sh /data/test_audio.wav
```

### 4. Launch Visualization (Phase 5)

Start the Public Portal and Admin Dashboard.

```bash
cd ../sound_dd_presentation_layer
pip install -r requirements.txt
./run_all.sh
# Public Portal: http://localhost:8050
# Researcher Dash: http://localhost:8501
```

---

## Key Capabilities & Innovations

### Smart Ingestion

- **Zero-Copy Uploads:** Uses S3 Presigned URLs to bypass API bottlenecks.
- **Integrity Checks:** Enforces MD5 checksums on mobile uploads.
- **Rate Limiting:** tiered QoS for Public vs. Research users.

### AI Core (NewCNNLeaf)

- **Orchestration:** Uses `KubernetesPodOperator` for ephemeral GPU scaling.
- **Cost Optimization:** Handles AWS Spot Instance interruptions gracefully via Checkpointing.
- **Performance:** JIT Compilation and ONNX Runtime for 3x faster inference.

### Geospatial Intelligence

- **Clustering:** Server-side `ST_SnapToGrid` clustering prevents frontend crashes.
- **Analytics:** Materialized Views provide sub-10ms response times for City Impact Reports.
- **Search:** Full-Text Search (GIN Index) for location queries.

---

## Operational Excellence

### Load Testing

To simulate 10,000 concurrent sensors:

```bash
cd sound_dd_production_ops
locust -f load_testing/locustfile.py --host=http://localhost:8000
```

### Disaster Recovery

- **S3 Versioning:** Enabled for Anti-Ransomware protection.
- **Database:** Automated cross-region snapshots.

---

## API Documentation

Once the App Layer (Phase 4) is running, access the interactive docs:

- **REST API (Swagger):** `http://localhost:8000/docs`
- **GraphQL Playground:** `http://localhost:8000/graphql`

**Example GraphQL Query:**

```graphql
query {
  events(region: "T. Nagar", minConfidence: 0.8) {
    timestamp
    classLabel
    audioUrl
  }
}
```

---

## Contributing

1.  **Fork** the repository.
2.  **Create a Branch:** `git checkout -b feature/new-sensor-type`
3.  **Commit:** `git commit -m 'Add support for ESP32 sensors'`
4.  **Test:** Run `pytest` inside the specific module folder.
5.  **Push & PR:** Submit pull request for review.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
