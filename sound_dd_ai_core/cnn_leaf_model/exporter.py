import torch
from .model_def import NewCNNLeaf

def export_to_onnx(pth_path, output_path="model.onnx"):
    """
    Converts PyTorch checkpoint to ONNX graph.
    Run this in your CI/CD pipeline before building the Docker image.
    """
    model = NewCNNLeaf()
    if pth_path:
        model.load_state_dict(torch.load(pth_path))
    model.eval()

    # Dummy input for tracing (1 batch, 16000*5 samples)
    dummy_input = torch.randn(1, 80000)

    print(f"Exporting {pth_path} to {output_path}...")
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input_audio'],
        output_names=['logits', 'spectrogram'],
        dynamic_axes={'input_audio': {0: 'batch_size'}} # Allow variable batch size
    )
    print("✅ Export Complete.")

if __name__ == "__main__":
    import sys
    export_to_onnx(sys.argv[1] if len(sys.argv) > 1 else None)