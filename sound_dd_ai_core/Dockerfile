# Stage 1: Builder
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime as builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime (Slimmer)
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

# Install System Libs
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages
COPY --from=builder /install /usr/local/lib/python3.10/site-packages

# Copy Code
COPY cnn_leaf_model /app/cnn_leaf_model
COPY core_services /app/core_services
COPY config.py /app/
COPY CNNLeaf.sh /app/

RUN chmod +x CNNLeaf.sh

# Enterprise: Non-root user for security
RUN useradd -m aiuser
USER aiuser

RUN python3 -m cnn_leaf_model.exporter cnn_leaf_model/weights/default.pth model.onnx

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python3 -c "import torch; print(torch.cuda.is_available())" || exit 1

ENTRYPOINT ["./CNNLeaf.sh"]