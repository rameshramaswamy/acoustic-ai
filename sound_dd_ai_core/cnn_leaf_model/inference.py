import sys
import json
import argparse
import structlog
import boto3
import io
import os
import signal
import numpy as np
import onnxruntime as ort
import torchaudio
import torch
from typing import List, Dict, Any

from ..config import settings

# --- Enterprise Logging Setup ---
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

LABELS = {0: "Non-Polluting", 1: "Polluting"}

# --- Optimization 1: Graceful Shutdown for Spot Instances ---
class GracefulKiller:
    """
    Listens for AWS Spot Termination signals (SIGTERM/SIGINT).
    Allows the batch loop to finish the current item and save state before exiting.
    """
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.warn("received_termination_signal", signal=signum)
        self.kill_now = True

# --- Optimization 2: S3 Streaming & Preprocessing ---
class S3Streamer:
    """
    Streams audio bytes directly from S3 into Memory.
    Performs resampling and padding/truncation to prepare for ONNX.
    """
    def __init__(self, bucket: str):
        self.s3_client = boto3.client(
            's3', 
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        self.bucket = bucket
        self.target_sample_rate = 16000
        # 5 seconds * 16000 Hz = 80000 samples
        self.target_length = 80000 

    def load_audio_as_numpy(self, key: str):
        try:
            # 1. Fetch Bytes (No Disk I/O)
            obj = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            file_stream = io.BytesIO(obj['Body'].read())
            
            # 2. Decode Audio
            # using torchaudio because it handles FLAC/WAV headers robustly
            waveform, sample_rate = torchaudio.load(file_stream)
            
            # 3. Validation: Dead Air Check
            rms = torch.sqrt(torch.mean(waveform**2))
            if rms < 0.001:
                return None, "silence_detected"

            # 4. Resample
            if sample_rate != self.target_sample_rate:
                resampler = torchaudio.transforms.Resample(sample_rate, self.target_sample_rate)
                waveform = resampler(waveform)

            # 5. Pad or Truncate to fixed length
            # Shape is [channels, time]. We assume mono [1, time]
            current_len = waveform.shape[1]
            
            if current_len > self.target_length:
                # Truncate
                waveform = waveform[:, :self.target_length]
            elif current_len < self.target_length:
                # Pad with zeros
                pad_amount = self.target_length - current_len
                waveform = torch.nn.functional.pad(waveform, (0, pad_amount))
            
            # 6. Convert to Numpy for ONNX
            # ONNX Model expects [batch, input_len] or [batch, 1, input_len] depending on export
            # We assume the exporter produced [batch, input_len] for this CNN
            return waveform.numpy(), "valid"

        except Exception as e:
            return None, str(e)

# --- Optimization 3: Statistical Drift Detection ---
def calculate_drift_stats(waveform_np: np.ndarray) -> Dict[str, float]:
    """
    Calculates lightweight signal statistics.
    Used in Phase 4 to detect if a city area is becoming 'louder' 
    or if a sensor is broken (static noise).
    """
    return {
        "mean_amplitude": float(np.mean(np.abs(waveform_np))),
        "std_dev": float(np.std(waveform_np)),
        "zero_crossing_rate": float(((waveform_np[:,:-1] * waveform_np[:,1:]) < 0).sum()) / waveform_np.shape[1]
    }

# --- Main Inference Loop (ONNX) ---
def run_onnx_inference(s3_keys: List[str], bucket: str, onnx_model_path: str):
    log = logger.bind(
        engine="onnxruntime", 
        batch_total=len(s3_keys), 
        model=onnx_model_path
    )
    log.info("inference_batch_started")

    # 1. Initialize ONNX Runtime
    # Prioritize CUDA (GPU), fall back to CPU
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
    try:
        session = ort.InferenceSession(onnx_model_path, providers=providers)
    except Exception as e:
        log.error("onnx_session_init_failed", error=str(e))
        print(json.dumps({"status": "fatal_error", "message": "Model load failed"}))
        sys.exit(1)

    input_name = session.get_inputs()[0].name
    
    # Utilities
    streamer = S3Streamer(bucket)
    killer = GracefulKiller()
    
    results = []
    processed_count = 0

    # 2. Iterate through Micro-Batch
    for key in s3_keys:
        
        # Spot Instance Check
        if killer.kill_now:
            log.warn("spot_interruption_received", processed=processed_count, remaining=len(s3_keys)-processed_count)
            # Add a specific status so Airflow knows to retry the remaining keys later
            results.append({"status": "interrupted", "last_processed_key": key})
            break

        # Load Data
        waveform_np, status = streamer.load_audio_as_numpy(key)
        
        if status != "valid":
            log.warn("invalid_audio_skipped", file=key, reason=status)
            results.append({"file": key, "status": "error", "message": status})
            continue

        try:
            # 3. Run Inference
            # Ensure input shape matches ONNX expectation (Batch Dimension)
            # Waveform is [1, 80000], we might need [1, 1, 80000] or just [1, 80000]
            # Adjusting to standard CNN input: [Batch, Channels, Time] -> [1, 1, 80000]
            if waveform_np.ndim == 2:
                 inp = waveform_np[np.newaxis, ...] # Add batch dim -> [1, 1, 80000]
            else:
                 inp = waveform_np # Already correct?

            # ONNX Execution
            outputs = session.run(None, {input_name: inp})
            logits = outputs[0] # Assuming first output is logits
            
            # Post-processing (Softmax)
            # Improve numerical stability
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / exp_logits.sum()
            
            class_id = int(np.argmax(probs))
            confidence = float(probs[0][class_id])
            
            # 4. Drift Analysis
            drift_stats = calculate_drift_stats(waveform_np)

            # 5. Thresholding (Business Logic)
            final_label = LABELS.get(class_id, "Unknown")
            if confidence < settings.CONFIDENCE_THRESHOLD:
                final_label = "Uncertain"

            results.append({
                "file": key,
                "class_id": class_id,
                "class_label": final_label,
                "confidence": round(confidence, 4),
                "status": "success",
                "stats": drift_stats
            })
            
            processed_count += 1

        except Exception as e:
            log.error("inference_failed_single_file", file=key, error=str(e))
            results.append({"file": key, "status": "error", "message": str(e)})

    # Final Output for Airflow XCom
    log.info("batch_processing_complete", success_count=processed_count)
    print(json.dumps(results))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SoundDD Enterprise Inference (ONNX)")
    parser.add_argument("s3_keys_json", help="JSON list of S3 keys to process")
    parser.add_argument("bucket", help="S3 Bucket Name")
    parser.add_argument("--model", help="Path to .onnx model", default="model.onnx")
    
    args = parser.parse_args()
    
    try:
        keys_list = json.loads(args.s3_keys_json)
        run_onnx_inference(keys_list, args.bucket, args.model)
    except json.JSONDecodeError:
        logger.error("invalid_json_input")
        sys.exit(1)