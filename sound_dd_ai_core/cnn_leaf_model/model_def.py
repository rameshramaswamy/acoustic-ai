import torch
import torch.nn as nn
import torchaudio.transforms as T

class NewCNNLeaf(nn.Module):
    """
    Simulated Architecture for NewCNNLeaf.
    """
    def __init__(self, num_classes=2):
        super().__init__()
        # Simulating a Learnable Frontend (LEAF) + CNN Backbone
        self.mel_spectrogram = T.MelSpectrogram(
            sample_rate=16000, n_fft=1024, n_mels=64
        )
        self.conv_block = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(32, num_classes) # 0: Non-Polluting, 1: Polluting
        )

    def forward(self, x):
        # x shape: [batch, samples]
        spec = self.mel_spectrogram(x) # [batch, n_mels, time]
        spec = spec.unsqueeze(1)       # [batch, 1, n_mels, time]
        features = self.conv_block(spec)
        logits = self.classifier(features)
        return logits, spec # Return spectrogram for Feature Store